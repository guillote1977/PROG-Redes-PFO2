# Práctica Formativa Obligatoria 2 (PFO 2)
## Sistema de Gestión de Tareas con API REST, SQLite y Autenticación de Usuarios

**Materia:** Programación sobre Redes  
**Cátedra:** Alan Portillo, Germán Ríos  
**Carrera:** Tecnicatura Superior en Desarrollo de Software (IFTS N° 29)  

---

## 📌 Descripción del Proyecto

Este trabajo práctico consiste en el desarrollo de un sistema completo **Cliente-Servidor** para la gestión de usuarios y tareas mediante una **API REST construida en Python con Flask** y persistencia en una base de datos **SQLite**.

El servidor implementa medidas de ciberseguridad clave como el **hasheo seguro de contraseñas** utilizando funciones criptográficas (`PBKDF2` con `SHA256` y sal única) mediante la librería `werkzeug.security`. Por su parte, el cliente es una **aplicación interactiva de consola** en Python que permite consumir los endpoints de la API en tiempo real.

---

## 🛠️ Arquitectura y Tecnologías Utilizadas

- **Servidor API REST (`servidor.py`)**: Desarrollado en Python 3 con **Flask**.
- **Base de Datos Persistente (`tareas.db`)**: Motor **SQLite3**.
- **Seguridad y Hasheo**: Módulo `werkzeug.security` (`generate_password_hash`, `check_password_hash`).
- **Cliente Consola (`cliente.py`)**: Desarrollado en Python 3 utilizando la librería `requests`.

---

## 🚀 Guía de Instalación y Ejecución

### Prerrequisitos

El proyecto utiliza librerías estándar de Python y el paquete `requests` para el cliente HTTP:

```bash
pip install flask requests
```

---

### Pasos para Ejecutar y Probar el Proyecto

#### 1. Iniciar el Servidor API REST
Abre una terminal en el directorio del proyecto y ejecuta:

```bash
python servidor.py
```

*Respuesta esperada en consola:*
```text
[DB] Base de datos inicializada correctamente con tablas 'usuarios' y 'tareas'.
[SERVER] Servidor Flask corriendo en http://localhost:5000 ...
```
*(Nota: El servidor creará automáticamente el archivo `tareas.db` en su primera ejecución).*

---

#### 2. Iniciar el Cliente de Consola
Abre una **segunda terminal** en el mismo directorio y ejecuta:

```bash
python cliente.py
```

---

## 📋 Endpoints de la API REST

| Método | Endpoint | Descripción | Formato Entrada / Payload |
| :--- | :--- | :--- | :--- |
| `POST` | `/registro` | Registro de nuevos usuarios con contraseña hasheada | `{"usuario": "nombre", "contraseña": "1234"}` |
| `POST` | `/login` | Verificación de credenciales y autenticación | `{"usuario": "nombre", "contraseña": "1234"}` |
| `GET` | `/tareas` | Muestra vista HTML de bienvenida o estado JSON | N/A (Header `Accept: application/json` opcional) |
| `POST` | `/tareas` | Crear una nueva tarea vinculada a un usuario | `{"usuario_id": 1, "titulo": "Aprender Flask", "descripcion": "..."}` |
| `GET` | `/tareas/usuario/<id>` | Obtener el listado de tareas de un usuario | N/A |
| `PUT` | `/tareas/<id>/completar` | Marcar una tarea específica como completada | N/A |

---

## 📸 Secuencia de Prueba Exitosa

1. **Registro**: Desde la Opción 1 del cliente, registra un usuario (ej. usuario: `alan`, contraseña: `secretpassword123`).
2. **Login**: Desde la Opción 2 del cliente, inicia sesión con las credenciales registradas. El servidor validará el hash y retornará el `usuario_id`.
3. **Consulta GET /tareas**: Selecciona la Opción 3 para verificar la respuesta del endpoint `/tareas` en consola o abre `http://localhost:5000/tareas` en tu navegador preferido.
4. **Gestión de Tareas**: Selecciona la Opción 4 para crear, listar y marcar tareas como completadas asociadas a tu usuario.

---

## 💡 Respuestas Conceptuales Exigidas en la Consigna

### 1. ¿Por qué es fundamental hashear contraseñas?

Hashear las contraseñas antes de almacenarlas en la base de datos es una buena práctica de ciberseguridad fundamental por las siguientes razones:

- **Protección contra filtraciones de datos (Data Leaks)**: Si la base de datos resulta comprometida o sustraída por un atacante, las contraseñas no se encontrarán expuestas en texto plano. El atacante solo obtendrá hashes criptográficos irreversibles.
- **Inversibilidad Criptográfica (Funciones de una sola vía)**: Una función de hasheo (como PBKDF2 o SHA256) es un algoritmo unidireccional. Resulta computacionalmente inviable reconstruir la contraseña original a partir de su valor hash.
- **Protección contra ataques por Diccionario y Tablas Rainbow**: Al utilizar sal de hasheo (*salt*), cada contraseña genera un hash único incluso si dos usuarios utilizan la misma contraseña en texto plano, neutralizando ataques masivos con tablas precalculadas.
- **Cumplimiento Normativo y Privacidad**: Normativas internacionales de protección de datos (como GDPR o ISO 27001) exigen que las credenciales de los usuarios nunca se almacenen o transmitan sin protección adecuada.

---

### 2. Ventajas de usar SQLite en este proyecto

SQLite es el motor de base de datos relacional ideal para este proyecto por los siguientes motivos:

- **Serverless (Sin servidor independiente)**: A diferencia de motores tradicionales como PostgreSQL o MySQL, SQLite no requiere la instalación, configuración ni mantenimiento de un proceso de servidor de base de datos separado.
- **Almacenamiento en Archivo Único y Portable**: Todos los datos (tablas, índices, usuarios y tareas) se guardan en un único archivo de disco (`tareas.db`), lo que facilita la portabilidad, distribución y ejecución inmediata del código en cualquier entorno.
- **Cero Configuración (Zero-Configuration)**: Se integra de manera nativa en la biblioteca estándar de Python mediante el módulo `sqlite3`, sin necesidad de instalar controladores ni dependencias externas.
- **Rendimiento Excelente y Transacciones ACID**: Es extremadamente rápido en operaciones de lectura y escritura para aplicaciones de pequeña y mediana escala, garantizando la integridad de los datos mediante cumplimiento estricto de propiedades ACID (Atomicidad, Consistencia, Aislamiento y Durabilidad).
