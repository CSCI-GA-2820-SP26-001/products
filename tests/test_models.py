######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Product Model
"""

# pylint: disable=duplicate-code
import os
import logging
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Product, DataValidationError, db
from .factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should create a Product and store it in the database"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)
        found = Product.all()
        self.assertEqual(len(found), 1)
        data = Product.find(product.id)
        self.assertEqual(data.name, product.name)
        self.assertEqual(data.description, product.description)
        self.assertEqual(data.price, product.price)
        self.assertEqual(data.category, product.category)
        self.assertEqual(data.available, product.available)

    def test_read_a_product(self):
        """It should retrieve a Product by its id with all fields correct"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)

        found = Product.find(product.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.description, product.description)
        self.assertEqual(found.price, product.price)
        self.assertEqual(found.category, product.category)
        self.assertEqual(found.available, product.available)

    def test_product_default_available_is_true(self):
        """It should default available to True when not specified"""
        product = Product(
            name="Test Product",
            description="A test product",
            price=Decimal("9.99"),
            category="test",
        )
        product.create()
        found = Product.find(product.id)
        self.assertTrue(found.available)

    def test_repr_of_product(self):
        """It should return a string representation of the Product"""
        product = ProductFactory()
        product.create()
        self.assertIn("Product", repr(product))
        self.assertIn(product.name, repr(product))

    def test_update_a_product(self):
        """It should update a Product in the database"""
        product = ProductFactory()
        product.create()
        original_id = product.id
        product.name = "Updated Name"
        product.update()

        found = Product.find(original_id)
        self.assertEqual(found.name, "Updated Name")
        self.assertEqual(found.id, original_id)

    def test_delete_a_product(self):
        """It should delete a Product from the database"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_find_by_name(self):
        """It should return Products matching the given name"""
        products = ProductFactory.create_batch(3)
        for p in products:
            p.create()
        target_name = products[0].name
        found = Product.find_by_name(target_name).all()
        self.assertGreaterEqual(len(found), 1)
        for p in found:
            self.assertEqual(p.name, target_name)

    def test_serialize_a_product(self):
        """It should serialize a Product into a dictionary"""
        product = ProductFactory()
        data = product.serialize()
        self.assertIsNotNone(data)
        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("description", data)
        self.assertIn("price", data)
        self.assertIn("category", data)
        self.assertIn("available", data)

    def test_deserialize_a_product(self):
        """It should deserialize a Product from a dictionary"""
        data = {
            "name": "Widget",
            "description": "A useful widget",
            "price": "19.99",
            "category": "gadgets",
            "available": True,
        }
        product = Product()
        product.deserialize(data)
        self.assertEqual(product.name, "Widget")
        self.assertEqual(product.description, "A useful widget")
        self.assertEqual(product.price, Decimal("19.99"))
        self.assertEqual(product.category, "gadgets")
        self.assertTrue(product.available)

    def test_deserialize_missing_name_raises_error(self):
        """It should raise DataValidationError when name is missing"""
        data = {
            "description": "No name here",
            "price": "5.00",
            "category": "misc",
            "available": True,
        }
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data_raises_error(self):
        """It should raise DataValidationError when data is not a dict"""
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, "bad data")

    def test_deserialize_attribute_error_raises_data_validation_error(self):
        """It should raise DataValidationError when data causes AttributeError"""

        class NoGetDict:
            """A dict-like object without .get() method"""

            def __getitem__(self, key):
                if key == "name":
                    return "Test"
                raise KeyError(key)

        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, NoGetDict())

    def test_create_raises_data_validation_error(self):
        """It should raise DataValidationError if a database error occurs during create"""
        product = ProductFactory()
        with patch.object(db.session, "add", side_effect=Exception("DB error")):
            self.assertRaises(DataValidationError, product.create)

    def test_update_raises_data_validation_error(self):
        """It should raise DataValidationError if a database error occurs during update"""
        product = ProductFactory()
        product.create()
        product.name = "New Name"
        with patch.object(db.session, "commit", side_effect=Exception("DB error")):
            self.assertRaises(DataValidationError, product.update)

    def test_delete_raises_data_validation_error(self):
        """It should raise DataValidationError if a database error occurs during delete"""
        product = ProductFactory()
        product.create()
        with patch.object(db.session, "delete", side_effect=Exception("DB error")):
            self.assertRaises(DataValidationError, product.delete)
