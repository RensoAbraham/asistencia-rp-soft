-- Init Script: Creación de tablas base para el Bot de Asistencia (lowercase)

-- Tabla de Practicantes (Usuarios)
CREATE TABLE IF NOT EXISTS practicante (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_discord BIGINT NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo VARCHAR(255) NOT NULL,
    semestre INT DEFAULT 1,
    estado VARCHAR(20) DEFAULT 'activo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Estados de Asistencia (Catálogo)
CREATE TABLE IF NOT EXISTS estado_asistencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estado VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar estados por defecto si no existen
INSERT IGNORE INTO estado_asistencia (estado) VALUES 
('Presente'),
('Tardanza'),
('Falta Injustificada'),
('Falta Recuperada'),
('Permiso');

-- Tabla de Registros de Asistencia
CREATE TABLE IF NOT EXISTS asistencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    practicante_id INT NOT NULL,
    estado_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora_entrada TIME,
    hora_salida TIME,
    observaciones TEXT,
    motivo VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (practicante_id) REFERENCES practicante(id) ON DELETE CASCADE,
    FOREIGN KEY (estado_id) REFERENCES estado_asistencia(id),
    UNIQUE KEY unique_asistencia_dia (practicante_id, fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla para almacenar las recuperaciones de asistencia
CREATE TABLE IF NOT EXISTS asistencia_recuperacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    practicante_id INT NOT NULL,
    fecha_recuperacion DATE NOT NULL,
    hora_entrada TIME NOT NULL,
    hora_salida TIME NULL,
    motivo TEXT NULL,
    estado VARCHAR(20) DEFAULT 'Pendiente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (practicante_id) REFERENCES practicante(id) ON DELETE CASCADE,
    UNIQUE KEY unique_recuperacion_dia (practicante_id, fecha_recuperacion),
    INDEX idx_practicante_fecha (practicante_id, fecha_recuperacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar usuario de prueba
INSERT IGNORE INTO practicante (id_discord, nombre, apellido, correo, semestre, estado) 
VALUES (615932763161362636, 'Usuario', 'Prueba', 'test@example.com', 1, 'activo');

INSERT IGNORE INTO practicante (id_discord, nombre, apellido, correo, semestre, estado) 
VALUES (501948181538668546, 'Joel', 'Santivañez', 'joel.test@example.com', 1, 'activo');
