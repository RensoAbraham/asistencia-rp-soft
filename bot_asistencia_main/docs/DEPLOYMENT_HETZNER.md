# 🚀 Guía de Deployment - Bot de Asistencia en Hetzner VPS

## 📋 Requisitos Previos

- ✅ Acceso SSH al VPS de Hetzner
- ✅ Usuario con permisos sudo
- ✅ Archivos del bot en tu PC local
- ✅ Archivo `.env` configurado
- ✅ Archivo `credentials.json` de Google

---

## 🔧 Paso 1: Conectarse al VPS

```bash
# Desde tu PC local (PowerShell o CMD)
ssh root@tu_ip_del_vps

# O si tienes un usuario específico
ssh usuario@tu_ip_del_vps
```

---

## 📦 Paso 2: Instalar Docker y Docker Compose

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Agregar repositorio de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Verificar instalación
docker --version

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker-compose --version

# Agregar usuario al grupo docker (opcional, para no usar sudo)
sudo usermod -aG docker $USER

# Aplicar cambios (o cerrar sesión y volver a entrar)
newgrp docker
```

---

## 📁 Paso 3: Crear Directorio del Proyecto

```bash
# Crear directorio para el bot
mkdir -p ~/bot_asistencia
cd ~/bot_asistencia
```

---

## 📤 Paso 4: Subir Archivos al VPS

### Opción A: Usando SCP (Desde tu PC local)

```powershell
# Desde PowerShell en tu PC (en el directorio del bot)
cd "C:\Users\Renso Abraham\Desktop\Rp Soft\Sala 4 6to\Bots discord\bot_asistencia_main"

# Subir todos los archivos (excepto __pycache__ y archivos temporales)
scp -r * root@tu_ip_del_vps:~/bot_asistencia/

# O si prefieres comprimir primero
tar -czf bot_asistencia.tar.gz --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' *
scp bot_asistencia.tar.gz root@tu_ip_del_vps:~/

# Luego en el VPS
ssh root@tu_ip_del_vps
cd ~/bot_asistencia
tar -xzf ~/bot_asistencia.tar.gz
```

### Opción B: Usando Git (Recomendado)

```bash
# En el VPS
cd ~/bot_asistencia

# Si tienes el código en GitHub/GitLab
git clone https://github.com/tu-usuario/bot-asistencia.git .

# O si usas un repositorio privado
git clone https://tu-token@github.com/tu-usuario/bot-asistencia.git .
```

### Opción C: Usando SFTP (FileZilla, WinSCP, etc.)

1. Abrir FileZilla/WinSCP
2. Conectar a: `sftp://tu_ip_del_vps`
3. Usuario: `root` (o tu usuario)
4. Contraseña: tu contraseña
5. Arrastrar carpeta del bot a `/root/bot_asistencia/`

---

## 🔐 Paso 5: Configurar Archivos Sensibles

```bash
# En el VPS
cd ~/bot_asistencia

# Crear archivo .env
nano .env
```

**Contenido del `.env`:**
```env
# Discord
DISCORD_TOKEN=tu_token_aqui

# Base de Datos
DB_HOST=gateway01.us-west-2.prod.aws.tidbcloud.com
DB_PORT=4000
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=asistencia_rp_soft
DB_USE_SSL=True
SSL_CA_PATH=isrgrootx1.pem

# Google Sheets
GOOGLE_SHEET_NAME=Practicantes_RP_Soft

# Backend (Opcional)
BACKEND_URL=
BACKEND_API_KEY=

# Puerto
PORT=10000
```

**Guardar:** `Ctrl + X` → `Y` → `Enter`

---

## 📝 Paso 6: Subir credentials.json

```bash
# Opción A: Crear manualmente
nano credentials.json
# Pegar el contenido del archivo
# Ctrl + X → Y → Enter

# Opción B: Desde tu PC
# En PowerShell local:
scp credentials.json root@tu_ip_del_vps:~/bot_asistencia/
```

---

## 🔒 Paso 7: Verificar Permisos

```bash
cd ~/bot_asistencia

# Verificar que los archivos existen
ls -la

# Deberías ver:
# - .env
# - credentials.json
# - docker-compose.yml
# - Dockerfile
# - bot.py
# - database.py
# - google_sheets.py
# - requirements.txt
# - etc.

# Asegurar permisos correctos
chmod 600 .env
chmod 600 credentials.json
```

---

## 🐳 Paso 8: Construir y Ejecutar el Bot

```bash
cd ~/bot_asistencia

# Construir la imagen Docker
docker-compose build

# Iniciar el bot en segundo plano
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Para salir de los logs: Ctrl + C
```

---

## 📊 Paso 9: Verificar que el Bot está Funcionando

