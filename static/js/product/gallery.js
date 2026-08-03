function changeImage(img){

    const main=document.getElementById("mainImage");

    main.src=img.src;

    document.querySelectorAll(".thumb").forEach(t=>{

        t.classList.remove("active");

    });

    img.classList.add("active");

}

function increaseQty(){

    let qty=document.getElementById("qty");

    qty.value=parseInt(qty.value)+1;

}

function decreaseQty(){

    let qty=document.getElementById("qty");

    if(parseInt(qty.value)>1){

        qty.value=parseInt(qty.value)-1;

    }

}