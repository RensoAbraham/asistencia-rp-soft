# 🎓 Plan de Capacitación - Deployment de Proyectos RP Soft

## 📋 Resumen de Proyectos

| # | Proyecto | Quién Despliega | Método de Enseñanza |
|---|----------|-----------------|---------------------|
| 1 | **Bot de Asistencia** | Renso (tú) | Solo deployment, sin enseñanza |
| 2 | **AV1 Arte Ideas** | Renso (tú) | **Demostración en vivo** (ellos observan) |
| 3 | **Urbany V2** | Practicantes | **Práctica supervisada** (ellos hacen, tú guías) |
| 4 | **RV3** | Practicantes | **Práctica independiente** (ellos hacen solos) |

---

## 🎯 Metodología: "Yo hago → Nosotros hacemos → Tú haces"

### Fase 1: YO HAGO (AV1 Arte Ideas)
**Tú despliegas, ellos observan y toman notas**

### Fase 2: NOSOTROS HACEMOS (Urbany V2)
**Ellos desplegan con tu guía paso a paso**

### Fase 3: TÚ HACES (RV3)
**Ellos desplegan solos, tú solo observas y corriges errores**

---

## 📅 Cronograma de Capacitación (3 sesiones)

### **Sesión 1: Demostración (1 hora)**
**Proyecto:** AV1 Arte Ideas

**Objetivo:** Que entiendan el proceso general

**Actividades:**
1. **Introducción (5 min)**
   - Explicar qué vamos a hacer
   - Mostrar la arquitectura del proyecto
   - Explicar por qué usamos Docker

2. **Demostración en vivo (40 min)**
   - Compartir pantalla
   - Desplegar AV1 paso a paso
   - Explicar CADA comando que ejecutas
   - Ellos toman notas

3. **Q&A y Resumen (15 min)**
   - Responder preguntas
   - Resumir los pasos principales
   - Entregar documento de referencia

**Documento a entregar:** `DEPLOYMENT_AV1.md`

---

### **Sesión 2: Práctica Supervisada (1.5 horas)**
**Proyecto:** Urbany V2

**Objetivo:** Que desplieguen con tu ayuda

**Actividades:**
1. **Repaso rápido (10 min)**
   - Recordar lo visto en Sesión 1
   - Mostrar el documento de Urbany V2

2. **Deployment supervisado (60 min)**
   - **ELLOS** ejecutan los comandos
   - **TÚ** solo guías y explicas
   - Pausar en cada paso para verificar
   - Resolver dudas en tiempo real

3. **Verificación y troubleshooting (20 min)**
   - Verificar que el proyecto funciona
   - Simular un error común y resolverlo juntos
   - Enseñar cómo leer logs

**Documento a usar:** `DEPLOYMENT_URBANY_V2.md`

---

### **Sesión 3: Práctica Independiente (1 hora)**
**Proyecto:** RV3

**Objetivo:** Que desplieguen solos

**Actividades:**
1. **Briefing (5 min)**
   - Explicar que desplegarán solos
   - Tú solo observas y tomas notas de errores

2. **Deployment independiente (45 min)**
   - **ELLOS** desplegan completamente solos
   - **TÚ** solo observas (sin intervenir)
   - Toman notas de errores para discutir después

3. **Retroalimentación (10 min)**
   - Discutir qué salió bien
   - Corregir errores conceptuales
   - Responder dudas finales

**Documento a usar:** `DEPLOYMENT_RV3.md`

---

## 📝 Estructura de los Documentos

Cada documento debe tener esta estructura:

### 1. **Información del Proyecto**
```markdown
## 📋 Información del Proyecto

- **Nombre:** Urbany V2
- **Tipo:** Aplicación Next.js
- **Base de datos:** PostgreSQL
- **Puerto:** 3000
- **Repositorio:** https://github.com/...
```

### 2. **Requisitos Previos**
```markdown
## ✅ Antes de Empezar

Verificar que tienes:
- [ ] Acceso SSH al VPS
- [ ] Docker instalado
- [ ] Credenciales de la base de datos
- [ ] Variables de entorno (.env)
```

### 3. **Comandos Paso a Paso**
```markdown
## 🚀 Paso 1: Conectar al VPS

```bash
ssh root@ip_del_vps
```

**¿Qué hace este comando?**
Conecta a tu servidor remoto vía SSH.

**¿Qué deberías ver?**
```
Welcome to Ubuntu...
root@servidor:~#
```
```

### 4. **Checkpoints de Verificación**
```markdown
## ✅ Checkpoint 1: Verificar conexión

```bash
docker ps
```

**Deberías ver:**
- Lista de contenedores (puede estar vacía)
- Sin errores

**Si ves un error:**
- Verificar que Docker está instalado: `docker --version`
```

### 5. **Troubleshooting**
```markdown
## 🆘 Problemas Comunes

### Error: "Cannot connect to Docker daemon"

**Causa:** Docker no está corriendo

**Solución:**
```bash
sudo systemctl start docker
```
```

---

## 🎬 Script para Cada Sesión

### **Script Sesión 1: Demostración AV1**

```
[INICIO - 5 min]
"Hola, hoy vamos a desplegar AV1 Arte Ideas. Ustedes solo observen y tomen notas.
El objetivo es que entiendan el proceso general. Luego les toca a ustedes con otros proyectos."

[DURANTE - 40 min]
Por cada comando:
1. "Voy a ejecutar: [comando]"
2. "Esto hace: [explicación simple]"
3. Ejecutar comando
4. "Como ven, el resultado es: [mostrar output]"
5. "¿Alguna pregunta hasta aquí?"

[CIERRE - 15 min]
"Resumiendo, los pasos fueron:
1. Conectar al VPS
2. Clonar repositorio
3. Configurar .env
4. Construir con Docker
5. Verificar que funciona

¿Preguntas?"
```

