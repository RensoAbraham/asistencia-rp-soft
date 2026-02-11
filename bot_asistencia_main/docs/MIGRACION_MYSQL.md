# 🔄 Guía de Migración: TiDB Cloud → MySQL Local (VPS Hetzner)

## 📋 Resumen

Esta guía te ayudará a migrar tu base de datos de TiDB Cloud a MySQL local en tu VPS de Hetzner.

**Ventajas:**
- ✅ Gratis (sin costos adicionales)
- ✅ Más rápido (latencia casi 0)
- ✅ Más seguro (datos en tu servidor)
- ✅ Sin límites de almacenamiento
- ✅ Control total sobre backups

---

## 🎯 Opción 1: MySQL con Docker (Recomendado)

### Paso 1: Modificar docker-compose.yml

```yaml
version: '3.8'

services:
  # Base de datos MySQL
  mysql:
    image: mysql:8.0
    container_name: bot_asistencia_mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: tu_contraseña_root_segura
      MYSQL_DATABASE: asistencia_rp_soft
      MYSQL_USER: bot_user
      MYSQL_PASSWORD: tu_contraseña_bot_segura
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    networks:
      - bot_network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

  # Bot de Discord
  bot-asistencia:
    build: .
    container_name: bot_asistencia_main
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - .:/app
    ports:
      - "${PORT:-10000}:${PORT:-10000}"
    depends_on:
      mysql:
        condition: service_healthy
    networks:
      - bot_network

volumes:
  mysql_data:

networks:
  bot_network:
    driver: bridge
```

### Paso 2: Actualizar archivo .env

```env
# Discord
DISCORD_TOKEN=tu_token_aqui

# Base de Datos LOCAL (MySQL en Docker)
DB_HOST=mysql
DB_PORT=3306
DB_USER=bot_user
DB_PASSWORD=tu_contraseña_bot_segura
DB_NAME=asistencia_rp_soft
DB_USE_SSL=False
# SSL_CA_PATH=  # Ya no necesario

# Google Sheets
GOOGLE_SHEET_NAME=Practicantes_RP_Soft

# Backend (Opcional)
BACKEND_URL=
BACKEND_API_KEY=

# Puerto
PORT=10000
```

### Paso 3: Modificar database.py

```python
# database.py - Líneas 14-32

def get_ssl_context():
    # Ya no necesitamos SSL para conexión local
    if os.getenv("DB_USE_SSL") == "True":
        ctx = ssl.create_default_context(cafile=os.getenv("SSL_CA_PATH", "isrgrootx1.pem"))
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx
    return None

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "db": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306)),  # Cambiar de 4000 a 3306
    "autocommit": False,
    "ssl": get_ssl_context()
}
```

### Paso 4: Exportar datos de TiDB (Opcional - si ya tienes datos)

```bash
# Desde tu PC local o VPS
# Instalar cliente MySQL
sudo apt install mysql-client

# Exportar datos de TiDB
mysqldump -h gateway01.us-west-2.prod.aws.tidbcloud.com \
  -P 4000 \
  -u tu_usuario \
  -p \
  --ssl-ca=isrgrootx1.pem \
  asistencia_rp_soft > backup_tidb.sql

# Subir al VPS
scp backup_tidb.sql root@tu_ip_vps:~/bot_asistencia/
```

### Paso 5: Iniciar servicios

```bash
cd ~/bot_asistencia

# Detener servicios actuales (si están corriendo)
docker-compose down

# Iniciar MySQL y Bot
docker-compose up -d

# Ver logs
docker-compose logs -f

# Esperar a que MySQL esté listo (verás "ready for connections")
```

### Paso 6: Importar datos (si hiciste backup)

