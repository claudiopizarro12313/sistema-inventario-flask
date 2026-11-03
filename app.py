import os
import csv
import io
import oracledb  # 1. Importado para usar oracledb.NUMBER en las ventas
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from db import conexion

load_dotenv()

app = Flask(__name__)

# Clave secreta estricta desde el archivo .env
app.secret_key = os.environ["FLASK_SECRET_KEY"]

# Protección CSRF para formularios
csrf = CSRFProtect(app)

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        try:
            with conexion() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT u.id_usuario, u.nombre, u.password_hash, r.nombre AS rol 
                    FROM usuarios u 
                    JOIN roles r ON u.id_rol = r.id_rol 
                    WHERE u.email = :email
                """
                cursor.execute(query, {'email': email})
                usuario = cursor.fetchone()
                
                if usuario and check_password_hash(usuario[2], password):
                    session.clear()
                    session['usuario_id'] = usuario[0]
                    session['usuario'] = usuario[1]
                    session['rol'] = usuario[3]
                    flash(f'¡Bienvenido de nuevo, {usuario[1]}!', 'success')
                    return redirect(url_for('dashboard'))
                
                flash('Credenciales incorrectas. Intenta de nuevo.', 'danger')
        except Exception:
            app.logger.exception("Error en el proceso de Login")
            flash('Ocurrió un error al intentar iniciar sesión.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    try:
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_producto, codigo_barras, nombre, precio, stock, stock_minimo, activo 
                FROM productos 
                WHERE activo = 1 
                ORDER BY id_producto DESC
            """)
            productos = cursor.fetchall()
            
            return render_template(
                'dashboard.html', 
                productos=productos,
                usuario=session.get('usuario', 'Usuario'),
                rol=session.get('rol', 'Vendedor')
            )
    except Exception:
        app.logger.exception("Error al cargar el Dashboard")
        flash('Error al consultar los productos en la base de datos.', 'danger')
        return render_template(
            'dashboard.html', 
            productos=[],
            usuario=session.get('usuario', 'Usuario'),
            rol=session.get('rol', 'Vendedor')
        )

