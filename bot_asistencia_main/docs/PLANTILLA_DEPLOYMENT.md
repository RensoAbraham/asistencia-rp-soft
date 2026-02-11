# 🚀 PLANTILLA: Guía de Deployment

> **Copia esta plantilla para cada proyecto y rellena los espacios**

---

## 📋 Información del Proyecto

- **Nombre del Proyecto:** [Nombre]
- **Tipo de Aplicación:** [Next.js / React / Node.js / Python / etc.]
- **Base de Datos:** [PostgreSQL / MySQL / MongoDB / Ninguna]
- **Puerto Principal:** [3000 / 8080 / etc.]
- **Repositorio Git:** [URL del repositorio]
- **Rama a desplegar:** [main / production / etc.]

---

## ✅ Requisitos Previos

Antes de empezar, verifica que tienes:

- [ ] Acceso SSH al VPS (usuario y contraseña)
- [ ] IP del VPS: `_______________`
- [ ] Docker instalado en el VPS
- [ ] Archivo `.env` configurado
- [ ] Credenciales de base de datos (si aplica)
- [ ] Tokens/API Keys necesarios

---

## 🎯 Resumen del Proceso (5 pasos)

```
1. Conectar al VPS
2. Preparar el proyecto (clonar/subir archivos)
3. Configurar variables de entorno
4. Construir e iniciar con Docker
5. Verificar que funciona
```

**Tiempo estimado:** [30 minutos / 1 hora / etc.]

---

## 📝 Paso a Paso Detallado

### 🔌 Paso 1: Conectar al VPS

**Comando:**
```bash
ssh [usuario]@[ip_del_vps]
```

**Ejemplo:**
```bash
ssh root@123.45.67.89
```

**¿Qué hace?**
Conecta a tu servidor remoto mediante SSH (Secure Shell).

**¿Qué deberías ver?**
```
Welcome to Ubuntu 22.04 LTS
Last login: Mon Feb 10 10:00:00 2026
root@servidor:~#
```

**Si ves un error:**
- Verificar que la IP es correcta
- Verificar que tienes la contraseña correcta
- Verificar que tienes conexión a internet

---

### 📁 Paso 2: Preparar el Proyecto

#### Opción A: Clonar desde Git (Recomendado)

**Comandos:**
```bash
# Crear directorio
mkdir -p ~/proyectos/[nombre_proyecto]
cd ~/proyectos/[nombre_proyecto]

# Clonar repositorio
git clone [url_repositorio] .

# Verificar archivos
ls -la
```

**Ejemplo:**
```bash
mkdir -p ~/proyectos/urbany_v2
cd ~/proyectos/urbany_v2
git clone https://github.com/rpsoft/urbany-v2.git .
ls -la
```

**¿Qué deberías ver?**
```
drwxr-xr-x  5 root root 4096 Feb 10 10:00 .
drwxr-xr-x  3 root root 4096 Feb 10 10:00 ..
-rw-r--r--  1 root root  123 Feb 10 10:00 Dockerfile
-rw-r--r--  1 root root  456 Feb 10 10:00 docker-compose.yml
-rw-r--r--  1 root root  789 Feb 10 10:00 package.json
...
```

#### Opción B: Subir archivos con SCP

**Desde tu PC (PowerShell):**
```powershell
# Comprimir proyecto
cd "C:\ruta\al\proyecto"
tar -czf proyecto.tar.gz *

# Subir al VPS
scp proyecto.tar.gz root@ip_vps:~/
```

**En el VPS:**
```bash
# Crear directorio y descomprimir
mkdir -p ~/proyectos/[nombre_proyecto]
cd ~/proyectos/[nombre_proyecto]
tar -xzf ~/proyecto.tar.gz
rm ~/proyecto.tar.gz
```

---

### ⚙️ Paso 3: Configurar Variables de Entorno

**Comando:**
```bash
cd ~/proyectos/[nombre_proyecto]
nano .env
```

**Contenido del .env:**
```env
# [INSTRUCCIONES: Pegar aquí el contenido del .env]

# Ejemplo para Next.js:
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_db
NEXT_PUBLIC_API_URL=https://api.ejemplo.com
SECRET_KEY=tu_clave_secreta_aqui
```

**Guardar archivo:**
1. Presionar `Ctrl + X`
2. Presionar `Y` (Yes)
3. Presionar `Enter`

**Verificar que se guardó:**
```bash
cat .env
```

**⚠️ IMPORTANTE:**
- NO compartir el .env públicamente
- NO subirlo a Git
- Verificar que todas las variables están completas

---

### 🐳 Paso 4: Construir e Iniciar con Docker

#### 4.1 Verificar archivos Docker

**Comando:**
```bash
ls -la | grep -i docker
```

**Deberías ver:**
```
-rw-r--r--  1 root root  351 Feb 10 10:00 Dockerfile
-rw-r--r--  1 root root  300 Feb 10 10:00 docker-compose.yml
```

#### 4.2 Construir imagen

**Comando:**
```bash
docker-compose build
```

**¿Qué hace?**
Construye la imagen Docker del proyecto según las instrucciones del Dockerfile.

**¿Qué deberías ver?**
```
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [internal] load metadata for docker.io/library/node:18
 ...
 => => naming to docker.io/library/[nombre_proyecto]
```

**Tiempo estimado:** [2-5 minutos]

#### 4.3 Iniciar contenedores

**Comando:**
```bash
docker-compose up -d
```

**¿Qué hace?**
- `up`: Inicia los contenedores
- `-d`: En modo "detached" (segundo plano)

