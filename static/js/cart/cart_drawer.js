const cartDrawer = document.getElementById("cartDrawer");
const cartOverlay = document.getElementById("cartOverlay");

const cartToggle = document.getElementById("cartToggle");
const closeCartDrawer = document.getElementById("closeCartDrawer");

// =======================
// Drawer
// =======================

function openDrawer() {

    loadCart();

    cartDrawer.classList.add("open");
    cartOverlay.classList.add("show");
    document.body.classList.add("cart-is-open");
    cartDrawer.setAttribute("aria-hidden", "false");

}

function closeDrawer() {

    cartDrawer.classList.remove("open");
    cartOverlay.classList.remove("show");
    document.body.classList.remove("cart-is-open");
    cartDrawer.setAttribute("aria-hidden", "true");

}

if (cartToggle)
    cartToggle.addEventListener("click", openDrawer);

if (closeCartDrawer)
    closeCartDrawer.addEventListener("click", closeDrawer);

if (cartOverlay)
    cartOverlay.addEventListener("click", closeDrawer);

document.addEventListener("click", function (event) {
    if (event.target.closest("#continueShopping, #emptyContinueShopping")) {
        closeDrawer();
    }
});

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && cartDrawer.classList.contains("open")) {
        closeDrawer();
    }
});

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
                    <div class="cart-empty-state">
                        <div class="empty-icon-wrap"><i class="bi bi-bag"></i></div>
                        <p class="empty-title">Your bag is waiting</p>
                        <p class="empty-text">Add something beautiful to get started.</p>
                        <button id="emptyContinueShopping" class="empty-continue" type="button">Explore the collection</button>
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

    const itemTotal = Number(item.price) * item.quantity;

    return `
        <article class="cart-item">
            <div class="cart-item-image-wrap">
                <img src="${item.image}" alt="${item.name}" class="cart-product-image">
            </div>
            <div class="cart-item-content">
                <div class="cart-item-heading">
                    <div>
                        <span class="cart-item-category">Casaio selection</span>
                        <h6>${item.name}</h6>
                    </div>
                    <button class="remove-item" data-id="${item.id}" aria-label="Remove ${item.name}">
                        <i class="bi bi-trash3"></i>
                    </button>
                </div>
                <div class="cart-item-price-row">
                    <span>₹${Number(item.price).toFixed(2)} each</span>
                    <strong>₹${itemTotal.toFixed(2)}</strong>
                </div>
                <div class="cart-item-controls">
                    <div class="quantity-group" aria-label="Quantity">
                        <button class="quantity-btn" data-id="${item.id}" data-action="decrease" aria-label="Decrease quantity">
                            <i class="bi bi-dash"></i>
                        </button>
                        <span>${item.quantity}</span>
                        <button class="quantity-btn" data-id="${item.id}" data-action="increase" aria-label="Increase quantity">
                            <i class="bi bi-plus"></i>
                        </button>
                    </div>
                    <span class="cart-item-stock"><i class="bi bi-check2"></i> In stock</span>
                </div>
            </div>
        </article>
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