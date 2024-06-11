from quart import Blueprint
from quart_schema import validate_querystring, validate_request, validate_response

from ads_directory.blueprints.schema import (
    CategorySchema,
    CreateListingSchema,
    CustomFieldSchema,
    ListingRecordSchema,
    ListingSchema,
)
from ads_directory.dao.base_dao import BaseDao
from ads_directory.dao.ListingDao import ListingDao
from ads_directory.models.models import Listing
from ads_directory.routes import PaginatedRequest

bp = Blueprint("listing", __name__)


@bp.get("/")
@validate_querystring(PaginatedRequest)
async def listing(query_args: PaginatedRequest):
    listings = await ListingDao.get_paginated_listing(per_page=query_args.per_page, page=query_args.page)

    return {
        "listings": [
            ListingRecordSchema(
                id=listing.id,
                name=listing.name,
                description=listing.description,
                price=listing.price,
                category=CategorySchema(
                    id=listing.category.id, name=listing.category.name, description=listing.category.description
                ),
                custom_fields=[],
                created_at=listing.created_at,
            )
            for listing in listings
        ]
    }


@bp.get("/<int:listing_id>")
async def get_listing(listing_id: int):
    listing = await BaseDao.get_one(Listing, Listing.id == listing_id)
    if listing is None:
        return {"error": "Listing not found"}, 404

    return ListingRecordSchema(
        id=listing.id,
        name=listing.name,
        description=listing.description,
        price=listing.price,
        category=CategorySchema(
            id=listing.category.id, name=listing.category.name, description=listing.category.description
        ),
        created_at=listing.created_at,
    )


@bp.post("/")
@validate_request(CreateListingSchema)
async def create_listing(data: CreateListingSchema):
    listing = await ListingDao.create_listing(data)

    return ListingRecordSchema(
        id=listing.id,
        name=listing.name,
        description=listing.description,
        price=listing.price,
        category=CategorySchema(
            id=listing.category.id, name=listing.category.name, description=listing.category.description
        ),
        created_at=listing.created_at,
    )


@bp.put("/<int:listing_id>")
@validate_request(CreateListingSchema)
async def update_listing(listing_id: int, data: CreateListingSchema):
    listing = await ListingDao.update_listing(listing_id, data)

    return ListingRecordSchema(
        id=listing.id,
        name=listing.name,
        description=listing.description,
        price=listing.price,
        category=CategorySchema(
            id=listing.category.id, name=listing.category.name, description=listing.category.description
        ),
        created_at=listing.created_at,
    )


@bp.delete("/<int:listing_id>")
async def delete_listing(listing_id: int):
    await ListingDao.delete_listing(listing_id)

    return {"message": "Listing deleted successfully"}
