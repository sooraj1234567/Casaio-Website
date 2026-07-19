const cartDrawer = document.getElementById("cartDrawer");
const cartOverlay = document.getElementById("cartOverlay");

const cartToggle = document.getElementById("cartToggle");
const closeCartDrawer = document.getElementById("closeCartDrawer");

// =======================
// Drawer
// =======================

function openDrawer() {

    loadCart();

    cartDrawer.classList.add("active");
    cartOverlay.classList.add("active");

}

function closeDrawer() {

    cartDrawer.classList.remove("active");
    cartOverlay.classList.remove("active");

}

if (cartToggle)
    cartToggle.addEventListener("click", openDrawer);

if (closeCartDrawer)
    closeCartDrawer.addEventListener("click", closeDrawer);

if (cartOverlay)
    cartOverlay.addEventListener("click", closeDrawer);

// =======================
// Load Cart
// =======================

function loadCart() {

    getCart()

        .then(data => {

            const container = document.getElementById("cartItemsContainer");

            container.innerHTML = "";

            if (data.items.length === 0) {

                container.innerHTML = `
                    <div class="text-center py-5 text-muted">
                        <i class="bi bi-cart3 fs-1"></i>
                        <p class="mt-3">Your cart is empty</p>
                    </div>
                `;

            } else {

                data.items.forEach(item => {

                    container.innerHTML += renderCartItem(item);

                });

            }

            document.getElementById("drawerSubtotal").innerText =
                "₹" + data.subtotal;

            updateCartBadge(data.total_items);

        })

        .catch(error => {

            console.error("Load Cart Error:", error);

        });

}

function renderCartItem(item) {

    return `
        <div class="cart-item border-bottom pb-3 mb-3">

            <div class="d-flex">

                <img
                    src="${item.image}"
                    alt="${item.name}"
                    class="cart-product-image rounded">

                <div class="flex-grow-1 ms-3">

                    <h6 class="fw-semibold mb-1">
                        ${item.name}
                    </h6>

                    <div class="text-muted mb-2">
                        ₹${Number(item.price).toFixed(2)}
                    </div>

                    <div class="d-flex justify-content-between align-items-center">

                        <div class="input-group input-group-sm quantity-group">

                            <button
                                class="btn btn-outline-dark quantity-btn"
                                data-id="${item.id}"
                                data-action="decrease">

                                −

                            </button>

                            <input
                                type="text"
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

                        <button
                            class="btn btn-link text-danger remove-item"
                            data-id="${item.id}">

                            <i class="bi bi-trash"></i>

                        </button>

                    </div>

                </div>

            </div>

        </div>
    `;

}

function updateCartBadge(totalItems) {

    const badge = document.getElementById("cartBadge");

    if (!badge) return;

    if (totalItems > 0) {

        badge.style.display = "inline-block";
        badge.innerText = totalItems;

    } else {

        badge.style.display = "none";

    }

}

// =======================
// Add To Cart Button
// =======================

const addToCartBtn = document.getElementById("addToCartBtn");

if (addToCartBtn) {

    addToCartBtn.addEventListener("click", function () {

        addToCart(this.dataset.productId)

            .then(data => {

                if (data.success) {

                    openDrawer();

                } else {

                    alert(data.message);

                }

            });

    });

}

document.addEventListener("DOMContentLoaded", function () {

    loadCart();

});

document.addEventListener("click", function (e) {

    // Remove Item
    const removeButton = e.target.closest(".remove-item");

    if (removeButton) {

        removeCartItem(removeButton.dataset.id)

            .then(data => {

                if (data.success) {

                    loadCart();

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

                loadCart();

            }

        })

        .catch(error => console.error(error));
    }

});