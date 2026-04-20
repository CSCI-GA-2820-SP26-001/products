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
TestProduct API Service Test Suite
"""

# pylint: disable=duplicate-code
from decimal import Decimal
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from werkzeug.exceptions import InternalServerError
from wsgi import app
from service.common import status
from service.models import db, Product
from .factories import ProductFactory

DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///test.db")


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()
        db.drop_all()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content_type, "application/json")
        data = response.get_json()
        self.assertIn("name", data)
        self.assertIn("version", data)
        self.assertIn("paths", data)
        self.assertEqual(data["name"], "Product Catalog Service")
        self.assertEqual(data["version"], "1.0")
        self.assertIsInstance(data["paths"], list)

    def test_admin_update_product_page(self):
        """It should render the admin update product UI page"""
        response = self.client.get("/admin/products/update")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/html", response.content_type)
        page = response.get_data(as_text=True)
        self.assertIn("Update Product", page)
        self.assertIn("Retrieve Product", page)

    def test_admin_create_product_page(self):
        """It should render the admin create product UI page"""
        response = self.client.get("/admin/products/create")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/html", response.content_type)
        page = response.get_data(as_text=True)
        self.assertIn("Create Product", page)
        self.assertIn("Product Details", page)

    def test_admin_delete_product_page(self):
        """It should render the admin delete product UI page"""
        response = self.client.get("/admin/products/delete")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/html", response.content_type)
        page = response.get_data(as_text=True)
        self.assertIn("Delete Product", page)

    def test_admin_read_product_page(self):
        """It should render the admin read product UI page"""
        response = self.client.get("/admin/products/read")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/html", response.content_type)
        page = response.get_data(as_text=True)
        self.assertIn("Read Product", page)
        self.assertIn("Retrieve Product", page)

    def test_admin_list_product_page(self):
        """It should render the admin list product UI page"""
        response = self.client.get("/admin/products/list")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/html", response.content_type)
        page = response.get_data(as_text=True)
        self.assertIn("List Products", page)
        self.assertIn("List All", page)

    def test_404_not_found(self):
        """It should return 404 JSON for an unknown route"""
        resp = self.client.get("/nonexistent-route")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.content_type, "application/json")
        data = resp.get_json()
        self.assertIn("error", data)
        self.assertIn("message", data)
        self.assertEqual(data["status"], status.HTTP_404_NOT_FOUND)

    def test_405_method_not_allowed(self):
        """It should return 405 JSON when using a disallowed HTTP method"""
        resp = self.client.post("/")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(resp.content_type, "application/json")
        data = resp.get_json()
        self.assertIn("error", data)
        self.assertIn("message", data)
        self.assertEqual(data["status"], status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_products_bad_request_returns_json(self):
        """It should return 400 JSON from the REST API for invalid create body"""
        resp = self.client.post(
            "/products",
            json={"description": "no name", "price": "1.00", "category": "x"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.content_type, "application/json")
        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["error"], "Bad Request")
        self.assertIn("message", data)
        self.assertEqual(data["status"], status.HTTP_400_BAD_REQUEST)

    def test_post_products_unsupported_media_type_returns_json(self):
        """It should return 415 JSON from the REST API for non-JSON create"""
        resp = self.client.post(
            "/products",
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(resp.content_type, "application/json")
        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["error"], "Unsupported media type")
        self.assertIn("message", data)
        self.assertEqual(data["status"], status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_products_internal_server_error_returns_json(self):
        """It should return 500 JSON when listing products hits an unexpected error"""
        with patch(
            "service.routes.Product.all",
            side_effect=InternalServerError(description="server error"),
        ):
            resp = self.client.get("/products")
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(resp.content_type, "application/json")
        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["error"], "Internal Server Error")
        self.assertEqual(data["status"], status.HTTP_500_INTERNAL_SERVER_ERROR)

    ######################################################################
    #  P R O D U C T   R O U T E   T E S T   C A S E S
    ######################################################################

    def test_create_product_success(self):
        """It should create a Product and return 201"""
        product = ProductFactory()
        payload = product.serialize()
        payload.pop("id", None)  # id is generated by the database

        resp = self.client.post("/products", json=payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertIsNotNone(data.get("id"))
        self.assertEqual(data["name"], payload["name"])
        self.assertEqual(data["description"], payload["description"])
        self.assertEqual(data["price"], payload["price"])
        self.assertEqual(data["category"], payload["category"])
        self.assertEqual(data["available"], payload["available"])
        self.assertEqual(data["stock"], payload["stock"])

    def test_create_product_missing_required_field(self):
        """It should return 400 for missing required fields"""
        payload = {
            "description": "missing name",
            "price": "9.99",
            "category": "test",
        }

        resp = self.client.post("/products", json=payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["error"], "Bad Request")
        self.assertIn("missing", data["message"])

    def test_create_product_wrong_content_type(self):
        """It should return 415 for non-JSON content types"""
        resp = self.client.post(
            "/products",
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_empty_json_body(self):
        """It should return 400 for empty or invalid JSON bodies"""
        resp = self.client.post(
            "/products",
            data="",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["error"], "Bad Request")

    def test_get_product_success(self):
        """It should retrieve a Product and return 200"""
        product = ProductFactory()
        payload = product.serialize()
        payload.pop("id", None)

        create_resp = self.client.post("/products", json=payload)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        created = create_resp.get_json()
        self.assertIsNotNone(created)
        product_id = created["id"]

        resp = self.client.get(f"/products/{product_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["id"], product_id)
        self.assertEqual(data["name"], payload["name"])
        self.assertEqual(data["description"], payload["description"])
        self.assertEqual(data["price"], payload["price"])
        self.assertEqual(data["category"], payload["category"])
        self.assertEqual(data["available"], payload["available"])
        self.assertEqual(data["stock"], payload["stock"])

    def test_list_products(self):
        """It should list all Products"""
        products = ProductFactory.create_batch(3)
        for product in products:
            payload = product.serialize()
            payload.pop("id", None)
            resp = self.client.post("/products", json=payload)
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/products")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.content_type, "application/json")

        data = resp.get_json()
        self.assertEqual(len(data), 3)

    def test_list_products_by_category(self):
        """It should list only Products matching the category query param"""
        for name, cat in [("Phone", "Electronics"), ("Shirt", "Clothing")]:
            resp = self.client.post(
                "/products",
                json={
                    "name": name,
                    "description": "d",
                    "price": "9.99",
                    "category": cat,
                    "available": True,
                },
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/products?category=Electronics")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Phone")
        self.assertEqual(data[0]["category"], "Electronics")

    def test_list_products_category_filter_case_insensitive(self):
        """It should match category case-insensitively"""
        resp = self.client.post(
            "/products",
            json={
                "name": "Cam",
                "description": "d",
                "price": "1.00",
                "category": "Electronics",
                "available": True,
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/products?category=electronics")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["category"], "Electronics")

    def test_list_products_category_empty_or_whitespace_lists_all(self):
        """It should list all Products when category is empty or whitespace after strip"""
        for i in range(2):
            resp = self.client.post(
                "/products",
                json={
                    "name": f"Item{i}",
                    "description": "d",
                    "price": "1.00",
                    "category": "Electronics",
                    "available": True,
                },
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/products?category=")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 2)

        resp = self.client.get("/products?category=%20%20")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 2)

    def test_list_products_category_duplicate_query_uses_first(self):
        """It should use the first category value when the key is repeated"""
        for name, cat in [("A", "Electronics"), ("B", "Clothing")]:
            resp = self.client.post(
                "/products",
                json={
                    "name": name,
                    "description": "d",
                    "price": "1.00",
                    "category": cat,
                    "available": True,
                },
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/products?category=Electronics&category=Clothing")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "A")

    def test_list_products_category_no_match_returns_empty_list(self):
        """It should return 200 with an empty list when no Products match category"""
        resp = self.client.post(
            "/products",
            json={
                "name": "Thing",
                "description": "d",
                "price": "1.00",
                "category": "Electronics",
                "available": True,
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/products?category=Books")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json(), [])

    def test_get_product_not_found(self):
        """It should return 404 when Product does not exist"""
        resp = self.client.get("/products/999999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["error"], "Not Found")
        self.assertIn("Product with id", data["message"])

    def test_get_product_invalid_id_format(self):
        """It should return 404 when id is not an integer (Flask routing)"""
        resp = self.client.get("/products/abc")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.content_type, "application/json")
        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["error"], "Not Found")

    def test_update_product_success(self):
        """It should update an existing Product and return 200"""
        product = ProductFactory()
        payload = product.serialize()
        payload.pop("id", None)

        create_resp = self.client.post("/products", json=payload)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        created = create_resp.get_json()
        product_id = created["id"]

        updated_data = created.copy()
        updated_data["name"] = "Updated Product Name"
        updated_data["price"] = 99.99

        resp = self.client.put(f"/products/{product_id}", json=updated_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["id"], product_id)
        self.assertEqual(data["name"], "Updated Product Name")
        self.assertEqual(str(data["price"]), "99.99")

    def test_update_product_not_found(self):
        """It should return 404 when updating a Product that does not exist"""
        product = ProductFactory()
        payload = product.serialize()
        payload["id"] = 999999

        resp = self.client.put("/products/999999", json=payload)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["error"], "Not Found")

    def test_update_product_invalid_id_format(self):
        """It should return 404 when update id is not an integer (Flask routing)"""
        product = ProductFactory()
        payload = product.serialize()

        resp = self.client.put("/products/abc", json=payload)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.content_type, "application/json")
        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["error"], "Not Found")

    def test_update_product_wrong_content_type(self):
        """It should return 415 for non-JSON content types on update"""
        resp = self.client.put(
            "/products/1",
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_product_empty_json_body(self):
        """It should return 400 for empty update body"""
        product = ProductFactory()
        payload = product.serialize()
        payload.pop("id", None)

        create_resp = self.client.post("/products", json=payload)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        created = create_resp.get_json()
        product_id = created["id"]

        resp = self.client.put(
            f"/products/{product_id}",
            data="",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["error"], "Bad Request")

    def test_delete_product_success(self):
        """It should delete an existing Product and return 204"""
        product = ProductFactory()
        payload = product.serialize()
        payload.pop("id", None)

        create_resp = self.client.post("/products", json=payload)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        created = create_resp.get_json()
        product_id = created["id"]

        resp = self.client.delete(f"/products/{product_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        get_resp = self.client.get(f"/products/{product_id}")
        self.assertEqual(get_resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_not_found_is_idempotent(self):
        """It should return 204 when deleting a missing Product (idempotent DELETE)"""
        resp = self.client.delete("/products/999999")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(resp.get_data(as_text=True), "")

    def test_delete_product_invalid_id_format(self):
        """It should return 404 when delete id is not an integer (Flask routing)"""
        resp = self.client.delete("/products/abc")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.content_type, "application/json")
        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["error"], "Not Found")

    def test_query_products_by_price_range(self):
        """It should list only Products within the given price range"""
        product1 = Product(
            name="Cheap Item",
            description="Cheap",
            category="Electronics",
            price=Decimal("9.99"),
            available=True,
        )
        product2 = Product(
            name="Mid Item",
            description="Mid",
            category="Electronics",
            price=Decimal("29.99"),
            available=True,
        )
        product3 = Product(
            name="Expensive Item",
            description="Expensive",
            category="Electronics",
            price=Decimal("99.99"),
            available=True,
        )
        product1.create()
        product2.create()
        product3.create()

        response = self.client.get(
            "/products?minimum_price=10&maximum_price=50",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Mid Item")

    def test_query_products_by_minimum_price_only(self):
        """It should list Products greater than or equal to minimum_price"""
        product1 = Product(
            name="Cheap Item",
            description="Cheap",
            category="Electronics",
            price=Decimal("9.99"),
            available=True,
        )
        product2 = Product(
            name="Mid Item",
            description="Mid",
            category="Electronics",
            price=Decimal("29.99"),
            available=True,
        )
        product1.create()
        product2.create()

        response = self.client.get(
            "/products?minimum_price=10",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Mid Item")

    def test_query_products_by_maximum_price_only(self):
        """It should list Products less than or equal to maximum_price"""
        product1 = Product(
            name="Cheap Item",
            description="Cheap",
            category="Electronics",
            price=Decimal("9.99"),
            available=True,
        )
        product2 = Product(
            name="Expensive Item",
            description="Expensive",
            category="Electronics",
            price=Decimal("99.99"),
            available=True,
        )
        product1.create()
        product2.create()

        response = self.client.get(
            "/products?maximum_price=50",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Cheap Item")

    def test_query_products_by_price_range_no_matches(self):
        """It should return an empty list when no Products match the range"""
        product = Product(
            name="Expensive Item",
            description="Expensive",
            category="Electronics",
            price=Decimal("99.99"),
            available=True,
        )
        product.create()

        response = self.client.get(
            "/products?minimum_price=10&maximum_price=50",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_list_products_by_name(self):
        """It should list only Products matching the name query param"""
        for name, cat in [("Wireless Mouse", "Electronics"), ("Keyboard", "Electronics")]:
            resp = self.client.post(
                "/products",
                json={
                    "name": name,
                    "description": "d",
                    "price": "29.99",
                    "category": cat,
                    "available": True,
                },
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/products?name=Wireless+Mouse")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Wireless Mouse")

    def test_list_products_by_name_no_match_returns_empty_list(self):
        """It should return 200 with an empty list when no Products match the name"""
        resp = self.client.post(
            "/products",
            json={
                "name": "Wireless Mouse",
                "description": "d",
                "price": "29.99",
                "category": "Electronics",
                "available": True,
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/products?name=Trackpad")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json(), [])

    def test_list_products_by_availability_true(self):
        """It should return only available products when ?available=true"""
        for name, avail in [("In Stock", True), ("Out of Stock", False)]:
            resp = self.client.post(
                "/products",
                json={
                    "name": name,
                    "description": "d",
                    "price": "9.99",
                    "category": "Electronics",
                    "available": avail,
                },
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/products?available=true")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "In Stock")
        self.assertTrue(data[0]["available"])

    def test_list_products_by_availability_false(self):
        """It should return only unavailable products when ?available=false"""
        for name, avail in [("In Stock", True), ("Out of Stock", False)]:
            resp = self.client.post(
                "/products",
                json={
                    "name": name,
                    "description": "d",
                    "price": "9.99",
                    "category": "Electronics",
                    "available": avail,
                },
            )
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.get("/products?available=false")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Out of Stock")
        self.assertFalse(data[0]["available"])

    def test_list_products_by_availability_invalid_value(self):
        """It should return 400 for an invalid ?available value"""
        resp = self.client.get("/products?available=maybe")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = resp.get_json()
        self.assertEqual(data["error"], "Bad Request")

    def test_query_products_by_price_range_invalid_input(self):
        """It should return 400 for invalid price query values"""
        response = self.client.get(
            "/products?minimum_price=abc&maximum_price=50",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_purchase_product_success(self):
        """It should decrement stock and return 200 with updated product"""
        resp = self.client.post(
            "/products",
            json={
                "name": "Stocked Item",
                "description": "d",
                "price": "9.99",
                "category": "Electronics",
                "available": True,
                "stock": 5,
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        product_id = resp.get_json()["id"]

        pur = self.client.put(f"/products/{product_id}/purchase")
        self.assertEqual(pur.status_code, status.HTTP_200_OK)
        data = pur.get_json()
        self.assertEqual(data["stock"], 4)
        self.assertTrue(data["available"])

    def test_purchase_product_last_unit_marks_unavailable(self):
        """It should set unavailable when stock reaches zero after purchase"""
        resp = self.client.post(
            "/products",
            json={
                "name": "Last One",
                "description": "d",
                "price": "1.00",
                "category": "c",
                "available": True,
                "stock": 1,
            },
        )
        product_id = resp.get_json()["id"]
        pur = self.client.put(f"/products/{product_id}/purchase")
        self.assertEqual(pur.status_code, status.HTTP_200_OK)
        data = pur.get_json()
        self.assertEqual(data["stock"], 0)
        self.assertFalse(data["available"])

    def test_purchase_product_conflict_when_unavailable(self):
        """It should return 409 when product is not available"""
        resp = self.client.post(
            "/products",
            json={
                "name": "Gone",
                "description": "d",
                "price": "1.00",
                "category": "c",
                "available": False,
                "stock": 3,
            },
        )
        product_id = resp.get_json()["id"]
        pur = self.client.put(f"/products/{product_id}/purchase")
        self.assertEqual(pur.status_code, status.HTTP_409_CONFLICT)

    def test_purchase_product_conflict_when_out_of_stock(self):
        """It should return 409 when stock is zero"""
        resp = self.client.post(
            "/products",
            json={
                "name": "Empty",
                "description": "d",
                "price": "1.00",
                "category": "c",
                "available": True,
                "stock": 0,
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        product_id = resp.get_json()["id"]
        pur = self.client.put(f"/products/{product_id}/purchase")
        self.assertEqual(pur.status_code, status.HTTP_409_CONFLICT)

    def test_purchase_product_not_found(self):
        """It should return 404 when purchasing a missing product"""
        resp = self.client.put("/products/999999/purchase")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_health_endpoint(self):
        """It should return 200 OK for health check"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "OK")
