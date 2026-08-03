document.addEventListener("DOMContentLoaded", function () {

    const stars = document.querySelectorAll(".star");

    const ratingInput =
        document.getElementById("id_rating");

    if (!stars.length || !ratingInput) return;

    stars.forEach(star => {

        star.addEventListener("click", function () {

            const value =
                this.dataset.rating;

            ratingInput.value = value;

            stars.forEach(s => {

                if (s.dataset.rating <= value) {

                    s.classList.remove("far");
                    s.classList.add("fas");
                    s.classList.add("active");

                }

                else {

                    s.classList.remove("fas");
                    s.classList.remove("active");
                    s.classList.add("far");

                }

            });

        });

    });

});