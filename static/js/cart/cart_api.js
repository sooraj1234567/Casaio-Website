// =========================================
// CART.JS
// =========================================

console.log("Cart JS Loaded");

// =========================================
// CSRF Token
// =========================================

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;

            }

        }

    }

    return cookieValue;

}

// =========================================
// Get Cart
// =========================================

function getCart() {

    return fetch("/cart/data/", {

        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }

    })

    .then(response => response.json());

}

// =========================================
// Cart Badge
// =========================================

function setCartBadge(totalItems) {

    const badge = document.getElementById("cartBadge");

    if (!badge) return;

    badge.textContent = totalItems;

    if (totalItems > 0) {

        badge.style.display = "inline-block";

    }

    else {

        badge.style.display = "none";

    }

}

// =========================================
// Update Badge
// =========================================

function updateCartBadge() {

    getCart()

    .then(data => {

        if (data.total_items !== undefined) {

            setCartBadge(data.total_items);

        }

    })

    .catch(error => {

        console.error(error);

    });

}

// =========================================
// Add To Cart
// =========================================

function addToCart(productId, quantity = 1) {

    return fetch(`/cart/add/${productId}/`, {

        method: "POST",

        headers: {

            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"

        },

        body: new URLSearchParams({ quantity })

    })

    .then(response => response.json())

    .then(data => {

        if (data.total_items !== undefined) {

            setCartBadge(data.total_items);

        }

        if (data.login_required && data.login_url) {

            window.location.href = data.login_url;

        }

        return data;

    });

}

// Intercept every add-to-cart form before the browser navigates to the JSON endpoint.
document.addEventListener("submit", function (event) {

    const form = event.target.closest('form[action*="/cart/add/"]');

    if (!form) return;

    event.preventDefault();

    const productId = form.action.match(/\/cart\/add\/(\d+)\//)?.[1];
    const quantity = Number(form.querySelector('[name="quantity"]')?.value || 1);

    if (!productId) {
        console.error("Unable to determine the product id for the cart request.");
        return;
    }

    addToCart(productId, quantity)
        .then(data => {
            if (data.login_required) {
                window.location.href = data.login_url;
            } else if (data.success && typeof openDrawer === "function") {
                openDrawer();
            } else if (!data.success) {
                alert(data.message || "Unable to add product.");
            }
        })
        .catch(error => {
            console.error("Add to Cart Error:", error);
            alert("Something went wrong while adding the product.");
        });

});

// =========================================
// Remove Cart Item
// =========================================

function removeCartItem(itemId) {

    return fetch(`/cart/remove/${itemId}/`, {

        method: "POST",

        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest"
        }

    })

    .then(response => response.json())

    .then(data => {

        if (data.total_items !== undefined) {

            setCartBadge(data.total_items);

        }

        return data;

    });

}

// =========================================
// Update Cart Quantity
// =========================================

function updateCartQuantity(itemId, action) {

    return fetch(`/cart/update/${itemId}/`, {

        method: "POST",

        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        },

        body: new URLSearchParams({ action })

    })

    .then(response => response.json())

    .then(data => {

        if (data.total_items !== undefined) {

            setCartBadge(data.total_items);

        }

        return data;

    });

}

// =========================================
// Click Event
// =========================================

document.addEventListener("click", function (e) {

    const btn = e.target.closest(".cart-btn");

    if (!btn) return;

    e.preventDefault();

    const productId = btn.dataset.productId;

    console.log("Product:", productId);

    addToCart(productId)

    .then(data => {

        if (data.success) {

            alert("Product added to cart!");

        }

        else {

            alert(data.message || "Unable to add product.");

        }

    })

    .catch(error => {

        console.error(error);

        alert("Something went wrong!");

    });

});

// =========================================
// Page Load
// =========================================

document.addEventListener("DOMContentLoaded", function () {

    updateCartBadge();

});