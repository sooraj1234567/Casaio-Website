function renderCartPageItem(item) {

    const total = Number(item.price) * Number(item.quantity);

    return `

    <div class="card shadow-sm border-0 rounded-4 mb-4">

        <div class="card-body">

            <div class="row align-items-center">

                <div class="col-lg-2 text-center">

                    <img
                        src="${item.image}"
                        class="cart-page-image">

                </div>

                <div class="col-lg-4">

                    <h5 class="fw-bold mb-2">

                        ${item.name}

                    </h5>

                    <div class="text-muted">

                        Premium Product

                    </div>

                    <div class="mt-3 fs-5 fw-semibold">

                        ₹${Number(item.price).toFixed(2)}

                    </div>

                </div>

                <div class="col-lg-3">

                    <div class="input-group quantity-group mx-auto">

                        <button
                            class="btn btn-outline-dark quantity-btn"
                            data-id="${item.id}"
                            data-action="decrease">

                            -

                        </button>

                        <input
                            class="form-control text-center"
                            value="${item.quantity}"
                            readonly>

                        <button
                            class="btn btn-outline-dark quantity-btn"
                            data-id="${item.id}"
                            data-action="increase">

                            +

                        </button>

                    </div>

                </div>

                <div class="col-lg-2 text-center">

                    <h5>

                        ₹${total.toFixed(2)}

                    </h5>

                </div>

                <div class="col-lg-1 text-end">

                    <button
                        class="btn btn-light remove-item"
                        data-id="${item.id}">

                        <i class="bi bi-trash text-danger"></i>

                    </button>

                </div>

            </div>

        </div>

    </div>

    `;

}

function loadCartPage() {

    getCart()

        .then(data => {

            const container = document.getElementById("cartPageItems");

            if (!container) return;

            container.innerHTML = "";

            if (data.items.length === 0) {

                container.innerHTML = `
                    <div class="text-center py-5">

                        <i class="bi bi-cart-x display-1 text-secondary"></i>

                        <h4 class="mt-3">
                            Your cart is empty
                        </h4>

                        <p class="text-muted">
                            Looks like you haven't added any products yet.
                        </p>

                        <a href="/products/" class="btn btn-dark mt-3">
                            Continue Shopping
                        </a>

                    </div>
                `;

                document.getElementById("summarySubtotal").innerText = "₹0";
                document.getElementById("summaryTotal").innerText = "₹0";

                return;

            }

            data.items.forEach(item => {

                container.innerHTML += renderCartPageItem(item);

            });

            document.getElementById("summarySubtotal").innerText =
                "₹" + data.subtotal;

            document.getElementById("summaryTotal").innerText =
                "₹" + data.subtotal;

        });

}

document.addEventListener("click", function (e) {

    // Remove Item
    const removeButton = e.target.closest(".remove-item");

    if (removeButton) {

        removeCartItem(removeButton.dataset.id)

            .then(data => {

                if (data.success) {

                    loadCartPage();
                    loadCart(); // Refresh Cart Drawer

                }

            })

            .catch(error => console.error(error));

        return;
    }

    // Quantity Update
    const quantityButton = e.target.closest(".quantity-btn");

    if (quantityButton) {

        updateCartQuantity(
            quantityButton.dataset.id,
            quantityButton.dataset.action
        )

        .then(data => {

            if (data.success) {

                loadCartPage();
                loadCart(); // Refresh Cart Drawer

            }

        })

        .catch(error => console.error(error));

    }

});

document.addEventListener("DOMContentLoaded", function () {

    loadCartPage();

});