### **Script Sesión 2: Práctica Urbany V2**

```
[INICIO - 10 min]
"Hoy ustedes van a desplegar Urbany V2. Yo solo los guío.
Tienen el documento DEPLOYMENT_URBANY_V2.md como referencia.
Vamos paso a paso, sin apuros."

[DURANTE - 60 min]
Por cada paso:
1. "Lean el Paso X del documento"
2. "¿Qué comando van a ejecutar?"
3. Ellos responden
4. "Correcto, ejecútenlo"
5. Verificar resultado
6. "¿Qué esperaban ver? ¿Qué vieron?"
7. Siguiente paso

[CIERRE - 20 min]
"Muy bien, ahora simulemos un error común..."
[Simular error y resolverlo juntos]
```

### **Script Sesión 3: Independiente RV3**

```
[INICIO - 5 min]
"Hoy desplegarán RV3 completamente solos.
Yo solo observo. Si se traban más de 5 minutos, pidan ayuda.
El objetivo es que lo hagan sin mí."

[DURANTE - 45 min]
- Silencio, solo observar
- Tomar notas de errores
- Solo intervenir si están completamente trabados

[CIERRE - 10 min]
"Bien, hablemos de lo que pasó:
- ¿Qué fue fácil?
- ¿Dónde se trabaron?
- ¿Qué aprendieron?

Errores que noté: [discutir]"
```

---

## 📊 Checklist de Evaluación

Usa esto para verificar que aprendieron:

### **Después de Sesión 1 (Demostración)**
- [ ] Entienden qué es Docker
- [ ] Saben conectarse al VPS
- [ ] Reconocen un archivo .env
- [ ] Entienden el flujo general

### **Después de Sesión 2 (Supervisada)**
- [ ] Pueden ejecutar comandos básicos
- [ ] Saben leer logs
- [ ] Pueden identificar errores comunes
- [ ] Usan el documento de referencia

### **Después de Sesión 3 (Independiente)**
- [ ] Despliegan sin ayuda
- [ ] Resuelven errores básicos solos
- [ ] Saben dónde buscar información
- [ ] Pueden explicar qué hace cada paso

---

## 💡 Tips para Enseñar (Aunque no seas bueno enseñando)

### ✅ HACER:

1. **Usa analogías simples**
   - "Docker es como una caja que contiene todo lo necesario"
   - "SSH es como una puerta para entrar a otra computadora"

2. **Repite los conceptos clave**
   - "Como vimos antes, el .env contiene..."
   - "Recuerden que Docker Compose..."

3. **Haz preguntas en lugar de explicar**
   - "¿Qué creen que hace este comando?"
   - "¿Por qué creen que dio este error?"

4. **Celebra los aciertos**
   - "¡Exacto! Bien pensado"
   - "Correcto, ese es el siguiente paso"

5. **Normaliza los errores**
   - "Este error es súper común, a mí me pasó mil veces"
   - "Bien que lo intentaron, ahora veamos por qué falló"

### ❌ EVITAR:

1. ❌ Asumir que saben algo
2. ❌ Usar jerga técnica sin explicar
3. ❌ Ir muy rápido
4. ❌ Hacer todo tú si se traban
5. ❌ Criticar errores

---

## 📱 Formato de los Documentos

### **Opción 1: Markdown (Recomendado)**
- Fácil de editar
- Se ve bien en GitHub
- Pueden copiar/pegar comandos

### **Opción 2: Google Docs**
- Más visual
- Pueden agregar comentarios
- Fácil de compartir

### **Opción 3: Notion**
- Muy visual
- Checkboxes interactivos
- Pueden marcar pasos completados

**Mi recomendación:** Markdown + GitHub

---

## 🎯 Checklist Final Antes de Irte

### **Documentación Entregada:**
- [ ] DEPLOYMENT_AV1.md
- [ ] DEPLOYMENT_URBANY_V2.md
- [ ] DEPLOYMENT_RV3.md
- [ ] TROUBLESHOOTING_COMUN.md
- [ ] CONTACTOS_EMERGENCIA.md

### **Capacitación Completada:**
- [ ] Sesión 1: Demostración (AV1)
- [ ] Sesión 2: Supervisada (Urbany V2)
- [ ] Sesión 3: Independiente (RV3)

### **Verificación:**
- [ ] Desplegaron al menos 2 proyectos solos
- [ ] Saben resolver errores básicos
- [ ] Tienen acceso a toda la documentación
- [ ] Saben a quién contactar si hay problemas

### **Transición:**
- [ ] Credenciales transferidas
- [ ] Accesos revocados de tu cuenta
- [ ] Documentación actualizada
- [ ] Contacto de emergencia definido (tú, por X tiempo)

---

## 📞 Soporte Post-Capacitación

Define un período de soporte:

```
"Estaré disponible para dudas por [WhatsApp/Discord/Email]
durante [2 semanas / 1 mes] después de mi salida.

Horario de respuesta: [Lunes a Viernes, 9am-6pm]

Después de ese período, deberán resolver por su cuenta
usando la documentación."
```

---

## 🎓 Recursos Adicionales para Ellos

Comparte estos links:

- **Docker Docs:** https://docs.docker.com/get-started/
- **SSH Tutorial:** https://www.digitalocean.com/community/tutorials/ssh-essentials-working-with-ssh-servers-clients-and-keys
- **Linux Command Line:** https://ubuntu.com/tutorials/command-line-for-beginners

---

**Última actualización:** 2026-02-10
**Autor:** Renso Abraham
**Propósito:** Capacitar a practicantes en deployment de proyectos
