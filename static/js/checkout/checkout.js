document
.getElementById("saveAddressBtn")
.addEventListener("click", function () {

    const form = document.getElementById("addressForm");

    const formData = new FormData(form);

    const addressId = document.getElementById("addressId").value;

    const url = addressId ? `/checkout/edit-address/${addressId}/` : "/checkout/save-address/";

    fetch(url, {

        method: "POST",

        body: formData,

        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }

    })

    .then(response => response.json())

    .then(data => {

        if (data.success) {

            form.reset();

            const model = new bootstrap.Modal(document.getElementById("addressModal"));

            model.hide();

            location.reload();

        }

        else{

            console.log(data.errors);

        }

    })

    .catch(error => console.log(error));

});

document.addEventListener("click", function (e) {

    const btn = e.target.closest(".delete-address");

    if (!btn) return;

    if (!confirm("Delete this address?")) return;

    fetch(`/checkout/delete-address/${btn.dataset.id}/`, {

        method: "POST",

        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }

    })

    .then(response => response.json())

    .then(data => {

        if (data.success){

            location.reload();

        }

    });

});

document.addEventListener("click", function (e) {

    const btn = e.target.closest(".edit-address");

    if (!btn) return;

    fetch(`/checkout/edit-address/${btn.dataset.id}/`)

    .then(response => response.json())

    .then(data => {

        document.getElementById("addressId").value = data.id;

        document.getElementById("id_full_name").value = data.full_name;
        document.getElementById("id_phone_number").value = data.phone_number;
        document.getElementById("id_house_name").value = data.house_name;
        document.getElementById("id_area").value = data.area;
        document.getElementById("id_city").value = data.city;
        document.getElementById("id_state").value = data.state;
        document.getElementById("id_pincode").value = data.pincode;

        new bootstrap.Modal(
            document.getElementById("addressModal")
        ).show();

    });

});

document.addEventListener("click", function (e) {

    const btn = e.target.closest(".set-default-address");

    if (!btn) return;

    fetch(`/checkout/set-default/${btn.dataset.id}/`, {

        method: "POST",

        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }

    })

    .then(response => response.json())

    .then(data => {

        if (data.success){

            location.reload();

        }

    });

});

document.querySelectorAll('input[name="paymentMethod"]').forEach(radio => {

    radio.addEventListener("change", function () {

        document.getElementById("selectedPaymentMethod").value = this.value;

    });

});