-- Init Script: Creación de tablas base para el Bot de Asistencia (lowercase)

-- Tabla de Practicantes (Usuarios) - ESQUEMA SIMPLIFICADO
CREATE TABLE IF NOT EXISTS practicante (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_discord BIGINT NOT NULL UNIQUE,
    nombre_completo VARCHAR(255) NOT NULL,
    horas_base TIME DEFAULT '00:00:00'
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
    FOREIGN KEY (practicante_id) REFERENCES practicante(id) ON DELETE CASCADE,
    UNIQUE KEY unique_recuperacion_dia (practicante_id, fecha_recuperacion),
    INDEX idx_practicante_fecha (practicante_id, fecha_recuperacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