@app.route('/crear_producto', methods=['POST'])
def crear_producto():
    if 'usuario_id' not in session or session.get('rol') != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('dashboard'))
        
    codigo = request.form.get('codigo', '').strip()
    nombre = request.form.get('nombre', '').strip()
    precio = request.form.get('precio', type=float)
    stock = request.form.get('stock', type=int)
    stock_minimo = request.form.get('stock_minimo', type=int, default=5)
    
    # Detalle menor: Validación previa de campos requeridos
    if not codigo or not nombre or precio is None or stock is None or precio < 0 or stock < 1 or stock_minimo < 0:
        flash('Revisa los datos: hay valores vacíos o inválidos.', 'warning')
        return redirect(url_for('dashboard'))

    try:
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_producto, stock FROM productos WHERE codigo_barras = :1", (codigo,))
            existente = cursor.fetchone()
            
            if existente:
                nuevo_stock = existente[1] + stock
                cursor.execute("""
                    UPDATE productos 
                    SET nombre = :1, precio = :2, stock = :3, stock_minimo = :4, activo = 1 
                    WHERE id_producto = :5
                """, (nombre, precio, nuevo_stock, stock_minimo, existente[0]))
                flash(f'Stock actualizado correctamente. Nuevo stock total: {nuevo_stock}', 'success')
            else:
                cursor.execute("""
                    INSERT INTO productos (codigo_barras, nombre, precio, stock, stock_minimo, activo)
                    VALUES (:1, :2, :3, :4, :5, 1)
                """, (codigo, nombre, precio, stock, stock_minimo))
                flash('Producto nuevo agregado correctamente.', 'success')
                
            conn.commit()
    except Exception:
        app.logger.exception("Error al crear o actualizar producto")
        flash('No se pudo procesar el producto.', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/desactivar_producto/<int:id_producto>', methods=['POST'])
def desactivar_producto(id_producto):
    if 'usuario_id' not in session or session.get('rol') != 'Administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('dashboard'))
        
    try:
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE productos SET activo = 0 WHERE id_producto = :1", (id_producto,))
            conn.commit()
            
        flash('Producto desactivado del catálogo.', 'success')
    except Exception:
        app.logger.exception("Error al desactivar producto")
        flash('No se pudo desactivar el producto.', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/procesar_venta', methods=['POST'])
def procesar_venta():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    try:
        id_producto = int(request.form.get('id_producto'))
        cantidad = int(request.form.get('cantidad'))
    except (ValueError, TypeError):
        flash('Datos de venta inválidos.', 'danger')
        return redirect(url_for('dashboard'))
        
    if cantidad < 1:
        flash('La cantidad debe ser al menos 1.', 'warning')
        return redirect(url_for('dashboard'))
        
    try:
        with conexion() as conn:
            cursor = conn.cursor()
            
            # 3. Descuento atómico de stock
            cursor.execute("""
                UPDATE productos SET stock = stock - :cant
                WHERE id_producto = :id AND stock >= :cant AND activo = 1
            """, {'cant': cantidad, 'id': id_producto})
            
            if cursor.rowcount == 0:
                conn.rollback()
                flash('Stock insuficiente o el producto no está disponible.', 'warning')
                return redirect(url_for('dashboard'))
                
            cursor.execute("SELECT precio FROM productos WHERE id_producto = :1", (id_producto,))
            precio = cursor.fetchone()[0]
            total = precio * cantidad
            
            # 2. Una sola variable id_venta_var para RETURNING INTO
            id_venta_var = cursor.var(oracledb.NUMBER)
            cursor.execute("""
                INSERT INTO ventas (id_usuario, total)
                VALUES (:1, :2)
                RETURNING id_venta INTO :3
            """, (session['usuario_id'], total, id_venta_var))
            
            id_venta = int(id_venta_var.getvalue()[0])
            
            cursor.execute("""
                INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (:1, :2, :3, :4, :5)
            """, (id_venta, id_producto, cantidad, precio, total))
            
            conn.commit()
            flash('Venta realizada con éxito.', 'success')
    except Exception:
        app.logger.exception("Error al procesar la venta")
        flash('No se pudo procesar la venta.', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/reporte_ventas')
def reporte_ventas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    try:
        with conexion() as conn:
            cursor = conn.cursor()
            query = """
                SELECT v.id_venta, u.nombre AS vendedor, v.fecha_venta, v.total
                FROM ventas v
                JOIN usuarios u ON v.id_usuario = u.id_usuario
                WHERE 1=1
            """
            params = {}
            
            if fecha_inicio:
                query += " AND v.fecha_venta >= TO_DATE(:fecha_inicio, 'YYYY-MM-DD')"
                params['fecha_inicio'] = fecha_inicio
            if fecha_fin:
                # Corregido filtro 'Hasta' a menor estricto (< fecha + 1)
                query += " AND v.fecha_venta < TO_DATE(:fecha_fin, 'YYYY-MM-DD') + 1"
                params['fecha_fin'] = fecha_fin
                
            query += " ORDER BY v.fecha_venta DESC"
            cursor.execute(query, params)
            ventas = cursor.fetchall()
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID Venta', 'Vendedor', 'Fecha', 'Total ($)'])
            
            for v in ventas:
                writer.writerow([v[0], v[1], v[2].strftime('%Y-%m-%d %H:%M:%S'), f"{v[3]:.0f}"])
                
            response = Response(output.getvalue().encode('utf-8-sig'), mimetype='text/csv')
            response.headers["Content-Disposition"] = "attachment; filename=reporte_ventas.csv"
            return response
    except Exception:
        app.logger.exception("Error al generar el reporte CSV")
        flash('Error al generar el reporte de ventas.', 'danger')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)