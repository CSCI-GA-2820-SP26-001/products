(function initAdminDeletePage() {
  "use strict";

  var deleteInput = document.getElementById("delete-product-id");
  var deleteButton = document.getElementById("delete-button");
  var message = document.getElementById("message");

  function showMessage(text, type) {
    message.textContent = text;
    message.className = "message";
    if (type) {
      message.classList.add(type);
    }
  }

  async function deleteProduct() {
    var productId = parseInt(deleteInput.value, 10);
    if (!Number.isInteger(productId) || productId <= 0) {
      showMessage("Enter a valid product ID before deleting.", "error");
      return;
    }

    // First verify the product exists
    var getResponse = await fetch("/products/" + productId, { method: "GET" });
    if (!getResponse.ok) {
      var payload = await getResponse.json().catch(function () {
        return null;
      });
      var errorMsg =
        payload && payload.message
          ? payload.message
          : "Product with id " + productId + " was not found.";
      showMessage(errorMsg, "error");
      return;
    }

    showMessage("Deleting product...", null);

    var response = await fetch("/products/" + productId, { method: "DELETE" });

    if (response.status === 204) {
      deleteInput.value = "";
      showMessage(
        "Product " + productId + " has been deleted successfully.",
        "success"
      );
      return;
    }

    var data = await response.json().catch(function () {
      return null;
    });
    showMessage(
      data && data.message ? data.message : "Failed to delete product.",
      "error"
    );
  }

  deleteButton.addEventListener("click", function onDeleteClick() {
    deleteProduct().catch(function onDeleteError() {
      showMessage("Unexpected error while deleting the product.", "error");
    });
  });
})();
