from datetime import datetime, timezone
from typing import Generator, List, Optional

from pydantic import BaseModel, computed_field


class ScanResultSchema(BaseModel):
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

        from_attributes = True


class ScanResultList(BaseModel):
    results: List[ScanResultSchema]

    def add_result(self, result: ScanResultSchema) -> None:
        """
        Add a scan result to the list.
        Args:
            result (ScanResultSchema): The scan result to add.

        Returns:
            None
        """
        self.results.append(result)

    def iter_results(self) -> Generator[ScanResultSchema, None, None]:
        """
        Generator to iterate over scan results.

        Returns:
            Generator[ScanResultSchema, None, None]: A generator of scan results.
        """
        for result in self.results:
            yield result
