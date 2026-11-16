# Sistema de Inventario y Ventas

Aplicación web para gestionar el inventario y las ventas de un negocio pequeño, con control de stock en tiempo real y roles de usuario. Proyecto de portafolio hecho con Flask y Oracle Database.

![Panel principal](docs/dashboard.png)

## Funciones

- **Autenticación y roles:** inicio de sesión con contraseñas cifradas (`werkzeug.security`) y dos roles: Administrador y Vendedor.
- **Ventas con stock seguro:** el descuento se hace en una sola sentencia (`UPDATE ... WHERE stock >= :cant`), por lo que el stock nunca queda negativo, aunque dos personas vendan al mismo tiempo.
- **Gestión de productos:** agregar productos o sumar stock cuando el código de barras ya existe, y desactivar productos sin perder el historial de ventas.
- **Alerta de poco stock** en el catálogo.
- **Reporte de ventas en CSV** con filtro por fechas, compatible con Excel (UTF-8 con BOM).
- **Seguridad:** protección CSRF (Flask-WTF), consultas parametrizadas, secretos en variables de entorno y mensajes de error genéricos para el usuario (el detalle queda en el registro del servidor).

## Capturas

| Inicio de sesión | Registrar una venta |
| --- | --- |
| ![Login](docs/login.png) | ![Venta](docs/venta.png) |

## Tecnologías

- Python 3 y Flask
- Oracle Database con `python-oracledb` (modo Thin: no requiere instalar Oracle Client)
- Flask-WTF (CSRF) y Werkzeug (hash de contraseñas)
- HTML5, CSS3 y JavaScript

## Estructura del proyecto

```
sistema-inventario-flask/
├── app.py              # rutas y lógica de negocio
├── db.py               # conexión a Oracle
├── seed.py             # crea las claves de demostración
├── schema.sql          # tablas y datos iniciales
├── requirements.txt
├── .env.example        # plantilla de variables de entorno
├── templates/          # login.html y dashboard.html
└── static/             # styles.css y main.js
```

**Modelo de datos:** `roles`, `usuarios`, `productos`, `ventas` y `detalle_ventas`, con llaves foráneas y restricciones `CHECK` (precio y stock no negativos).

## Instalación local

1. Clona el repositorio y crea un entorno virtual:

   ```bash
   git clone https://github.com/claudiopizarro12313/sistema-inventario-flask.git
   cd sistema-inventario-flask
   python -m venv venv
   venv\Scripts\activate
   ```

   En Mac o Linux, el último comando es `source venv/bin/activate`.

2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Prepara la base de datos. Conéctate a tu base como administrador (en Oracle XE, a la base pluggable `XEPDB1`) y crea un usuario para el proyecto:

   ```sql
   CREATE USER inventario IDENTIFIED BY "tu_clave" QUOTA UNLIMITED ON USERS;
   GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE, CREATE VIEW TO inventario;
   ```

   Luego, conectado con ese usuario, ejecuta `schema.sql`.

4. Configura las variables de entorno. Copia `.env.example` a `.env` y completa los valores:

   ```
   FLASK_SECRET_KEY=una_clave_larga_y_aleatoria
   DB_USER=inventario
   DB_PASSWORD=tu_clave
   DB_DSN=localhost:1521/XEPDB1
   ```

   Para generar una clave secreta:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. Crea las claves de los usuarios de demostración:

   ```bash
   python seed.py
   ```

6. Inicia la aplicación y abre http://127.0.0.1:5000 en el navegador:

   ```bash
   python app.py
   ```

## Usuarios de demostración

Solo para pruebas en un entorno local:

| Rol | Correo | Contraseña |
| --- | --- | --- |
| Administrador | `admin@local.cl` | `admin123` |
| Vendedor | `vendedor@local.cl` | `vendedor123` |

## Limitaciones y próximos pasos

- Cada venta registra un solo producto.
- Falta editar productos y ver el historial de ventas en pantalla.
- Pendientes: límite de intentos de inicio de sesión y pruebas automáticas con `pytest`.

## Autor

Claudio Pizarro, analista programador. [Portafolio y GitHub](https://github.com/claudiopizarro12313)
