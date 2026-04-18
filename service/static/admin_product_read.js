(function initAdminReadPage() {
  "use strict";

  const retrieveInput = document.getElementById("retrieve-product-id");
  const retrieveButton = document.getElementById("retrieve-button");
  const message = document.getElementById("message");

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
    stockInput.value = "";
    availableInput.checked = false;
  }

  function fillForm(product) {
    nameInput.value = product.name || "";
    descriptionInput.value = product.description || "";
    priceInput.value = product.price || "";
    categoryInput.value = product.category || "";
    stockInput.value = String(product.stock ?? "");
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
      clearForm();
      showMessage("Enter a valid product ID before retrieving.", "error");
      return;
    }

    clearForm();
    showMessage("Retrieving product...", null);

    const response = await fetch(`/products/${productId}`, { method: "GET" });
    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      showMessage(
        getErrorMessage(payload, "Could not retrieve this product."),
        "error"
      );
      return;
    }

    fillForm(payload);
    showMessage(`Product ${payload.id} retrieved successfully.`, "success");
  }

  retrieveButton.addEventListener("click", function onRetrieveClick() {
    retrieveProduct().catch(function onRetrieveError() {
      clearForm();
      showMessage("Unexpected error while retrieving the product.", "error");
    });
  });
})();
