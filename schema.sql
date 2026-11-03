-- 1. Creación de tablas
CREATE TABLE ROLES (
    id_rol NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(50) NOT NULL UNIQUE
);

CREATE TABLE USUARIOS (
    id_usuario NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR2(100) NOT NULL,
    email VARCHAR2(100) NOT NULL UNIQUE,
    password_hash VARCHAR2(255) NOT NULL,
    id_rol NUMBER NOT NULL,
    CONSTRAINT fk_usuario_rol FOREIGN KEY (id_rol) REFERENCES ROLES(id_rol)
);

CREATE TABLE PRODUCTOS (
    id_producto NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_barras VARCHAR2(50) NOT NULL UNIQUE,
    nombre VARCHAR2(100) NOT NULL,
    precio NUMBER(10, 2) NOT NULL CONSTRAINT chk_precio_pos CHECK (precio >= 0),
    stock NUMBER NOT NULL CONSTRAINT chk_stock_pos CHECK (stock >= 0),
    stock_minimo NUMBER DEFAULT 5 CONSTRAINT chk_stock_min_pos CHECK (stock_minimo >= 0),
    activo NUMBER(1) DEFAULT 1 NOT NULL CONSTRAINT chk_activo CHECK (activo IN (0, 1))
);

CREATE TABLE VENTAS (
    id_venta NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario NUMBER NOT NULL,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    total NUMBER(10, 2) NOT NULL CONSTRAINT chk_total_pos CHECK (total >= 0),
    CONSTRAINT fk_venta_usuario FOREIGN KEY (id_usuario) REFERENCES USUARIOS(id_usuario)
);

CREATE TABLE DETALLE_VENTAS (
    id_detalle NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_venta NUMBER NOT NULL,
    id_producto NUMBER NOT NULL,
    cantidad NUMBER NOT NULL CONSTRAINT chk_cant_pos CHECK (cantidad > 0),
    precio_unitario NUMBER(10, 2) NOT NULL,
    subtotal NUMBER(10, 2) NOT NULL,
    CONSTRAINT fk_detalle_venta FOREIGN KEY (id_venta) REFERENCES VENTAS(id_venta),
    CONSTRAINT fk_detalle_producto FOREIGN KEY (id_producto) REFERENCES PRODUCTOS(id_producto)
);

-- 2. Inserción de datos iniciales
INSERT INTO ROLES (nombre) VALUES ('Administrador');
INSERT INTO ROLES (nombre) VALUES ('Vendedor');

INSERT INTO USUARIOS (nombre, email, password_hash, id_rol) 
VALUES ('Administrador Sistema', 'admin@local.cl', 'pendiente', 1);

INSERT INTO USUARIOS (nombre, email, password_hash, id_rol) 
VALUES ('Vendedor Uno', 'vendedor@local.cl', 'pendiente', 2);

INSERT INTO PRODUCTOS (codigo_barras, nombre, precio, stock, stock_minimo, activo) VALUES ('780123456789', 'Teclado Mecánico RGB', 45000, 15, 5, 1);
INSERT INTO PRODUCTOS (codigo_barras, nombre, precio, stock, stock_minimo, activo) VALUES ('780987654321', 'Mouse Inalámbrico', 18500, 2, 5, 1);
INSERT INTO PRODUCTOS (codigo_barras, nombre, precio, stock, stock_minimo, activo) VALUES ('780456789012', 'Audífonos Gamer 7.1', 32000, 8, 5, 1);

COMMIT;