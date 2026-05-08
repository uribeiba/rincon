document.addEventListener("DOMContentLoaded", function () {

    const efectivo = document.getElementById("id_efectivo");
    const debito = document.getElementById("id_debito");
    const transferencia = document.getElementById("id_transferencia");
    const credito = document.getElementById("id_credito");
    const total = document.getElementById("id_total");

    function calcular() {

        let e = parseInt(efectivo.value || 0);
        let d = parseInt(debito.value || 0);
        let t = parseInt(transferencia.value || 0);
        let c = parseInt(credito.value || 0);

        total.value = e + d + t + c;
    }

    efectivo.addEventListener("keyup", calcular);
    debito.addEventListener("keyup", calcular);
    transferencia.addEventListener("keyup", calcular);
    credito.addEventListener("keyup", calcular);

});
