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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Product, DataValidationError, DatabaseConnectionError
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/", methods=["GET"])
def index():
    """Root URL response"""
    return {
        "name": "Product Catalog Service",
        "version": "1.0",
        "paths": [
            "/products",
            "/products/{id}"
        ]
    }, status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
# CREATE A PRODUCT
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """Creates a Product"""
    if not request.is_json:
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Content-Type must be application/json")

    data = request.get_json(silent=True)
    if not data:
        raise DataValidationError("Invalid Product: body of request contained bad or no data")

    product = Product()
    product.deserialize(data)
    product.create()

    location_url = url_for("create_products", _external=True)
    return (
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": f"{location_url}/{product.id}"},
    )


######################################################################
# RETRIEVE A PRODUCT
######################################################################
@app.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):
    """Returns a Product when given its id"""
    try:
        product_id_int = int(product_id)
    except (TypeError, ValueError) as error:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Invalid product id format: must be an integer ({error})",
        )

    product = Product.find(product_id_int)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id {product_id_int} was not found.",
        )

    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE A PRODUCT
######################################################################
@app.route("/products/<product_id>", methods=["PUT"])
def update_product(product_id):
    """Updates an existing Product"""
    if not request.is_json:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Content-Type must be application/json",
        )

    try:
        product_id_int = int(product_id)
    except (TypeError, ValueError) as error:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Invalid product id format: must be an integer ({error})",
        )

    product = Product.find(product_id_int)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id {product_id_int} was not found.",
        )

    data = request.get_json(silent=True)
    if not data:
        raise DataValidationError(
            "Invalid Product: body of request contained bad or no data"
        )

    data["id"] = product_id_int
    product.deserialize(data)
    product.update()

    return jsonify(product.serialize()), status.HTTP_200_OK

############################################################
# List products
############################################################
@app.route("/products", methods=["GET"])
def list_products():
    """List products"""
    app.logger.info("Request to list all products...")
    products = []
    try:
        products = Product.all()
    except DatabaseConnectionError as err:
        abort(status.HTTP_503_SERVICE_UNAVAILABLE, err)

    return jsonify(products)
