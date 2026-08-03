const imageInput = document.getElementById("id_image");
const preview = document.getElementById("image-preview");

if (imageInput) {

    imageInput.addEventListener("change", function () {

        preview.innerHTML = "";

        if (!this.files.length) return;

        const reader = new FileReader();

        reader.onload = function (e) {

            const img = document.createElement("img");

            img.src = e.target.result;

            img.className = "preview-image";

            preview.appendChild(img);

        };

        reader.readAsDataURL(this.files[0]);

    });

}