"""
Models for Product

All of the models are stored in this module
"""

import logging
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Product(db.Model):
    """
    Class that represents a Product
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    description = db.Column(db.String(256))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(63), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    available = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Product to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Product to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Product from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Product into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "category": self.category,
            "stock": self.stock,
            "available": self.available,
        }

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.description = data.get("description", "")
            self.price = Decimal(str(data["price"]))
            self.category = data["category"]
            self.available = data.get("available", True)
            if "stock" in data:
                stock_val = int(data["stock"])
                if stock_val < 0:
                    raise DataValidationError("Invalid Product: stock cannot be negative")
                self.stock = stock_val
                if self.stock <= 0:
                    self.available = False
            else:
                self.stock = int(data.get("stock", 0))
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + str(error)) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data "
                + str(error)
            ) from error
        except ValueError as error:
            raise DataValidationError(
                "Invalid Product: stock must be a valid integer"
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Products in the database"""
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Product by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Products with the given name

        Args:
            name (string): the name of the Products you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_availability(cls, available):
        """Returns all Products with the given availability

        Args:
            available (bool): True for available, False for unavailable
        """
        logger.info("Processing availability query for %s ...", available)
        return cls.query.filter(cls.available == available).all()

    @classmethod
    def find_by_category(cls, category):
        """Returns all Products whose category matches case-insensitively.

        Args:
            category (string): the category to match
        """
        logger.info("Processing category query for %s ...", category)
        return (
            cls.query.filter(func.lower(cls.category) == category.lower()).all()
        )

    @classmethod
    def find_by_price_range(cls, minimum_price=None, maximum_price=None):
        """Returns all products within a price range"""
        query = cls.query

        if minimum_price is not None:
            query = query.filter(cls.price >= minimum_price)

        if maximum_price is not None:
            query = query.filter(cls.price <= maximum_price)

        return query.all()
