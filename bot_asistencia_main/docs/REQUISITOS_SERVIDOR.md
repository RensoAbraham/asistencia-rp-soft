# ⚙️ Requisitos del Servidor VPS Hetzner

## 📋 Checklist de Instalación Única

Esta es la lista completa de todo lo que necesitas instalar **UNA SOLA VEZ** en el servidor VPS para todos los proyectos.

---

## 🖥️ Sistema Operativo

**Recomendado:** Ubuntu 22.04 LTS

```bash
# Verificar versión
lsb_release -a
```

---

## 📦 Software Base Requerido

### 1. Docker Engine

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verificar instalación
docker --version
# Debería mostrar: Docker version 24.x.x

# Habilitar Docker al inicio
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. Docker Compose

```bash
# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dar permisos de ejecución
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker-compose --version
# Debería mostrar: Docker Compose version v2.x.x
```

### 3. Git

```bash
# Instalar Git
sudo apt install git -y

# Verificar instalación
git --version
# Debería mostrar: git version 2.x.x

# Configurar Git (opcional)
git config --global user.name "RP Soft"
git config --global user.email "dev@rpsoft.com"
```

### 4. Herramientas de Red

```bash
# Instalar utilidades de red
sudo apt install -y curl wget net-tools

# Verificar
curl --version
wget --version
```

### 5. Editor de Texto

```bash
# Nano ya viene instalado, pero por si acaso
sudo apt install nano -y

# Verificar
nano --version
```

---

## 🔒 Seguridad

### 1. Firewall (UFW)

```bash
# Instalar UFW
sudo apt install ufw -y

# Configurar reglas básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH (IMPORTANTE: Hacer esto ANTES de activar)
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

### 2. Fail2Ban (Protección contra ataques)

```bash
# Instalar Fail2Ban
sudo apt install fail2ban -y

# Iniciar servicio
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Verificar estado
sudo systemctl status fail2ban
```

---

## 🗄️ Base de Datos (Opcional - según proyecto)

### MySQL/MariaDB (Si usas MySQL local)

```bash
# Instalar MySQL
sudo apt install mysql-server -y

# Iniciar servicio
sudo systemctl enable mysql
sudo systemctl start mysql

# Configuración segura
sudo mysql_secure_installation

# Verificar
mysql --version
```

### PostgreSQL (Si usas PostgreSQL)

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Iniciar servicio
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Verificar
psql --version
```

---

## 📊 Monitoreo (Opcional pero Recomendado)

### 1. Htop (Monitor de recursos)

```bash
# Instalar htop
sudo apt install htop -y

# Usar
htop
```

### 2. Logs del Sistema

```bash
# Ver logs del sistema
sudo journalctl -xe

# Ver logs de Docker
sudo journalctl -u docker
```

---

## 🌐 Certificados SSL (Opcional - para HTTPS)

### Certbot (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot -y

# Verificar
certbot --version
```

---

## 📁 Estructura de Directorios Recomendada

```bash
# Crear estructura de directorios
mkdir -p ~/proyectos
mkdir -p ~/backups
mkdir -p ~/scripts

# Verificar
ls -la ~/
```

---

## ✅ Verificación Final

Ejecuta este script para verificar que todo está instalado:

```bash
#!/bin/bash

echo "=== Verificación de Requisitos del Servidor ==="
echo ""

# Docker
echo -n "Docker: "
if command -v docker &> /dev/null; then
    docker --version
else
    echo "❌ NO INSTALADO"
fi

# Docker Compose
echo -n "Docker Compose: "
if command -v docker-compose &> /dev/null; then
    docker-compose --version
else
    echo "❌ NO INSTALADO"
fi

# Git
echo -n "Git: "
if command -v git &> /dev/null; then
    git --version
else
    echo "❌ NO INSTALADO"
fi

# UFW
echo -n "UFW: "
if command -v ufw &> /dev/null; then
    sudo ufw status | head -n 1
else
    echo "❌ NO INSTALADO"
fi

# MySQL (opcional)
echo -n "MySQL: "
if command -v mysql &> /dev/null; then
    mysql --version
else
    echo "⚠️ No instalado (opcional)"
fi

# PostgreSQL (opcional)
echo -n "PostgreSQL: "
if command -v psql &> /dev/null; then
    psql --version
else
    echo "⚠️ No instalado (opcional)"
fi

echo ""
echo "=== Verificación de Recursos ==="
echo ""

# Espacio en disco
echo "Espacio en disco:"
df -h / | tail -n 1

# Memoria RAM
echo ""
echo "Memoria RAM:"
free -h | grep Mem

# CPU
echo ""
echo "CPU:"
lscpu | grep "Model name"

echo ""
echo "=== Fin de Verificación ==="
```

**Guardar como:** `~/verificar_requisitos.sh`

```bash
# Dar permisos
chmod +x ~/verificar_requisitos.sh

# Ejecutar
~/verificar_requisitos.sh
```

---

## 📝 Checklist de Instalación

Marca cada item al completarlo:

### Software Base

- [X] Ubuntu 22.04 LTS instalado
- [X] Sistema actualizado (`apt update && apt upgrade`)
- [X] Docker instalado y funcionando
- [X] Docker Compose instalado
- [X] Git instalado
- [X] Curl y Wget instalados
- [X] Nano instalado

### Seguridad

- [X] UFW instalado y configurado
- [X] Puerto 22 (SSH) permitido
- [X] Puertos 80 y 443 permitidos
- [X] Fail2Ban instalado

### Base de Datos (según necesidad)

- [ ] MySQL instalado (si se usa)
- [ ] PostgreSQL instalado (si se usa)

### Estructura

- [ ] Directorio ~/proyectos creado
- [ ] Directorio ~/backups creado
- [ ] Directorio ~/scripts creado

### Verificación

- [ ] Script de verificación ejecutado
- [ ] Todos los servicios corriendo
- [ ] Sin errores en los logs

---

## 🔧 Comandos Útiles de Mantenimiento

### Ver servicios corriendo

```bash
sudo systemctl list-units --type=service --state=running
```

### Ver uso de disco

```bash
df -h
```

### Ver uso de memoria

```bash
free -h
```

### Ver procesos

```bash
htop
```

### Limpiar espacio

```bash
# Limpiar paquetes no usados
sudo apt autoremove -y
sudo apt autoclean

# Limpiar Docker
docker system prune -a --volumes
```

---

## 📊 Recursos Mínimos Recomendados

| Recurso                  | Mínimo  | Recomendado |
| ------------------------ | -------- | ----------- |
| **CPU**            | 1 core   | 2 cores     |
| **RAM**            | 1 GB     | 2 GB        |
| **Disco**          | 20 GB    | 40 GB       |
| **Ancho de banda** | 1 TB/mes | Ilimitado   |

---

## 🆘 Troubleshooting

### Docker no inicia

```bash
sudo systemctl status docker
sudo systemctl restart docker
```

### Sin espacio en disco

```bash
# Ver qué ocupa más espacio
du -sh /* | sort -h

# Limpiar logs antiguos
sudo journalctl --vacuum-time=7d
```

### Firewall bloqueando conexiones

```bash
# Ver reglas
sudo ufw status numbered

# Permitir puerto específico
sudo ufw allow [puerto]/tcp
```

---

**Última actualización:** 2026-02-10
**Propósito:** Lista única de requisitos para el servidor VPS
