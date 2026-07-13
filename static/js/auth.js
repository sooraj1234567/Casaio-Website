const container = document.getElementById("container");

const signUp = document.getElementById("signUp");

const signIn = document.getElementById("signIn");

if (signUp && container) {

    signUp.addEventListener("click", function (e) {

        e.preventDefault();

        container.classList.add("right-panel-active");

        setTimeout(function () {

            window.location.href = signUp.href;

        }, 600);

    });

}

if (signIn && container) {

    signIn.addEventListener("click", function (e) {

        e.preventDefault();

        container.classList.remove("right-panel-active");

        setTimeout(function () {

            window.location.href = signIn.href;

        }, 600);

    });

}