from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Generic, TypeVar, List, Optional

from app.utils.database import get_db
from app.schemas.base import BaseSchema, BaseResponseSchema
from app.services.base import BaseService

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseResponseSchema)


class BaseRouter(Generic[CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    def __init__(
        self,
        service: BaseService,
        create_schema: type[CreateSchemaType],
        update_schema: type[UpdateSchemaType],
        response_schema: type[ResponseSchemaType],
        prefix: str
    ):
        self.service = service
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.response_schema = response_schema
        self.router = APIRouter(prefix=prefix)
        self.setup_routes()

    def setup_routes(self):
        @self.router.get("/{id}", response_model=self.response_schema)
        def get_by_id(id: int, db: Session = Depends(get_db)):
            item = self.service.get(db, id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found"
                )
            return item

        @self.router.get("/", response_model=List[self.response_schema])
        def get_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
            return self.service.get_all(db, skip, limit)

        @self.router.post("/", response_model=self.response_schema, status_code=status.HTTP_201_CREATED)
        def create(item: self.create_schema, db: Session = Depends(get_db)):
            return self.service.create(db, item)

        @self.router.put("/{id}", response_model=self.response_schema)
        def update(id: int, item: self.update_schema, db: Session = Depends(get_db)):
            updated_item = self.service.update(db, id, item)
            if not updated_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found"
                )
            return updated_item

        @self.router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
        def delete(id: int, db: Session = Depends(get_db)):
            if not self.service.delete(db, id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found"
                )
            return None
