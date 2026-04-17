(function initAdminUpdatePage() {
  "use strict";

  const retrieveInput = document.getElementById("retrieve-product-id");
  const retrieveButton = document.getElementById("retrieve-button");
  const updateButton = document.getElementById("update-button");
  const updateForm = document.getElementById("update-form");
  const message = document.getElementById("message");
  const updatedProductCard = document.getElementById("updated-product");
  const updatedProductDetails = document.getElementById("updated-product-details");

  const nameInput = document.getElementById("name");
  const descriptionInput = document.getElementById("description");
  const priceInput = document.getElementById("price");
  const categoryInput = document.getElementById("category");
  const stockInput = document.getElementById("stock");
  const availableInput = document.getElementById("available");

  let currentProductId = null;

  function showMessage(text, type) {
    message.textContent = text;
    message.className = "message";
    if (type) {
      message.classList.add(type);
    }
  }

  function clearDetails() {
    updatedProductDetails.innerHTML = "";
    updatedProductCard.classList.add("hidden");
  }

  function clearForm() {
    nameInput.value = "";
    descriptionInput.value = "";
    priceInput.value = "";
    categoryInput.value = "";
    stockInput.value = "0";
    availableInput.checked = false;
  }

  function renderDetails(product) {
    const entries = [
      ["ID", product.id],
      ["Name", product.name],
      ["Description", product.description || ""],
      ["Price", product.price],
      ["Category", product.category],
      ["Stock", product.stock],
      ["Available", product.available ? "Yes" : "No"],
    ];

    updatedProductDetails.innerHTML = entries
      .map(([label, value]) => `<dt>${label}</dt><dd>${value}</dd>`)
      .join("");
    updatedProductCard.classList.remove("hidden");
  }

  function fillForm(product) {
    nameInput.value = product.name || "";
    descriptionInput.value = product.description || "";
    priceInput.value = product.price || "";
    categoryInput.value = product.category || "";
    stockInput.value = String(product.stock ?? 0);
    availableInput.checked = Boolean(product.available);
  }

  function getErrorMessage(payload, fallback) {
    if (payload && payload.message) {
      return payload.message;
    }
    return fallback;
  }

  async function retrieveProduct() {
    const productId = parseInt(retrieveInput.value, 10);
    if (!Number.isInteger(productId) || productId <= 0) {
      currentProductId = null;
      updateButton.disabled = true;
      clearDetails();
      clearForm();
      showMessage("Enter a valid product ID before retrieving.", "error");
      return;
    }

    currentProductId = null;
    updateButton.disabled = true;
    clearDetails();
    clearForm();
    showMessage("Retrieving product...", null);

    const response = await fetch(`/products/${productId}`, { method: "GET" });
    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      currentProductId = null;
      updateButton.disabled = true;
      showMessage(
        getErrorMessage(payload, "Could not retrieve this product."),
        "error"
      );
      return;
    }

    currentProductId = payload.id;
    fillForm(payload);
    updateButton.disabled = false;
    showMessage(`Product ${payload.id} loaded. You can edit and update now.`, "success");
  }

  function buildUpdatePayload() {
    const priceValue = Number(priceInput.value);
    if (!Number.isFinite(priceValue)) {
      throw new Error("Price must be a valid decimal value.");
    }

    const stockValue = parseInt(stockInput.value, 10);
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

  async function updateProduct(event) {
    event.preventDefault();

    if (!currentProductId) {
      showMessage("Retrieve a product before updating.", "error");
      return;
    }

    let payload;
    try {
      payload = buildUpdatePayload();
    } catch (error) {
      showMessage(error.message, "error");
      return;
    }

    showMessage("Updating product...", null);

    const response = await fetch(`/products/${currentProductId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      showMessage(getErrorMessage(data, "Update failed."), "error");
      return;
    }

    fillForm(data);
    renderDetails(data);
    showMessage("Product updated successfully.", "success");
  }

  stockInput.addEventListener("input", function onStockChange() {
    const value = parseInt(stockInput.value, 10);
    if (Number.isInteger(value) && value <= 0) {
      availableInput.checked = false;
    }
  });

  retrieveButton.addEventListener("click", function onRetrieveClick() {
    retrieveProduct().catch(function onRetrieveError() {
      currentProductId = null;
      updateButton.disabled = true;
      clearDetails();
      clearForm();
      showMessage("Unexpected error while retrieving the product.", "error");
    });
  });

  updateForm.addEventListener("submit", function onSubmit(event) {
    updateProduct(event).catch(function onUpdateError() {
      showMessage("Unexpected error while updating the product.", "error");
    });
  });
})();
