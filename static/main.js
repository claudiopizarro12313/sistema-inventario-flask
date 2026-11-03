document.addEventListener('DOMContentLoaded', () => {
    // 4. Selector corregido para coincidir con la ruta /procesar_venta
    const formVenta = document.querySelector('form[action="/procesar_venta"]');
    if (formVenta) {
        formVenta.addEventListener('submit', (e) => {
            const selectProducto = formVenta.querySelector('select[name="id_producto"]');
            const inputCantidad = formVenta.querySelector('input[name="cantidad"]');
            
            if (!selectProducto.value) {
                e.preventDefault();
                alert('Por favor, selecciona un producto.');
                return;
            }
            
            if (parseInt(inputCantidad.value) < 1) {
                e.preventDefault();
                alert('La cantidad debe ser mayor o igual a 1.');
                return;
            }
        });
    }

    // Selector corregido para la confirmación de desactivación
    const formsDesactivar = document.querySelectorAll('.form-desactivar');
    formsDesactivar.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!confirm('¿Estás seguro de que deseas desactivar este producto del catálogo?')) {
                e.preventDefault();
            }
        });
    });
});