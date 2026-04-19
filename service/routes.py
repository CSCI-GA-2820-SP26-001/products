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
from decimal import Decimal, InvalidOperation
from flask import jsonify, request, url_for, abort, render_template
from flask import current_app as app  # Import Flask application
from service.models import Product
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
        "paths": ["/products", "/products/{id}", "/products/{id}/purchase", "/health"],
    }, status.HTTP_200_OK


######################################################################
# ADMIN UI
######################################################################
@app.route("/admin/products/update", methods=["GET"])
def admin_update_product_page():
    """Render the admin UI for retrieving and updating products."""
    return render_template("admin_product_update.html"), status.HTTP_200_OK


@app.route("/admin/products/create", methods=["GET"])
def admin_create_product_page():
    """Render the admin UI for creating products."""
    return render_template("admin_product_create.html"), status.HTTP_200_OK


@app.route("/admin/products/delete", methods=["GET"])
def admin_delete_product_page():
    """Render the admin UI for deleting products."""
    return render_template("admin_product_delete.html"), status.HTTP_200_OK


@app.route("/admin/products/read", methods=["GET"])
def admin_read_product_page():
    """Render the admin UI for retrieving products by id."""
    return render_template("admin_product_read.html"), status.HTTP_200_OK


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
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Content-Type must be application/json",
        )

    product = Product()
    product.deserialize(request.get_json(silent=True))
    product.create()
    app.logger.info("Product [%s] created with id [%s]", product.name, product.id)

    location_url = url_for("create_products", _external=True)
    return (
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": f"{location_url}/{product.id}"},
    )


######################################################################
# RETRIEVE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Returns a Product when given its id"""
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id {product_id} was not found.",
        )

    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# PURCHASE A PRODUCT (decrement stock)
######################################################################
@app.route("/products/<int:product_id>/purchase", methods=["PUT"])
def purchase_product(product_id):
    """Purchase one unit: decrement stock; unavailable when stock is depleted."""
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id {product_id} was not found.",
        )
    if not product.available or product.stock <= 0:
        abort(
            status.HTTP_409_CONFLICT,
            "Product is not available for purchase (unavailable or out of stock).",
        )
    product.stock -= 1
    if product.stock <= 0:
        product.available = False
    product.update()
    app.logger.info(
        "Product [%s] purchased; stock is now [%s]", product_id, product.stock
    )
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Updates an existing Product"""
    if not request.is_json:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Content-Type must be application/json",
        )

    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id {product_id} was not found.",
        )

    data = request.get_json(silent=True) or {}
    data["id"] = product_id
    product.deserialize(data)
    product.update()
    app.logger.info("Product [%s] updated", product_id)

    return jsonify(product.serialize()), status.HTTP_200_OK


############################################################
# List products
############################################################
def _filter_products(name, available, category, minimum_price, maximum_price):
    """Return a filtered list of products based on the provided query parameters."""
    if available is not None:
        app.logger.info("Request to list products with available [%s]...", available)
        return Product.find_by_availability(available)

    if name:
        app.logger.info("Request to list products with name [%s]...", name)
        return Product.find_by_name(name).all()

    if category:
        app.logger.info("Request to list products with category [%s]...", category)
        return Product.find_by_category(category)

    if minimum_price or maximum_price:
        app.logger.info(
            "Request to list products with minimum_price [%s] and maximum_price [%s]...",
            minimum_price,
            maximum_price,
        )
        try:
            min_price = Decimal(minimum_price) if minimum_price else None
            max_price = Decimal(maximum_price) if maximum_price else None
        except InvalidOperation:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "minimum_price and maximum_price must be valid decimal numbers",
            )
        return Product.find_by_price_range(min_price, max_price)

    app.logger.info("Request to list all products...")
    return Product.all()


@app.route("/products", methods=["GET"])
def list_products():
    """List products, optionally filtered by available, name, category, or price range."""
    available_raw = request.args.get("available")
    name = request.args.get("name", "").strip() or None
    category = request.args.get("category", "").strip() or None
    minimum_price = request.args.get("minimum_price", "").strip() or None
    maximum_price = request.args.get("maximum_price", "").strip() or None

    available = None
    if available_raw is not None and available_raw.strip():
        value = available_raw.strip().lower()
        if value not in ("true", "false"):
            abort(status.HTTP_400_BAD_REQUEST, "available must be 'true' or 'false'")
        available = value == "true"

    products = _filter_products(name, available, category, minimum_price, maximum_price)
    return jsonify([product.serialize() for product in products])


############################################################
# Delete a Product
############################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Deletes a Product"""
    product = Product.find(product_id)
    if not product:
        app.logger.info(
            "Delete idempotent: no product with id [%s] (returning 204)",
            product_id,
        )
        return "", status.HTTP_204_NO_CONTENT

    product.delete()
    app.logger.info("Product [%s] deleted", product_id)
    return "", status.HTTP_204_NO_CONTENT


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {"status": "OK"}, status.HTTP_200_OK
