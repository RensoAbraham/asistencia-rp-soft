-- Init Script: Creación de tablas base para el Bot de Asistencia

-- Tabla de Practicantes (Usuarios)
CREATE TABLE IF NOT EXISTS Practicante (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_discord BIGINT NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    rol VARCHAR(50) DEFAULT 'Practicante',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de Estados de Asistencia (Catálogo)
CREATE TABLE IF NOT EXISTS Estado_Asistencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estado VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar estados por defecto si no existen
INSERT IGNORE INTO Estado_Asistencia (estado) VALUES 
('Presente'),
('Tardanza'),
('Falta Injustificada'),
('Falta Recuperada'),
('Permiso');

-- Tabla de Registros de Asistencia
CREATE TABLE IF NOT EXISTS Asistencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    practicante_id INT NOT NULL,
    estado_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora_entrada TIME,
    hora_salida TIME,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (practicante_id) REFERENCES Practicante(id) ON DELETE CASCADE,
    FOREIGN KEY (estado_id) REFERENCES Estado_Asistencia(id),
    UNIQUE KEY unique_asistencia_dia (practicante_id, fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
