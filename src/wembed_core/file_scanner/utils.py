import hashlib
import mimetypes
import os
import traceback
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from anyio import Path

from wembed_core.constants import MD_XREF as md_xref
from wembed_core.schemas.indexing_schemas import (
    IndexedFileLineSchema,
    IndexedFileSchema,
)


def create_file_record_from_path(
    file_path: Path,
    source_type: str,
    source_name: str,
    source_root: str,
    relative_path: str,
) -> Optional[IndexedFileSchema]:
    """Create a IndexedFileSchema from a file path."""
    if not file_path.is_file() or not file_path.exists():
        return None

    try:
        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()

        # Try to decode as text
        try:
            content_text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content_text = content.decode("latin-1", errors="replace")
            except Exception:
                content_text = "<Binary or non-text content>"

        # Calculate hashes
        sha256 = hashlib.sha256(content).hexdigest()
        md5 = hashlib.md5(content).hexdigest()

        # Get file stats
        stat = file_path.stat()

        # Count lines if it's a text file
        line_count = (
            len(content_text.splitlines())
            if content_text != "<Binary or non-text content>"
            else 0
        )

        file_record = IndexedFileSchema(
            id=uuid4().hex,
            version=1,
            source_type=source_type,
            source_root=source_root,
            source_name=source_name,
            host=os.environ.get("COMPUTERNAME", "unknown"),
            user=os.environ.get("USERNAME", "unknown"),
            name=file_path.name,
            stem=file_path.stem,
            path=str(file_path),
            relative_path=relative_path,
            suffix=file_path.suffix,
            sha256=sha256,
            md5=md5,
            mode=stat.st_mode,
            size=stat.st_size,
            content=(
                content if len(content) < 1024 * 1024 else None
            ),  # Don't store large files in DB
            content_text=content_text,
            ctime_iso=datetime.fromtimestamp(stat.st_birthtime, tz=timezone.utc),
            mtime_iso=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            created_at=datetime.now(timezone.utc),
            line_count=line_count,
            uri=f"file://{file_path.as_posix()}",
            mimetype=mimetypes.guess_type(file_path.name)[0]
            or "application/octet-stream",  # noqa: W503
            markdown=None,  # Will be generated separately
        )

        return file_record

    except Exception as e:
        print(
            f"\nError creating file record for {file_path}: {e}, {traceback.format_exc()}\n",
        )
        return None


def get_filelines_list_from_file_record(
    file_record: IndexedFileSchema,
) -> list[IndexedFileLineSchema]:
    """
    Genetates a list of IndexedFileLineSchema objects from a IndexedFileSchema.
    returns [] if file_record.content_text is None or empty.
    """
    if not file_record.content_text:
        return []

    lines = file_record.content_text.splitlines()
    filelines = []
    for idx, line in enumerate(lines, start=1):
        fileline = IndexedFileLineSchema(
            id=uuid4().hex,
            file_id=file_record.id,
            line_number=idx,
            content=line,
            created_at=datetime.now(timezone.utc),
        )
        filelines.append(fileline)

    return filelines


def format_file_record_markdown(file_record: IndexedFileSchema) -> str:
    """Generate markdown content for a file record."""
    return f"""---
id: {file_record.id}
host: {file_record.host}
user: {file_record.user}
sha256: {file_record.sha256}
uri: {file_record.uri}
source_type: {file_record.source_type}
source_name: {file_record.source_name}
version: {file_record.version}
file_path: {file_record.path}
relative_path: {file_record.relative_path}
file_name: {file_record.name}
file_stem: {file_record.stem}
file_suffix: {file_record.suffix}
file_size: {file_record.size}
line_count: {file_record.line_count}
mimetype: {file_record.mimetype}
created_at: {file_record.ctime_iso.isoformat() if hasattr(file_record.ctime_iso, 'isoformat') else file_record.ctime_iso}
modified_at: {file_record.mtime_iso.isoformat() if hasattr(file_record.mtime_iso, 'isoformat') else file_record.mtime_iso}
indexed_at: {file_record.created_at.isoformat() if hasattr(file_record.created_at, 'isoformat') else file_record.created_at}
generated_at: {datetime.now(timezone.utc).isoformat()}
---

# {file_record.name} *(Version {file_record.version})*

## File Content

```{md_xref.get(file_record.suffix, "")}
{file_record.content_text or "<Binary or non-text content>"}
```
"""
