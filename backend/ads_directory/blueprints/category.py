from pydantic.main import BaseModel
from quart import Blueprint
from quart_schema import validate_querystring, validate_request, validate_response

from ads_directory.blueprints.custom_fields import CustomFieldSchema
from ads_directory.blueprints.schema import CategorySchema, CreateCategorySchema
from ads_directory.dao.base_dao import BaseDao
from ads_directory.dao.category_dao import CategoryDao
from ads_directory.models.models import Category
from ads_directory.routes import CreatedResponse, DeletedResponse, ErrorResponse, PaginatedRequest

bp = Blueprint("categories", __name__)


@bp.get("/")
@validate_querystring(PaginatedRequest)
async def categories(query_args: PaginatedRequest):
    categories: list[Category] = await CategoryDao.get_paginated_categories(
        per_page=query_args.per_page, page=query_args.page
    )

    result = []
    for c in categories:
        # build the custom fields schema
        custom_fields = []
        for custom_field in c.custom_fields:
            custom_fields.append(CustomFieldSchema(id=custom_field.id, name=custom_field.name, type=custom_field.type))
        result.append(CategorySchema(id=c.id, name=c.name, description=c.description, custom_fields=custom_fields))
    return {"categories": result}


@bp.get("/<int:category_id>")
async def category(category_id: int):
    try:
        category: Category = await CategoryDao.get_one(Category, Category.id == category_id)
        if category is None:
            raise Exception("Category not found")
        custom_fields = []
        for custom_field in category.custom_fields:
            custom_fields.append(CustomFieldSchema(id=custom_field.id, name=custom_field.name, type=custom_field.type))
        return {
            "category": CategorySchema(
                id=category.id, name=category.name, description=category.description, custom_fields=custom_fields
            )
        }
    except Exception as e:
        return ErrorResponse(success=False, message=str(e))


@bp.post("/")
@validate_request(CreateCategorySchema)
async def create_category(data: CreateCategorySchema):
    category: Category = await CategoryDao.create_category(data)
    return {"category": CategorySchema(id=category.id, name=category.name, description=category.description)}


@bp.put("/<int:category_id>")
@validate_request(CreateCategorySchema)
@validate_response(CreatedResponse)
async def update_category(category_id: int, data: CreateCategorySchema):
    await CategoryDao.update_category(category_id, data)
    return CreatedResponse(success=True, id=category_id)


@bp.delete("/<int:category_id>")
@validate_response(DeletedResponse)
async def delete_category(category_id: int):
    rowcount: int = await BaseDao.delete(Category, Category.id == category_id)
    return DeletedResponse(success=True, rowcount=rowcount)