```bash
# Esperar a que MySQL esté completamente iniciado
docker-compose logs mysql | grep "ready for connections"

# Importar datos
docker exec -i bot_asistencia_mysql mysql -ubot_user -ptu_contraseña_bot_segura asistencia_rp_soft < backup_tidb.sql

# Verificar que se importó
docker exec -it bot_asistencia_mysql mysql -ubot_user -ptu_contraseña_bot_segura asistencia_rp_soft -e "SHOW TABLES;"
```

### Paso 7: Verificar funcionamiento

```bash
# Ver logs del bot
docker-compose logs -f bot-asistencia

# Deberías ver:
# "Verificando y configurando base de datos..."
# "Base de datos inicializada Correctamente"
# "✅ Bot conectado y listo como..."
```

---

## 🎯 Opción 2: MySQL Instalado Directamente en el VPS

Si prefieres NO usar Docker para MySQL:

### Paso 1: Instalar MySQL

```bash
# Actualizar sistema
sudo apt update

# Instalar MySQL Server
sudo apt install mysql-server -y

# Iniciar MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Configuración segura
sudo mysql_secure_installation
```

Responder:
- **VALIDATE PASSWORD COMPONENT**: No (o Yes si quieres)
- **Remove anonymous users**: Yes
- **Disallow root login remotely**: Yes
- **Remove test database**: Yes
- **Reload privilege tables**: Yes

### Paso 2: Crear base de datos y usuario

```bash
# Entrar a MySQL
sudo mysql

# En el prompt de MySQL:
```

```sql
-- Crear base de datos
CREATE DATABASE asistencia_rp_soft CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario
CREATE USER 'bot_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';

-- Dar permisos
GRANT ALL PRIVILEGES ON asistencia_rp_soft.* TO 'bot_user'@'localhost';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Salir
EXIT;
```

### Paso 3: Actualizar .env

```env
# Base de Datos LOCAL (MySQL instalado en VPS)
DB_HOST=localhost
DB_PORT=3306
DB_USER=bot_user
DB_PASSWORD=tu_contraseña_segura
DB_NAME=asistencia_rp_soft
DB_USE_SSL=False
```

### Paso 4: Modificar docker-compose.yml

```yaml
version: '3.8'

services:
  bot-asistencia:
    build: .
    container_name: bot_asistencia_main
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - .:/app
    ports:
      - "${PORT:-10000}:${PORT:-10000}"
    network_mode: "host"  # Para acceder a MySQL en localhost
```

### Paso 5: Importar datos (si tienes backup)

```bash
# Importar desde archivo SQL
mysql -ubot_user -p asistencia_rp_soft < backup_tidb.sql
```

---

## 📊 Comparación de Opciones

| Característica | MySQL con Docker | MySQL Instalado |
|----------------|------------------|-----------------|
| **Facilidad** | ⭐⭐⭐⭐⭐ Muy fácil | ⭐⭐⭐ Moderado |
| **Aislamiento** | ✅ Contenedor separado | ❌ Instalado en sistema |
| **Backups** | ✅ Volúmenes Docker | ⚠️ Manual |
| **Portabilidad** | ✅ Fácil mover | ❌ Difícil |
| **Recursos** | ⚠️ Usa más RAM | ✅ Más eficiente |
| **Mantenimiento** | ✅ Fácil actualizar | ⚠️ Más complejo |

**Recomendación:** **MySQL con Docker** (Opción 1)

---

## 🔐 Backups Automáticos

### Script de Backup

```bash
# Crear script
nano ~/backup_bot.sh
```

**Contenido:**
```bash
#!/bin/bash

# Configuración
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
MYSQL_CONTAINER="bot_asistencia_mysql"
DB_NAME="asistencia_rp_soft"
DB_USER="bot_user"
DB_PASS="tu_contraseña_bot_segura"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup de base de datos
docker exec $MYSQL_CONTAINER mysqldump -u$DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Comprimir
gzip $BACKUP_DIR/backup_$DATE.sql

# Eliminar backups antiguos (más de 7 días)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completado: backup_$DATE.sql.gz"
```

