import asyncio
import logging

from flask_bcrypt import generate_password_hash
from sqlalchemy import select

from ..database.connection import async_session
from ..models.models import Category, CustomFields, User

logger = logging.getLogger(__name__)


async def create_user(session: async_session):
    user = await session.execute(select(User).filter(User.email == "jd@email.com"))
    if user.scalars().first():
        logger.info("User Data already seeded")
        return

    user1 = User(
        name="John", last_name="Dow", email="jd@email.com", password=generate_password_hash("pass").decode("utf-8")
    )
    session.add(user1)


async def create_custom_fields(session: async_session):
    if (await session.execute(select(CustomFields).filter(CustomFields.name == "Car Make"))).scalars().first() is None:
        car_make = CustomFields(
            name="Car Make",
            type="select",
            description="Car make",
            field_config={
                "placeholder": "car make",
                "options": [
                    {"label": "Toyota", "value": "Toyota"},
                    {"label": "Honda", "value": "Honda"},
                    {"label": "BMW", "value": "BMW"},
                    {"label": "Mercedes", "value": "Mercedes"},
                ],
            },
        )

        session.add(car_make)

    if (
        await session.execute(select(CustomFields).filter(CustomFields.name == "Car Fuel Type"))
    ).scalars().first() is None:
        car_fuel_type = CustomFields(
            name="Car Fuel Type",
            type="select",
            description="Car fuel type",
            field_config={
                "placeholder": "car fuel type",
                "options": [
                    {"label": "Petrol", "value": "Petrol"},
                    {"label": "Diesel", "value": "Diesel"},
                    {"label": "Electric", "value": "Electric"},
                ],
            },
        )
        session.add(car_fuel_type)

    # Real Estate
    if (await session.execute(select(CustomFields).filter(CustomFields.name == "Bedrooms"))).scalars().first() is None:
        bedrooms = CustomFields(
            name="Bedrooms",
            type="number",
            description="Number of bedrooms",
            field_config={"placeholder": "Number of bedrooms"},
        )

        session.add(bedrooms)

    if (await session.execute(select(CustomFields).filter(CustomFields.name == "Bathrooms"))).scalars().first() is None:
        bathrooms = CustomFields(
            name="Bathrooms",
            type="number",
            description="Number of bathrooms",
            field_config={"placeholder": "Number of bathrooms"},
        )

        session.add(bathrooms)


async def create_categories(session: async_session):
    if (await session.execute(select(CustomFields).filter(Category.name == "Cars"))).scalars().first() is None:
        cars = Category(name="Cars", description="Cars category")

        custom_fields = await session.execute(
            select(CustomFields).filter(CustomFields.name.in_(["Car Make", "Car Fuel Type"]))
        )

        cars.custom_fields.extend(custom_fields.scalars().all())
        session.add(cars)

    # Real Estate
    if (await session.execute(select(CustomFields).filter(Category.name == "Real Estate"))).scalars().first() is None:
        real_estate = Category(name="Real Estate", description="Real Estate category")

        custom_fields = await session.execute(
            select(CustomFields).filter(CustomFields.name.in_(["Bedrooms", "Bathrooms"]))
        )

        real_estate.custom_fields.extend(custom_fields.scalars().all())
        session.add(real_estate)


async def _seed():
    async with async_session.begin() as session:
        await create_user(session)
        await create_custom_fields(session)
        await create_categories(session)

        await session.commit()


def seed_data():
    result = asyncio.get_event_loop().run_until_complete(_seed())
