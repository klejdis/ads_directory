from typing import Any

from pydantic.main import BaseModel
from quart import Blueprint
from quart_schema import validate_querystring, validate_request, validate_response

from ads_directory.blueprints.schema import CreateCustomFieldSchema, CustomFieldSchema
from ads_directory.dao.base_dao import BaseDao
from ads_directory.models.models import CustomFields
from ads_directory.routes import PaginatedRequest

bp = Blueprint("custom_fields", __name__)


@bp.get("/")
@validate_querystring(PaginatedRequest)
async def custom_fields(query_args: PaginatedRequest):
    custom_fields: list[CustomFields] = await BaseDao.get_paginated(
        CustomFields, per_page=query_args.per_page, page=query_args.page
    )
    return {
        "custom_fields": [
            CustomFieldSchema(id=c.id, name=c.name, type=c.type, description=c.description, field_config=c.field_config)
            for c in custom_fields
            if c is not None
        ]
    }


@bp.get("/<int:custom_field_id>")
async def custom_field(custom_field_id: int):
    custom_field: CustomFields = await BaseDao.get_one(CustomFields, CustomFields.id == custom_field_id)
    return {
        "custom_field": CustomFieldSchema(
            id=custom_field.id,
            name=custom_field.name,
            type=custom_field.type,
            description=custom_field.description,
            field_config=custom_field.field_config,
        )
    }


@bp.post("/")
@validate_request(CreateCustomFieldSchema)
async def create_custom_field(data: CreateCustomFieldSchema):
    custom_field: CustomFields = await BaseDao.create(CustomFields, **data.dict())
    return {
        "custom_field": CustomFieldSchema(
            id=custom_field.id,
            name=custom_field.name,
            type=custom_field.type,
            description=custom_field.description,
            field_config=custom_field.field_config,
        )
    }


@bp.put("/<int:custom_field_id>")
@validate_request(CreateCustomFieldSchema)
async def update_custom_field(custom_field_id: int, data: CreateCustomFieldSchema):
    await BaseDao.update(CustomFields, CustomFields.id == custom_field_id, **data.dict())
    return {
        "custom_field": CustomFieldSchema(
            id=custom_field_id,
            name=data.name,
            type=data.type,
            description=data.description,
            field_config=data.field_config,
        )
    }


@bp.delete("/<int:custom_field_id>")
async def delete_custom_field(custom_field_id: int):
    await BaseDao.delete(CustomFields, CustomFields.id == custom_field_id)
    return {"success": True}
