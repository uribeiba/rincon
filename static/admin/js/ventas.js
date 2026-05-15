document.addEventListener('DOMContentLoaded', function () {

    const efectivo = document.getElementById('id_efectivo');
    const debito = document.getElementById('id_debito');
    const transferencia = document.getElementById('id_transferencia');
    const credito = document.getElementById('id_credito');
    const total = document.getElementById('id_total');

    function calcularTotal() {

        const v1 = parseInt(efectivo.value) || 0;
        const v2 = parseInt(debito.value) || 0;
        const v3 = parseInt(transferencia.value) || 0;
        const v4 = parseInt(credito.value) || 0;

        const suma = v1 + v2 + v3 + v4;

        total.value = suma;
    }

    calcularTotal();

    efectivo.addEventListener('input', calcularTotal);
    debito.addEventListener('input', calcularTotal);
    transferencia.addEventListener('input', calcularTotal);
    credito.addEventListener('input', calcularTotal);

});