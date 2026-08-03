document.addEventListener("DOMContentLoaded", function () {

    console.log("Wishlist JS Loaded");

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

    const csrftoken = getCookie("csrftoken");

    /* -----------------------------
        PRODUCT PAGE WISHLIST
    ------------------------------ */

    document.addEventListener("click", function (e) {

        const btn = e.target.closest(".wishlist-btn");

        if (!btn) return;

        e.preventDefault();

        const productId = btn.dataset.productId;

        fetch(`/wishlist/toggle/${productId}/`, {

            method: "POST",

            headers: {
                "X-CSRFToken": csrftoken
            }

        })

        .then(response => response.json())

        .then(data => {

            if (data.success) {

                const icon = btn.querySelector("i");

                if (data.action === "added") {

                    icon.classList.remove("far");
                    icon.classList.add("fas", "text-danger");

                } else {

                    icon.classList.remove("fas", "text-danger");
                    icon.classList.add("far");

                }

                const badge = document.getElementById("wishlistBadge");

                if (badge) {

                    badge.textContent = data.wishlist_count;

                    if (data.wishlist_count > 0) {

                        badge.style.display = "inline-block";

                    } else {

                        badge.style.display = "none";

                    }

                }

            }

        })

        .catch(error => console.error(error));

    });

    /* -----------------------------
       REMOVE FROM WISHLIST
    ------------------------------ */

    document.addEventListener("click", function (e) {

        const btn = e.target.closest(".remove-wishlist-btn");

        if (!btn) return;

        e.preventDefault();

        const productId = btn.dataset.productId;

        fetch(`/wishlist/toggle/${productId}/`, {

            method: "POST",

            headers: {
                "X-CSRFToken": csrftoken
            }

        })

        .then(response => response.json())

        .then(data => {

            if (data.success) {

                const card = document.getElementById(
                    `wishlist-item-${productId}`
                );

                if (card) {

                    card.remove();

                }

                const badge = document.getElementById("wishlistBadge");

                if (badge) {

                    if (data.wishlist_count > 0) {

                        badge.innerHTML = data.wishlist_count;
                        badge.style.display = "inline";

                    }

                    else {

                        badge.style.display = "none";

                    }

                }

            }

        })

        .catch(error => {

            console.error(error);

        });

    });

    /* -----------------------------
       MOVE TO CART
    ------------------------------ */

    document.addEventListener("click", function (e) {

        const btn = e.target.closest(".move-to-cart-btn");

        if (!btn) return;

        e.preventDefault();

        const productId = btn.dataset.productId;

        fetch(`/wishlist/move_to_cart/${productId}/`, {

            method: "POST",

            headers: {
                "X-CSRFToken": csrftoken
            }

        })

        .then(response => response.json())

        .then(data => {

            if (data.success) {

                const card = document.getElementById(
                    `wishlist-item-${productId}`
                );

                if (card) {

                    card.remove();

                }

                const wishlistBadge =
                    document.getElementById("wishlistBadge");

                if (wishlistBadge) {

                    if (data.wishlist_count > 0) {

                        wishlistBadge.innerHTML =
                            data.wishlist_count;

                        wishlistBadge.style.display =
                            "inline";

                    }

                    else {

                        wishlistBadge.style.display =
                            "none";

                    }

                }

                const cartBadge =
                    document.getElementById("cartBadge");

                if (cartBadge) {

                    cartBadge.innerHTML =
                        data.cart_count;

                    cartBadge.style.display =
                        "inline";

                }

            }

        })

        .catch(error => {

            console.error(error);

        });

    });

});