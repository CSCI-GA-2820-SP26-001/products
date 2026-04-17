(function initAdminCreatePage() {
  "use strict";

  const createForm = document.getElementById("create-form");
  const message = document.getElementById("message");
  const createdProductCard = document.getElementById("created-product");
  const createdProductDetails = document.getElementById("created-product-details");

  const nameInput = document.getElementById("name");
  const descriptionInput = document.getElementById("description");
  const priceInput = document.getElementById("price");
  const categoryInput = document.getElementById("category");
  const stockInput = document.getElementById("stock");
  const availableInput = document.getElementById("available");

  function showMessage(text, type) {
    message.textContent = text;
    message.className = "message";
    if (type) {
      message.classList.add(type);
    }
  }

  function clearForm() {
    nameInput.value = "";
    descriptionInput.value = "";
    priceInput.value = "";
    categoryInput.value = "";
    stockInput.value = "0";
    availableInput.checked = false;
  }

  function clearDetails() {
    createdProductDetails.innerHTML = "";
    createdProductCard.classList.add("hidden");
  }

  function renderDetails(product) {
    var entries = [
      ["ID", product.id],
      ["Name", product.name],
      ["Description", product.description || ""],
      ["Price", product.price],
      ["Category", product.category],
      ["Stock", product.stock],
      ["Available", product.available ? "Yes" : "No"],
    ];

    createdProductDetails.innerHTML = entries
      .map(function (entry) {
        return "<dt>" + entry[0] + "</dt><dd>" + entry[1] + "</dd>";
      })
      .join("");
    createdProductCard.classList.remove("hidden");
  }

  function getErrorMessage(payload, fallback) {
    if (payload && payload.message) {
      return payload.message;
    }
    return fallback;
  }

  function buildCreatePayload() {
    var priceValue = Number(priceInput.value);
    if (!Number.isFinite(priceValue) || priceValue < 0) {
      throw new Error("Price must be a valid positive decimal value.");
    }

    var stockValue = parseInt(stockInput.value, 10);
    if (!Number.isInteger(stockValue) || stockValue < 0) {
      throw new Error("Stock must be a whole number greater than or equal to 0.");
    }

    return {
      name: nameInput.value.trim(),
      description: descriptionInput.value.trim(),
      price: priceValue.toFixed(2),
      category: categoryInput.value.trim(),
      stock: stockValue,
      available: availableInput.checked,
    };
  }

  async function createProduct(event) {
    event.preventDefault();
    clearDetails();

    var payload;
    try {
      payload = buildCreatePayload();
    } catch (error) {
      showMessage(error.message, "error");
      return;
    }

    showMessage("Creating product...", null);

    var response = await fetch("/products", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    var data = await response.json().catch(function () {
      return null;
    });

    if (!response.ok) {
      showMessage(getErrorMessage(data, "Failed to create product."), "error");
      return;
    }

    clearForm();
    renderDetails(data);
    showMessage("Product created successfully.", "success");
  }

  createForm.addEventListener("submit", function onSubmit(event) {
    createProduct(event).catch(function onCreateError() {
      showMessage("Unexpected error while creating the product.", "error");
    });
  });
})();
