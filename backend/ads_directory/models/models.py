from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, ForeignKeyConstraint, Integer, String, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    __abstract__ = True

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def __declare_last__(cls) -> None:
        @event.listens_for(cls, "before_insert")
        def set_created_at(mapper, connection, target):
            target.created_at = datetime.utcnow()
            target.updated_at = datetime.utcnow()

        @event.listens_for(cls, "before_update")
        def set_updated_at(mapper, connection, target) -> None:
            target.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)

    custom_fields: Mapped[list["CustomFields"]] = relationship(
        "CustomFields", secondary="category_custom_fields", back_populates="categories"
    )


class CustomFields(Base):
    __tablename__ = "custom_fields"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    field_config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    description: Mapped[str] = mapped_column(String(200), nullable=False)

    categories: Mapped[list[Category]] = relationship(
        "Category", secondary="category_custom_fields", back_populates="custom_fields"
    )

    listings_association: Mapped[list["ListingCustomFields"]] = relationship(
        "ListingCustomFields", back_populates="custom_field"
    )
    listing: Mapped[list["Listing"]] = relationship(
        "Listing", secondary="listing_custom_fields", back_populates="custom_fields"
    )


class CategoryCustomFields(Base):
    __tablename__ = "category_custom_fields"

    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), primary_key=True)
    custom_field_id: Mapped[int] = mapped_column(Integer, ForeignKey("custom_fields.id"), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(["category_id"], ["categories.id"]),
        ForeignKeyConstraint(["custom_field_id"], ["custom_fields.id"]),
    )


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))

    category: Mapped[Category] = relationship("Category", lazy="joined")

    custom_fields: Mapped[CustomFields] = relationship(
        CustomFields, secondary="listing_custom_fields", back_populates="listing"
    )
    custom_fields_association: Mapped[list["ListingCustomFields"]] = relationship(
        "ListingCustomFields", back_populates="listing"
    )

    __table_args__ = (ForeignKeyConstraint(["category_id"], ["categories.id"]),)


class ListingCustomFields(Base):
    __tablename__ = "listing_custom_fields"

    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), primary_key=True)
    custom_field_id: Mapped[int] = mapped_column(ForeignKey("custom_fields.id"), primary_key=True)
    value: Mapped[str] = mapped_column(String(200), nullable=False)

    listing: Mapped[Listing] = relationship("Listing", back_populates="custom_fields_association")

    custom_field: Mapped[CustomFields] = relationship("CustomFields", back_populates="listings_association")

    __table_args__ = (
        ForeignKeyConstraint(["listing_id"], ["listings.id"]),
        ForeignKeyConstraint(["custom_field_id"], ["custom_fields.id"]),
    )
