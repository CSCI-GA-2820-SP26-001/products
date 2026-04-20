(function initAdminListPage() {
  "use strict";

  var listAllButton = document.getElementById("list-all-button");
  var message = document.getElementById("message");
  var emptyState = document.getElementById("empty-state");
  var productsTable = document.getElementById("products-table");
  var productsTbody = document.getElementById("products-tbody");

  function showMessage(text, type) {
    message.textContent = text;
    message.className = "message";
    if (type) {
      message.classList.add(type);
    }
  }

  function clearResults() {
    productsTbody.innerHTML = "";
    productsTable.hidden = true;
    emptyState.hidden = false;
  }

  function renderProducts(products) {
    productsTbody.innerHTML = "";

    if (products.length === 0) {
      productsTable.hidden = true;
      emptyState.hidden = false;
      emptyState.textContent = "No products found.";
      showMessage("No products exist in the catalog.", "error");
      return;
    }

    emptyState.hidden = true;
    productsTable.hidden = false;

    for (var i = 0; i < products.length; i++) {
      var p = products[i];
      var row = document.createElement("tr");
      row.innerHTML =
        "<td>" + p.id + "</td>" +
        "<td>" + (p.name || "") + "</td>" +
        "<td>" + (p.category || "") + "</td>" +
        "<td>" + (p.price || "") + "</td>" +
        "<td>" + (p.stock != null ? p.stock : "") + "</td>" +
        "<td>" + (p.available ? "Yes" : "No") + "</td>";
      productsTbody.appendChild(row);
    }

    showMessage(products.length + " product(s) found.", "success");
  }

  async function listAllProducts() {
    clearResults();
    showMessage("Loading products...", null);

    var response = await fetch("/products", { method: "GET" });
    var payload = await response.json().catch(function () { return null; });

    if (!response.ok) {
      showMessage("Failed to retrieve products.", "error");
      return;
    }

    renderProducts(payload || []);
  }

  listAllButton.addEventListener("click", function onListAllClick() {
    listAllProducts().catch(function onListError() {
      clearResults();
      showMessage("Unexpected error while listing products.", "error");
    });
  });
})();
