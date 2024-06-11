from datetime import datetime
from typing import Any

from pydantic.main import BaseModel


class CreateCategorySchema(BaseModel):
    name: str
    description: str | None
    custom_fields: list[int] | None


class ConfigSchema(BaseModel):
    class ConfigOptions(BaseModel):
        label: str
        value: str

    placeholder: str | None
    options: list[ConfigOptions] | None


class CustomFieldSchema(BaseModel):
    id: int
    name: str
    type: str
    description: str | None
    field_config: ConfigSchema | None


class CreateCustomFieldSchema(BaseModel):
    name: str
    type: str
    description: str | None
    field_config: ConfigSchema | None


class CategorySchema(BaseModel):
    id: int
    name: str
    description: str | None
    custom_fields: list[CustomFieldSchema] | None


class ListingSchema(BaseModel):
    name: str
    description: str | None
    price: float


class ListingCustomFieldSchema(BaseModel):
    listing_id: int
    custom_field_id: int
    value: str


class ListingRecordSchema(ListingSchema):
    id: int
    custom_fields: list[ListingCustomFieldSchema] | None
    category: CategorySchema
    created_at: datetime
    updated_at: datetime | None


class CreateListingSchema(ListingSchema):
    class CustomFieldItem(BaseModel):
        id: int
        value: str

    custom_fields: list[CustomFieldItem] | None
    category_id: int
