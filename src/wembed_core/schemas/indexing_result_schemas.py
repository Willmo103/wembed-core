from datetime import datetime, timezone
from typing import Generator, List, Optional

from pydantic import BaseModel, computed_field


class IndexingResultSchema(BaseModel):
    id: str
    root_path: str
    scan_name: str
    scan_type: str
    files: Optional[List[str]] = None
    scan_start: datetime = datetime.now(tz=timezone.utc)
    scan_end: Optional[datetime] = None
    duration: Optional[float] = None
    options: Optional[dict] = None
    user: str
    host: str

    @computed_field
    def total_files(self) -> int:
        """Compute the total number of files in the scan result."""
        return len(self.files) if self.files else 0

    class Config:
        """Pydantic configuration to allow ORM mode."""

        exclude = {"total_files"}
        from_attributes = True


class IndexingResultsListSchema(BaseModel):
    results: List[IndexingResultSchema]

    def add_result(self, result: IndexingResultSchema) -> None:
        """
        Add a scan result to the list.
        Args:
            result (IndexingResultSchema): The scan result to add.

        Returns:
            None
        """
        self.results.append(result)

    def iter_results(self) -> Generator[IndexingResultSchema, None, None]:
        """
        Generator to iterate over scan results.

        Returns:
            Generator[IndexingResultSchema, None, None]: A generator of scan results.
        """
        for result in self.results:
            yield result
