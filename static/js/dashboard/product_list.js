const deleteModal = document.getElementById("deleteProductModal");

if (deleteModal) {

    deleteModal.addEventListener("show.bs.modal", function (event) {

        const button = event.relatedTarget;

        const productId = button.getAttribute("data-product-id");
        const productName = button.getAttribute("data-product-name");

        document.getElementById("productName").textContent = productName;

        document.getElementById("deleteProductForm").action =
            `/dashboard/products/${productId}/delete/`;

    });

}