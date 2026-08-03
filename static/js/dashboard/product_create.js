const galleryInput = document.getElementById("gallery_images");
const preview = document.getElementById("gallery-preview");

if (galleryInput) {

    galleryInput.addEventListener("change", function () {

        preview.innerHTML = "";

        [...this.files].forEach(file => {

            const reader = new FileReader();

            reader.onload = function (e) {

                const img = document.createElement("img");

                img.src = e.target.result;

                preview.appendChild(img);

            };

            reader.readAsDataURL(file);

        });

    });

}