```bash
# Dar permisos
chmod +x ~/backup_bot.sh

# Probar
~/backup_bot.sh

# Programar backup diario a las 3 AM
crontab -e

# Agregar:
0 3 * * * /root/backup_bot.sh >> /root/backup.log 2>&1
```

---

## 🔄 Proceso de Migración Completo (Paso a Paso)

### 1. Preparación
```bash
# Conectar al VPS
ssh root@tu_ip_vps

# Ir al directorio del bot
cd ~/bot_asistencia

# Hacer backup del .env actual
cp .env .env.backup
```

### 2. Exportar datos de TiDB (si tienes datos)
```bash
# Desde tu PC o VPS
mysqldump -h gateway01.us-west-2.prod.aws.tidbcloud.com \
  -P 4000 \
  -u tu_usuario \
  -p \
  --ssl-ca=isrgrootx1.pem \
  asistencia_rp_soft > backup_tidb.sql

# Subir al VPS
scp backup_tidb.sql root@tu_ip_vps:~/bot_asistencia/
```

### 3. Detener bot actual
```bash
cd ~/bot_asistencia
docker-compose down
```

### 4. Actualizar archivos
```bash
# Actualizar docker-compose.yml (usar Opción 1 de arriba)
nano docker-compose.yml

# Actualizar .env
nano .env

# Actualizar database.py (cambiar puerto 4000 a 3306)
nano database.py
```

### 5. Iniciar servicios
```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 6. Importar datos
```bash
# Esperar a que MySQL esté listo
sleep 30

# Importar
docker exec -i bot_asistencia_mysql mysql -ubot_user -ptu_contraseña asistencia_rp_soft < backup_tidb.sql
```

### 7. Verificar
```bash
# Ver logs del bot
docker-compose logs bot-asistencia

# Probar comandos en Discord
# /estado, /entrada, etc.
```

---

## ✅ Checklist de Migración

- [ ] Exportar datos de TiDB
- [ ] Actualizar docker-compose.yml
- [ ] Actualizar .env (DB_HOST, DB_PORT, DB_USE_SSL)
- [ ] Actualizar database.py (puerto 3306)
- [ ] Detener servicios actuales
- [ ] Iniciar MySQL y Bot
- [ ] Importar datos
- [ ] Verificar funcionamiento
- [ ] Configurar backups automáticos
- [ ] Eliminar credenciales de TiDB del .env

---

## 🆘 Troubleshooting

### Error: "Can't connect to MySQL server"

```bash
# Verificar que MySQL está corriendo
docker ps | grep mysql

# Ver logs de MySQL
docker-compose logs mysql

# Verificar red
docker network ls
docker network inspect bot_asistencia_bot_network
```

### Error: "Access denied for user"

```bash
# Verificar credenciales en .env
cat .env | grep DB_

# Recrear usuario en MySQL
docker exec -it bot_asistencia_mysql mysql -uroot -p

# En MySQL:
DROP USER 'bot_user'@'%';
CREATE USER 'bot_user'@'%' IDENTIFIED BY 'nueva_contraseña';
GRANT ALL PRIVILEGES ON asistencia_rp_soft.* TO 'bot_user'@'%';
FLUSH PRIVILEGES;
```

### Bot no inicia después de migración

```bash
# Ver logs detallados
docker-compose logs -f bot-asistencia

# Verificar que database.py tiene el puerto correcto
grep "DB_PORT" database.py

# Reconstruir imagen
docker-compose build --no-cache
docker-compose up -d
```

---

## 📝 Notas Finales

1. **Guarda las credenciales de TiDB** por si acaso, pero ya no las necesitarás
2. **Configura backups automáticos** desde el primer día
3. **Monitorea el uso de disco** con `df -h`
4. **MySQL con Docker es más fácil de mantener** que instalado directamente

---

**¿Necesitas ayuda con la migración?** Puedo guiarte paso a paso.