**¿Qué deberías ver?**
```
[+] Running 2/2
 ✔ Container [nombre_proyecto]-db-1   Started
 ✔ Container [nombre_proyecto]-app-1  Started
```

---

### ✅ Paso 5: Verificar que Funciona

#### 5.1 Ver contenedores corriendo

**Comando:**
```bash
docker ps
```

**Deberías ver:**
```
CONTAINER ID   IMAGE              STATUS         PORTS
abc123def456   proyecto-app       Up 2 minutes   0.0.0.0:3000->3000/tcp
def456ghi789   postgres:15        Up 2 minutes   5432/tcp
```

**Verificar:**
- [ ] Estado = "Up X minutes" (no "Restarting" o "Exited")
- [ ] Puerto correcto mapeado

#### 5.2 Ver logs

**Comando:**
```bash
docker-compose logs -f
```

**Buscar líneas como:**
```
✓ Ready in 3.2s
✓ Local: http://localhost:3000
✓ Database connected
```

**Para salir de los logs:** `Ctrl + C`

#### 5.3 Probar desde el navegador

**Abrir en tu navegador:**
```
http://[ip_del_vps]:[puerto]
```

**Ejemplo:**
```
http://123.45.67.89:3000
```

**Deberías ver:**
- [ ] La aplicación carga correctamente
- [ ] No hay errores 500 o 404
- [ ] Puedes navegar por la aplicación

---

## ✅ Checkpoints de Verificación

Marca cada checkpoint al completarlo:

### Checkpoint 1: Conexión SSH
- [ ] Conectado al VPS
- [ ] Puedo ejecutar comandos
- [ ] Veo el prompt: `root@servidor:~#`

### Checkpoint 2: Archivos del Proyecto
- [ ] Directorio creado
- [ ] Archivos clonados/subidos
- [ ] Veo Dockerfile y docker-compose.yml

### Checkpoint 3: Configuración
- [ ] Archivo .env creado
- [ ] Todas las variables configuradas
- [ ] Sin valores de ejemplo o placeholders

### Checkpoint 4: Docker Build
- [ ] Build completado sin errores
- [ ] Imagen creada correctamente
- [ ] No hay warnings críticos

### Checkpoint 5: Aplicación Corriendo
- [ ] Contenedores en estado "Up"
- [ ] Logs muestran "Ready" o similar
- [ ] Aplicación accesible desde navegador

---

## 🆘 Troubleshooting (Problemas Comunes)

### Error: "Cannot connect to Docker daemon"

**Causa:** Docker no está corriendo

**Solución:**
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

---

### Error: "Port already in use"

**Causa:** El puerto ya está siendo usado por otro proceso

**Solución 1:** Cambiar puerto en docker-compose.yml
```yaml
ports:
  - "3001:3000"  # Cambiar 3000 a 3001
```

**Solución 2:** Detener el proceso que usa el puerto
```bash
# Ver qué usa el puerto
sudo lsof -i :3000

# Detener contenedor anterior
docker-compose down
```

---

### Error: "Build failed" o errores durante build

**Causa:** Dependencias faltantes o errores en el código

**Solución:**
```bash
# Ver logs detallados
docker-compose build --no-cache

# Verificar que el .env está correcto
cat .env

# Verificar que package.json existe
cat package.json
```

---

### Error: "Database connection failed"

**Causa:** Base de datos no está corriendo o credenciales incorrectas

**Solución:**
```bash
# Ver logs de la base de datos
docker-compose logs db

# Verificar que el contenedor de DB está corriendo
docker ps | grep db

# Verificar credenciales en .env
cat .env | grep DATABASE
```

---

### Aplicación no carga en el navegador

**Causa:** Firewall bloqueando el puerto

**Solución:**
```bash
# Permitir puerto en firewall
sudo ufw allow [puerto]/tcp

# Ejemplo:
sudo ufw allow 3000/tcp

# Ver reglas del firewall
sudo ufw status
```

---

## 🔄 Comandos de Mantenimiento

### Ver logs en tiempo real
```bash
docker-compose logs -f
```

### Reiniciar aplicación
```bash
docker-compose restart
```

### Detener aplicación
```bash
docker-compose down
```

### Actualizar código y reiniciar
```bash
git pull origin main
docker-compose up --build -d
```

### Ver uso de recursos
```bash
docker stats
```

### Limpiar espacio en disco
```bash
docker system prune -a
```

---

## 📊 Checklist Final

Antes de dar por terminado el deployment:

- [ ] Aplicación accesible desde navegador
- [ ] Base de datos funcionando (si aplica)
- [ ] Logs sin errores críticos
- [ ] Variables de entorno configuradas
- [ ] Puerto correcto abierto en firewall
- [ ] Documentado en [lugar donde guardan info]
- [ ] Equipo notificado del deployment

---

## 📞 Contactos de Soporte

**Si tienes problemas:**

1. **Revisar esta guía** - Especialmente la sección de Troubleshooting
2. **Ver logs:** `docker-compose logs -f`
3. **Buscar el error en Google:** Copiar mensaje de error exacto
4. **Contactar a:** [Nombre] - [Email/WhatsApp]

---

## 📝 Notas Adicionales

**Espacio para notas personales:**

```
[Aquí puedes agregar notas específicas del proyecto]
[Configuraciones especiales]
[Comandos útiles específicos]
```

---

**Última actualización:** [Fecha]
**Autor:** [Tu nombre]
**Versión del documento:** 1.0
