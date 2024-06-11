import typing
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from ads_directory.blueprints.schema import CreateCategorySchema
from ads_directory.dao.base_dao import BaseDao, T
from ads_directory.database.connection import async_session
from ads_directory.models.models import Category, CustomFields


class CategoryDao(BaseDao):
    @staticmethod
    async def get_paginated_categories(page: int = 1, per_page: int = 20) -> list[Category]:
        async with async_session.begin() as session:
            result = await session.execute(
                sa.select(Category)
                .options(joinedload(Category.custom_fields))
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            return result.scalars().unique().all()

    @staticmethod
    async def get_one(model: typing.Type[T], *criteria: typing.Any) -> T:
        async with async_session.begin() as session:
            result = await session.execute(
                sa.select(Category).options(joinedload(Category.custom_fields)).where(*criteria)
            )
            return result.scalars().first()

    @staticmethod
    async def create_category(data: CreateCategorySchema) -> Category:
        # if custom_fields are provided, fetch them from the database and add them to the category
        cs_ids = data.custom_fields
        del data.custom_fields

        async with async_session.begin() as session:
            c = Category(**data.dict())

            if cs_ids:
                # fetch custom fields from the database
                cs = await BaseDao.get_all(CustomFields, CustomFields.id.in_(cs_ids))
                for custom_field in cs:
                    c.custom_fields.append(custom_field)

            session.add(c)
            await session.commit()
            return c

    @staticmethod
    async def update_category(category_id: int, data: CreateCategorySchema) -> Category:
        async with async_session.begin() as session:
            c: Category = await CategoryDao.get_one(Category, Category.id == category_id)
            if c is None:
                raise Exception("Category not found")

            # if custom_fields are provided, fetch them from the database and add them to the category
            cs_ids = data.custom_fields
            del data.custom_fields

            c.update(**data.dict())

            if cs_ids:
                # fetch custom fields from the database
                cs = await BaseDao.get_all(CustomFields, CustomFields.id.in_(cs_ids))
                c.custom_fields.clear()
                for custom_field in cs:
                    c.custom_fields.append(custom_field)
            else:
                c.custom_fields.clear()

            await session.merge(c)
            await session.commit()
            return c