```bash
# Ver contenedores corriendo
docker ps

# Deberías ver algo como:
# CONTAINER ID   IMAGE                                COMMAND           STATUS
# abc123def456   bot_asistencia_main-bot-asistencia   "python bot.py"   Up 2 minutes

# Ver logs del bot
docker-compose logs bot-asistencia

# Ver logs en tiempo real
docker-compose logs -f bot-asistencia

# Verificar estado del bot
docker-compose ps
```

---

## 🔄 Comandos Útiles de Mantenimiento

### Ver Logs
```bash
# Logs completos
docker-compose logs

# Últimas 100 líneas
docker-compose logs --tail=100

# Seguir logs en tiempo real
docker-compose logs -f

# Logs de las últimas 24 horas
docker-compose logs --since 24h
```

### Reiniciar el Bot
```bash
# Reinicio suave
docker-compose restart

# Reinicio completo (reconstruye)
docker-compose down
docker-compose up --build -d
```

### Detener el Bot
```bash
# Detener sin eliminar
docker-compose stop

# Detener y eliminar contenedores
docker-compose down
```

### Actualizar el Bot
```bash
cd ~/bot_asistencia

# Si usas Git
git pull origin main

# Reconstruir y reiniciar
docker-compose up --build -d

# Ver logs para verificar
docker-compose logs -f
```

### Limpiar Docker (Liberar espacio)
```bash
# Eliminar imágenes no usadas
docker image prune -a

# Eliminar volúmenes no usados
docker volume prune

# Limpieza completa
docker system prune -a --volumes
```

---

## 🔧 Troubleshooting

### Problema: Bot no inicia

```bash
# Ver logs detallados
docker-compose logs bot-asistencia

# Verificar que el .env existe
cat .env

# Verificar que credentials.json existe
cat credentials.json

# Reconstruir desde cero
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Problema: Error de conexión a base de datos

```bash
# Verificar conectividad
ping gateway01.us-west-2.prod.aws.tidbcloud.com

# Verificar que el certificado SSL existe
ls -la isrgrootx1.pem

# Si no existe, descargarlo
curl -o isrgrootx1.pem https://letsencrypt.org/certs/isrgrootx1.pem
```

### Problema: Puerto 10000 ya en uso

```bash
# Ver qué está usando el puerto
sudo lsof -i :10000

# Cambiar puerto en .env
nano .env
# Cambiar PORT=10000 a PORT=10001

# Reiniciar
docker-compose up --build -d
```

### Problema: Sin espacio en disco

```bash
# Ver espacio disponible
df -h

# Limpiar Docker
docker system prune -a --volumes

# Limpiar logs del sistema
sudo journalctl --vacuum-time=7d
```

---

## 🔐 Seguridad Adicional (Recomendado)

### Configurar Firewall

```bash
# Instalar UFW
sudo apt install ufw

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir puerto del bot (si es necesario desde afuera)
sudo ufw allow 10000/tcp

# Activar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

### Configurar Auto-reinicio

```bash
# Editar docker-compose.yml
nano docker-compose.yml
```

Agregar `restart: unless-stopped`:
```yaml
version: '3.8'

services:
  bot-asistencia:
    build: .
    container_name: bot_asistencia_main-bot-asistencia-1
    restart: unless-stopped  # ← Agregar esta línea
    env_file:
      - .env
    volumes:
      - .:/app
    ports:
      - "${PORT:-10000}:${PORT:-10000}"
```

```bash
# Aplicar cambios
docker-compose up -d
```

---

## 📱 Monitoreo (Opcional)

### Crear script de monitoreo

```bash
# Crear script
nano ~/check_bot.sh
```

**Contenido:**
```bash
#!/bin/bash

if ! docker ps | grep -q bot_asistencia; then
    echo "Bot caído, reiniciando..."
    cd ~/bot_asistencia
    docker-compose up -d
    echo "Bot reiniciado a las $(date)" >> ~/bot_restart.log
fi
```

```bash
# Dar permisos
chmod +x ~/check_bot.sh

# Agregar a crontab (ejecutar cada 5 minutos)
crontab -e

# Agregar esta línea:
*/5 * * * * /root/check_bot.sh
```

---

## 🎯 Resumen de Comandos Rápidos

```bash
# Conectar al VPS
ssh root@tu_ip_del_vps

# Ir al directorio del bot
cd ~/bot_asistencia

# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Actualizar código y reiniciar
git pull && docker-compose up --build -d

# Detener
docker-compose down

# Iniciar
docker-compose up -d
```

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `docker-compose logs -f`
2. Verifica el `.env` y `credentials.json`
3. Asegúrate de que Docker está corriendo: `docker ps`
4. Revisa la documentación técnica en `docs/DOCUMENTACION_TECNICA.md`

---

**Última actualización:** 2026-02-10
**Autor:** Equipo RP Soft
