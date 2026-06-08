-- ==========================================================
-- TECHSTORE 360 - SUPABASE POSTGRESQL
-- Usuarios - Productos - Compras
-- ==========================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ==========================================================
-- USUARIOS
-- ==========================================================

CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(255) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('ADMIN','CLIENTE')),
    telefono VARCHAR(20),
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_usuario_email ON usuarios(email);

-- ==========================================================
-- PRODUCTOS
-- ==========================================================

CREATE TABLE productos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    precio NUMERIC(10,2) NOT NULL CHECK (precio > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    imagen_url TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_producto_nombre ON productos(nombre);

-- ==========================================================
-- COMPRAS
-- ==========================================================

CREATE TABLE compras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    fecha_compra TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    subtotal NUMERIC(12,2) NOT NULL DEFAULT 0,
    iva NUMERIC(12,2) NOT NULL DEFAULT 0,
    total NUMERIC(12,2) NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE'
        CHECK (estado IN ('PENDIENTE','PAGADA','FACTURADA','CANCELADA')),
    factura_xml TEXT,
    clave_acceso VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_compra_usuario ON compras(usuario_id);

-- ==========================================================
-- DETALLE COMPRA
-- ==========================================================

CREATE TABLE detalle_compra (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compra_id UUID NOT NULL REFERENCES compras(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario > 0),
    subtotal NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0)
);

CREATE INDEX idx_detalle_compra ON detalle_compra(compra_id);
CREATE INDEX idx_detalle_producto ON detalle_compra(producto_id);

-- ==========================================================
-- DATOS INICIALES
-- ==========================================================

INSERT INTO productos (nombre, descripcion, precio, stock)
VALUES
('Laptop Lenovo', 'Laptop Ryzen 7', 850.00, 20),
('Mouse Logitech', 'Mouse inalámbrico', 25.50, 100),
('Teclado Mecánico', 'RGB Switch Blue', 65.00, 50);

-- ==========================================================
-- ACTUALIZACIONES / MIGRACIONES
-- ==========================================================

ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS cedula VARCHAR(20) UNIQUE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS eliminado BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE productos ADD COLUMN IF NOT EXISTS eliminado BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE compras ADD COLUMN IF NOT EXISTS eliminado BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE compras ADD COLUMN IF NOT EXISTS direccion_origen VARCHAR(255);
ALTER TABLE compras ADD COLUMN IF NOT EXISTS direccion_destino VARCHAR(255);
ALTER TABLE compras ADD COLUMN IF NOT EXISTS latitud_origen DECIMAL(10,8);
ALTER TABLE compras ADD COLUMN IF NOT EXISTS longitud_origen DECIMAL(10,8);
ALTER TABLE compras ADD COLUMN IF NOT EXISTS latitud_destino DECIMAL(10,8);
ALTER TABLE compras ADD COLUMN IF NOT EXISTS longitud_destino DECIMAL(10,8);
ALTER TABLE compras ADD COLUMN IF NOT EXISTS metodo_entrega VARCHAR(50) DEFAULT 'ENTREGA';