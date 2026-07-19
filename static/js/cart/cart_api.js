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
// Add To Cart API
// =========================================

function addToCart(productId) {

    return fetch(`/cart/add/${productId}/`, {

        method: "POST",

        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
        }

    }).then(response => response.json());

}

// =========================================
// Get Cart API
// =========================================

function getCart() {

    return fetch("/cart/data/")

        .then(response => response.json());

}

function removeCartItem(itemId) {

    return fetch(`/cart/remove/${itemId}/`, {

        method: "POST",

        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
        }

    })

    .then(response => response.json());

}

function updateCartQuantity(itemId, action) {

    const formData = new FormData();

    formData.append("action", action);

    return fetch(`/cart/update/${itemId}/`, {

        method: "POST",

        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
        },

        body: formData

    })

    .then(response => response.json());

}