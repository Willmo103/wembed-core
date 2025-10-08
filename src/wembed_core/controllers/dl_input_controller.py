"""
wembed_core/controllers/dl_input_controller.py
"""

from typing import List, Optional

from wembed_core.database import DatabaseService
from wembed_core.models.dl_doc.dl_inputs import DLInputs
from wembed_core.schemas.dl_doc_schemas import DLInputSchema


class DLInputController:
    """Controller for CRUD operations on DLInputs."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create(self, input_data: DLInputSchema) -> DLInputs:
        """Creates a new input record."""
        with self.db_service.get_db() as session:
            db_record = DLInputs(**input_data.model_dump())
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
        return db_record

    def get_by_id(self, input_id: int) -> Optional[DLInputs]:
        """Retrieves an input record by its ID."""
        with self.db_service.get_db() as session:
            res = session.query(DLInputs).filter(DLInputs.id == input_id).first()
        return res

    def get_by_status(self, status: int) -> List[DLInputs]:
        """Retrieves input records by their status."""
        with self.db_service.get_db() as session:
            res = session.query(DLInputs).filter(DLInputs.status == status).all()
        return res

    def update(self, input_id: int, input_data: DLInputSchema) -> Optional[DLInputs]:
        """Updates an existing input record."""
        with self.db_service.get_db() as session:
            db_record = session.query(DLInputs).filter(DLInputs.id == input_id).first()
            if db_record:
                update_data = input_data.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(db_record, key, value)
                session.commit()
                session.refresh(db_record)
        return db_record
