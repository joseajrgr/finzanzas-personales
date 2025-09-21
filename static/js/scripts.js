function capturarSaldo() {
    fetch('/capturar_saldo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(data.mensaje);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}