from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ads_directory.blueprints.schema import CreateListingSchema, ListingSchema
from ads_directory.dao.base_dao import BaseDao
from ads_directory.database.connection import async_session
from ads_directory.models.models import Category, CustomFields, Listing, ListingCustomFields


class ListingDao(BaseDao):
    @staticmethod
    async def get_paginated_listing(page: int = 1, per_page: int = 20) -> list[Listing]:
        async with async_session.begin() as session:
            l = select(Listing).options(joinedload(Listing.category)).limit(per_page).offset((page - 1) * per_page)
            result = await session.execute(l)
            return result.scalars().unique().all()

    @staticmethod
    async def create_listing(data: CreateListingSchema):
        async with async_session.begin() as session:
            listing = Listing(
                name=data.name,
                description=data.description,
                price=data.price,
            )

            category = (
                (
                    await session.execute(
                        select(Category)
                        .options(joinedload(Category.custom_fields))
                        .where(Category.id == data.category_id)
                    )
                )
                .unique()
                .scalar_one_or_none()
            )

            if category is None:
                return {"error": "Category not found"}, 404

            listing.category = category

            # get the category custom fields
            # validate the custom fields
            # ToDo add required field to custom fields and valiate

            if data.custom_fields:
                for c in data.custom_fields:
                    # add the value in relation table listing_custom_fields
                    lcf = ListingCustomFields(listing_id=listing.id, custom_field_id=c.id, value=c.value)
                    listing.custom_fields_association.append(lcf)
            session.add(listing)
            await session.commit()
            return listing

    @classmethod
    async def update_listing(cls, listing_id, data: CreateListingSchema):
        async with async_session() as session:
            listing = (
                (
                    await session.execute(
                        select(Listing)
                        .options(
                            joinedload(Listing.category),
                            joinedload(Listing.custom_fields_association),
                            joinedload(Listing.custom_fields),
                        )
                        .where(Listing.id == listing_id)
                    )
                )
                .unique()
                .scalar_one_or_none()
            )

            if listing is None:
                raise Exception("Listing not found")

            listing.name = data.name
            listing.description = data.description
            listing.price = data.price

            category = (
                (
                    await session.execute(
                        select(Category)
                        .options(joinedload(Category.custom_fields))
                        .where(Category.id == data.category_id)
                    )
                )
                .unique()
                .scalar_one_or_none()
            )

            if category is None:
                raise Exception("Category not found")

            listing.category = category

            # get the category custom fields
            # validate the custom fields
            # ToDo add required field to custom fields and valiate

            # delete the existing custom fields
            # Clear current custom fields association
            listing.custom_fields.clear()
            await session.commit()

            if data.custom_fields:
                for c in data.custom_fields:
                    # add the value in relation table listing_custom_fields
                    lcf = ListingCustomFields(listing_id=listing.id, custom_field_id=c.id, value=c.value)
                    listing.custom_fields_association.append(lcf)

            await session.commit()
            return listing

    @classmethod
    def delete_listing(cls, listing_id) -> bool:
        async with async_session() as session:
            listing = (
                (
                    await session.execute(
                        select(Listing)
                        .where(Listing.id == listing_id)
                    )
                )
                .unique()
                .scalar_one_or_none()
            )

            if listing is None:
                raise Exception("Listing not found")

            session.delete(listing)
            await session.commit()
            return True
