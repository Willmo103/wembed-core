from datetime import datetime, timezone
from typing import Optional

from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.types.doc.document import DoclingDocument
from pydantic import BaseModel

from wembed_core.config import AppConfig
from wembed_core.constants import HEADERS
from wembed_core.controllers import (
    DLChunkController,
    DLDocumentController,
    DLInputController,
)
from wembed_core.database import DatabaseService
from wembed_core.embedding import EmbeddingModelConfig, EmbeddingService
from wembed_core.models.dl_doc import DLChunks, DLDocuments
from wembed_core.ollama_client import OllamaClient
from wembed_core.schemas import DLChunkSchema, DLDocumentSchema


class ConversionRetult(BaseModel):
    document: DoclingDocument
    doc_record: DLDocuments
    chunk_records: list[DLChunks]


class DLConverterService:
    def __init__(
        self,
        app_config: AppConfig,
        embedding_model_config: Optional[EmbeddingModelConfig] = EmbeddingModelConfig(),
    ):
        self._temp_dir = app_config.app_data / "dl_temp"
        if not self._temp_dir.exists():
            self._temp_dir.mkdir(parents=True, exist_ok=True)
        self._db_service = DatabaseService(app_config)
        self._ollama_client = OllamaClient(app_config)
        self._embedding_model_config = embedding_model_config
        self._embedding_service = EmbeddingService(
            app_config, embedding_model_config or EmbeddingModelConfig()
        )
        self._document_converter = DocumentConverter()
        self._chunker = HybridChunker(
            tokenizer=HuggingFaceTokenizer.from_pretrained(
                model_name=self._embedding_model_config.hf_model_id,
                max_length=self._embedding_model_config.max_tokens,
            ),
            max_tokens=self._embedding_model_config.max_tokens,
            merge_peers=True,
        )
        self._dl_documents_controller = DLDocumentController(self._db_service)
        self._dl_chunks_controller = DLChunkController(self._db_service)
        self._dl_input_controller = DLInputController(self._db_service)

    def convert_source_to_dl_doc(
        self,
        source: str,
        headers: Optional[dict[str, str]] = None,
        source_type: Optional[str] = None,
        source_ref: Optional[str] = None,
    ) -> Optional[ConversionRetult]:
        """Converts a document from a source URL/path to DLDocument and stores it in the DB."""
        headers = headers or HEADERS
        if "://" not in source:
            doc = self._document_converter.convert(source=source).document
            if not source_type:
                source_type = "file"
        else:
            doc = self._document_converter.convert(
                source=source, headers=headers
            ).document
            if not source_type:
                source_type = "url"

        doc_schema = DLDocumentSchema(
            source=source,
            source_type=source_type,
            source_ref=source_ref,
            dl_doc=doc.model_dump_json(),
            markdown=doc.export_to_markdown(),
            html=doc.export_to_html(),
            text=doc.export_to_text(),
            doctags=doc.export_to_doctags(),
            chunks_json=None,
            created_at=datetime.now(timezone.utc),
        )
        doc_record: DLDocuments
        doc_id: int
        chunk_records: list[DLChunks] = []
        errors: list[Exception] = []

        try:
            doc_record = self._dl_documents_controller.create(doc_schema)
            doc_id = doc_record.id
        except Exception as e:
            print(f"Error creating DLDocument record for {source}: {e}")
            return None

        try:
            chunks = self._chunker.chunk(doc)
            total_chunks = len(list(chunks))
            print(f"Processing {total_chunks} chunks...")

            # Re-chunk since chunks iterator is consumed
            chunks = self._chunker.chunk(doc)

            for i, chunk in enumerate(chunks):
                try:
                    print(f"Processing chunk {i + 1}/{total_chunks}", nl=False)
                    print("\r", nl=False)  # Carriage return for overwrite

                    # Contextualize chunk
                    c_txt = self._chunker.contextualize(chunk)
                    chunk.text = c_txt

                    # Add to chunks_json
                    chunk_records.append(chunk.model_dump_json())

                    # Generate embedding
                    embedding = self._embedding_service.get_embedding(c_txt)

                    # Create chunk record
                    chunk_record = DLChunkSchema(
                        document_id=doc_id,
                        chunk_index=i,
                        chunk_text=c_txt,
                        embedding=embedding,
                        created_at=datetime.now(timezone.utc),
                    )

                    # Save chunk record
                    chunk_db_record = self._dl_chunks_controller.create(chunk_record)
                    chunk_records.append(chunk_db_record)

                except Exception as e:
                    error_msg = f"Error processing chunk {i}: {str(e)}"
                    errors.append(error_msg)
                    print(
                        f"\nError on chunk {i}: {e}",
                    )

            chunks_data = str([chunk.model_dump_json() for chunk in chunks])
            # Update document with chunks_json
            self._dl_documents_controller.update(
                doc_id,
                DLDocumentSchema(
                    chunks_json=chunks_data,
                ),
            )
            print(f"\nProcessed {total_chunks - len(errors)} chunks successfully")
            if errors:
                print(
                    f"Encountered {len(errors)} errors during chunk processing",
                )

        except Exception as e:
            error_msg = f"Error during chunking: {str(e)}"
            errors.append(error_msg)
            print(f"Chunking failed: {e}")
