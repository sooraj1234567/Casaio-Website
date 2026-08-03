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

function addToCart(productId) {

    return fetch(`/cart/add/${productId}/`, {

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