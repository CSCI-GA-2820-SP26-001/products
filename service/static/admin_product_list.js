(function initAdminListPage() {
  "use strict";

  var listAllButton = document.getElementById("list-all-button");
  var queryButton = document.getElementById("query-button");
  var categoryInput = document.getElementById("category-input");
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

  function renderProducts(products, context) {
    productsTbody.innerHTML = "";
    context = context || { mode: "list" };

    if (products.length === 0) {
      productsTable.hidden = true;
      emptyState.hidden = false;
      if (context.mode === "category") {
        emptyState.textContent = 'No products found for category "' + context.value + '".';
        showMessage('No products found for category "' + context.value + '".', "error");
      } else {
        emptyState.textContent = "No products found.";
        showMessage("No products exist in the catalog.", "error");
      }
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

    if (context.mode === "category") {
      showMessage(
        products.length + ' product(s) found for category "' + context.value + '".',
        "success"
      );
    } else {
      showMessage(products.length + " product(s) found.", "success");
    }
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

    renderProducts(payload || [], { mode: "list" });
  }

  async function queryProductsByCategory() {
    var category = categoryInput.value.trim();

    if (!category) {
      clearResults();
      emptyState.textContent = 'Enter a category and press "Query" to search.';
      showMessage("Enter a category to query products.", "error");
      return;
    }

    clearResults();
    showMessage('Loading products for category "' + category + '"...', null);

    var params = new URLSearchParams({ category: category });
    var response = await fetch("/products?" + params.toString(), { method: "GET" });
    var payload = await response.json().catch(function () { return null; });

    if (!response.ok) {
      showMessage("Failed to retrieve products.", "error");
      return;
    }

    renderProducts(payload || [], { mode: "category", value: category });
  }

  listAllButton.addEventListener("click", function onListAllClick() {
    listAllProducts().catch(function onListError() {
      clearResults();
      showMessage("Unexpected error while listing products.", "error");
    });
  });

  queryButton.addEventListener("click", function onQueryClick() {
    queryProductsByCategory().catch(function onQueryError() {
      clearResults();
      showMessage("Unexpected error while querying products.", "error");
    });
  });

  categoryInput.addEventListener("keydown", function onCategoryKeydown(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      queryButton.click();
    }
  });
})();
