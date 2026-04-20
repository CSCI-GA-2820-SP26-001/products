(function initAdminPurchasePage() {
  "use strict";

  const purchaseInput = document.getElementById("purchase-product-id");
  const purchaseButton = document.getElementById("purchase-button");
  const message = document.getElementById("message");
  const purchasedProductCard = document.getElementById("purchased-product");
  const purchasedProductDetails = document.getElementById("purchased-product-details");

  function showMessage(text, type) {
    message.textContent = text;
    message.className = "message";
    if (type) {
      message.classList.add(type);
    }
  }

  function clearDetails() {
    purchasedProductDetails.innerHTML = "";
    purchasedProductCard.classList.add("hidden");
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

    purchasedProductDetails.innerHTML = entries
      .map(([label, value]) => `<dt>${label}</dt><dd>${value}</dd>`)
      .join("");
    purchasedProductCard.classList.remove("hidden");
  }

  function getErrorMessage(payload, fallback) {
    if (payload && payload.message) {
      return payload.message;
    }
    return fallback;
  }

  async function purchaseProduct() {
    const productId = parseInt(purchaseInput.value, 10);
    if (!Number.isInteger(productId) || productId <= 0) {
      clearDetails();
      showMessage("Enter a valid product ID before purchasing.", "error");
      return;
    }

    clearDetails();
    showMessage("Purchasing product...", null);

    const response = await fetch(`/products/${productId}/purchase`, {
      method: "PUT",
    });
    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      showMessage(
        getErrorMessage(payload, "Purchase failed. Try again."),
        "error"
      );
      return;
    }

    renderDetails(payload);
    showMessage(
      `Product ${payload.id} purchased successfully. Stock is now ${payload.stock}.`,
      "success"
    );
  }

  purchaseButton.addEventListener("click", function onPurchaseClick() {
    purchaseProduct().catch(function onPurchaseError() {
      clearDetails();
      showMessage("Unexpected error while purchasing the product.", "error");
    });
  });
})();
