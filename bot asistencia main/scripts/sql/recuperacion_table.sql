-- Tabla para almacenar las recuperaciones de asistencia
CREATE TABLE IF NOT EXISTS Recuperacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    practicante_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora_entrada TIME NOT NULL,
    hora_salida TIME NULL,
    motivo TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (practicante_id) REFERENCES Practicante(id) ON DELETE CASCADE,
    UNIQUE KEY unique_recuperacion_dia (practicante_id, fecha),
    INDEX idx_practicante_fecha (practicante_id, fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

