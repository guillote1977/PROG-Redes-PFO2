#SCIULLI, Guillermo Miguel - COM E - 
import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB_NAME = "tareas.db"

# ==========================================
# INICIALIZACIÓN DE LA BASE DE DATOS SQLITE
# ==========================================
def obtener_conexion_bd():
    #Establece conexión con la base de datos SQLite y retorna el objeto de conexión.
    conexion = sqlite3.connect(DB_NAME)
    conexion.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conexion

def inicializar_bd():
    #Crea las tablas 'usuarios' y 'tareas' si no existen en la base de datos.
    with obtener_conexion_bd() as conexion:
        cursor = conexion.cursor()
        
        # Tabla de Usuarios (contraseñas hasheadas)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contrasena_hash TEXT NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de Tareas vinculada a los usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                completada INTEGER DEFAULT 0,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        ''')
        conexion.commit()
    print("[DB] Base de datos inicializada correctamente con tablas 'usuarios' y 'tareas'.")

# ==========================================
# ENDPOINTS DE LA API REST (FLASK)
# ==========================================

@app.route('/', methods=['GET'])
def inicio():
    #Ruta raíz de estado de la API.
    return jsonify({
        "estado": "Servidor activo",
        "version": "1.0.0",
        "endpoints_disponibles": [
            "POST /registro",
            "POST /login",
            "GET /tareas",
            "POST /tareas",
            "GET /tareas/usuario/<usuario_id>",
            "PUT /tareas/<tarea_id>/completar"
        ]
    }), 200

# ------------------------------------------
# 1. REGISTRO DE USUARIOS (POST /registro)
# ------------------------------------------
@app.route('/registro', methods=['POST'])
def registro():
    
    #Endpoint para registrar un nuevo usuario.
    #Recibe JSON: {"usuario": "nombre", "contraseña": "1234"} o {"usuario": "nombre", "contrasena": "1234"}
    #Almacena el usuario con la contraseña hasheada de manera segura.
    
    datos = request.get_json(silent=True) or request.form
    
    if not datos:
        return jsonify({"error": "No se enviaron datos válidos en la petición"}), 400
        
    usuario = datos.get('usuario')
    # Permite tanto 'contraseña' como 'contrasena' para evitar inconvenientes de codificación
    contrasena = datos.get('contraseña') or datos.get('contrasena')
    
    if not usuario or not contrasena:
        return jsonify({"error": "Debe proporcionar los campos 'usuario' y 'contraseña'"}), 400
        
    usuario = str(usuario).strip()
    contrasena = str(contrasena).strip()
    
    if len(usuario) < 3 or len(contrasena) < 3:
        return jsonify({"error": "El usuario y la contraseña deben tener al menos 3 caracteres"}), 400

    # Hashear la contraseña usando werkzeug.security (PBKDF2 con SHA256 + salt)
    hash_contrasena = generate_password_hash(contrasena)
    
    try:
        with obtener_conexion_bd() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO usuarios (usuario, contrasena_hash) VALUES (?, ?)",
                (usuario, hash_contrasena)
            )
            conexion.commit()
            return jsonify({
                "mensaje": "Usuario registrado exitosamente",
                "usuario": usuario
            }), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": f"El nombre de usuario '{usuario}' ya se encuentra registrado"}), 409
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

# ------------------------------------------
# 2. INICIO DE SESIÓN (POST /login)
# ------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    
    #Endpoint para autenticar un usuario existente.
    #Recibe JSON: {"usuario": "nombre", "contraseña": "1234"}
    #Verifica las credenciales comparando el hash de la contraseña.
    
    datos = request.get_json(silent=True) or request.form
    
    if not datos:
        return jsonify({"error": "No se enviaron datos válidos en la petición"}), 400
        
    usuario = datos.get('usuario')
    contrasena = datos.get('contraseña') or datos.get('contrasena')
    
    if not usuario or not contrasena:
        return jsonify({"error": "Debe proporcionar los campos 'usuario' y 'contraseña'"}), 400

    try:
        with obtener_conexion_bd() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (str(usuario).strip(),))
            usuario_db = cursor.fetchone()
            
            if usuario_db is None:
                return jsonify({"error": "Credenciales inválidas (usuario no encontrado)"}), 401
                
            # Verificación del hash de la contraseña
            if not check_password_hash(usuario_db['contrasena_hash'], str(contrasena).strip()):
                return jsonify({"error": "Credenciales inválidas (contraseña incorrecta)"}), 401
                
            return jsonify({
                "mensaje": "Inicio de sesión exitoso",
                "usuario_id": usuario_db['id'],
                "usuario": usuario_db['usuario']
            }), 200
    except Exception as e:
        return jsonify({"error": f"Error interno en la autenticación: {str(e)}"}), 500

# ------------------------------------------
# 3. GESTIÓN DE TAREAS (GET /tareas)
# ------------------------------------------
@app.route('/tareas', methods=['GET'])
def tareas():
    
    #Endpoint GET /tareas: Muestra un HTML de bienvenida interactivo al acceder desde un navegador.
    #Si se solicita mediante JSON o cliente API, responde con el estado del módulo de tareas.
    
    # Si se prefiere JSON o manda ?format=json
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        return jsonify({
            "mensaje": "Bienvenido a la API REST de Gestión de Tareas - PFO2",
            "instrucciones": "Utilice POST /login para autenticarse y luego acceda a sus tareas."
        }), 200

    # Plantilla HTML de bienvenida con diseño moderno
    html_bienvenida = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bienvenido - Sistema de Gestión de Tareas</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #4f46e5;
                --bg-gradient-1: #0f172a;
                --bg-gradient-2: #1e1b4b;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --card-bg: rgba(30, 41, 59, 0.7);
                --card-border: rgba(255, 255, 255, 0.1);
            }
            body { 
                font-family: 'Inter', sans-serif; 
                background: linear-gradient(135deg, var(--bg-gradient-1), var(--bg-gradient-2)); 
                color: var(--text-main); 
                margin: 0; 
                padding: 40px 20px; 
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                box-sizing: border-box;
            }
            .container { 
                max-width: 700px; 
                width: 100%;
                background: var(--card-bg); 
                padding: 45px; 
                border-radius: 24px; 
                box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); 
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid var(--card-border);
                transform: translateY(0);
                transition: transform 0.4s ease, box-shadow 0.4s ease;
            }
            .container:hover {
                transform: translateY(-5px);
                box-shadow: 0 30px 60px -15px rgba(0,0,0,0.7);
            }
            h1 { 
                color: #ffffff; 
                font-size: 34px; 
                font-weight: 800;
                margin-bottom: 14px; 
                letter-spacing: -0.5px;
                background: linear-gradient(to right, #818cf8, #c084fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            p { 
                font-size: 16px; 
                color: var(--text-muted); 
                line-height: 1.7; 
            }
            .badge { 
                display: inline-flex; 
                align-items: center;
                background: rgba(16, 185, 129, 0.15); 
                color: #34d399; 
                padding: 8px 16px; 
                border-radius: 9999px; 
                font-weight: 600; 
                font-size: 13px; 
                margin-bottom: 24px; 
                border: 1px solid rgba(16, 185, 129, 0.3);
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }
            .badge::before {
                content: '';
                display: inline-block;
                width: 8px;
                height: 8px;
                background-color: #34d399;
                border-radius: 50%;
                margin-right: 8px;
                box-shadow: 0 0 8px #34d399;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.4); }
                70% { box-shadow: 0 0 0 6px rgba(52, 211, 153, 0); }
                100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
            }
            .endpoints { 
                text-align: left; 
                background: rgba(15, 23, 42, 0.6); 
                padding: 26px; 
                border-radius: 16px; 
                margin-top: 35px; 
                border: 1px solid var(--card-border);
            }
            .endpoints h3 {
                margin-top: 0;
                font-size: 18px;
                color: #e2e8f0;
                font-weight: 600;
                margin-bottom: 20px;
            }
            ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            li {
                padding: 14px 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
                display: flex;
                align-items: center;
                color: #cbd5e1;
                font-size: 15px;
                transition: color 0.2s ease;
            }
            li:hover {
                color: #ffffff;
            }
            li:last-child {
                border-bottom: none;
                padding-bottom: 0;
            }
            code { 
                background: rgba(99, 102, 241, 0.15); 
                padding: 6px 12px; 
                border-radius: 8px; 
                font-family: 'Fira Code', monospace; 
                color: #818cf8; 
                font-size: 13px;
                font-weight: 600;
                margin-right: 15px;
                border: 1px solid rgba(99, 102, 241, 0.3);
                transition: background 0.2s ease;
            }
            li:hover code {
                background: rgba(99, 102, 241, 0.25);
            }
            .footer {
                margin-top: 40px; 
                font-size: 13px; 
                color: #64748b; 
                text-align: center;
                border-top: 1px solid rgba(255,255,255,0.05);
                padding-top: 25px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <span class="badge">API REST Funcional - PFO2</span>
            <h1>Sistema de Gestión de Tareas</h1>
            <p>Esta plataforma permite gestionar usuarios de forma segura mediante <strong>hasheo de contraseñas</strong> y almacenar tareas persistentes de forma eficiente con <strong>SQLite</strong>.</p>
            
            <div class="endpoints">
                <h3>Endpoints disponibles para interactuar:</h3>
                <ul>
                    <li><code>POST /registro</code> Registrar un nuevo usuario</li>
                    <li><code>POST /login</code> Iniciar sesión de usuario</li>
                    <li><code>GET /tareas</code> Vista de bienvenida (HTML / JSON)</li>
                    <li><code>POST /tareas</code> Crear una nueva tarea</li>
                    <li><code>GET /tareas/usuario/&lt;id&gt;</code> Listar tareas de un usuario</li>
                    <li><code>PUT /tareas/&lt;id&gt;/completar</code> Marcar tarea como completada</li>
                </ul>
            </div>
            <div class="footer">
                Programación sobre Redes | IFTS N° 29
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_bienvenida), 200

# ------------------------------------------
# ENDPOINTS ADICIONALES DE GESTIÓN DE TAREAS
# ------------------------------------------
@app.route('/tareas', methods=['POST'])
def crear_tarea():
    #Crea una nueva tarea asociada a un usuario registrado.
    datos = request.get_json(silent=True) or request.form
    if not datos:
        return jsonify({"error": "No se enviaron datos válidos"}), 400
        
    usuario_id = datos.get('usuario_id')
    titulo = datos.get('titulo')
    descripcion = datos.get('descripcion', '')
    
    if not usuario_id or not titulo:
        return jsonify({"error": "Se requieren los campos 'usuario_id' y 'titulo'"}), 400
        
    try:
        with obtener_conexion_bd() as conexion:
            cursor = conexion.cursor()
            # Verificar existencia del usuario
            cursor.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id,))
            if not cursor.fetchone():
                return jsonify({"error": "El usuario especificado no existe"}), 404
                
            cursor.execute(
                "INSERT INTO tareas (usuario_id, titulo, descripcion) VALUES (?, ?, ?)",
                (usuario_id, str(titulo).strip(), str(descripcion).strip())
            )
            conexion.commit()
            tarea_id = cursor.lastrowid
            
            return jsonify({
                "mensaje": "Tarea creada exitosamente",
                "tarea": {
                    "id": tarea_id,
                    "usuario_id": usuario_id,
                    "titulo": titulo,
                    "descripcion": descripcion,
                    "completada": False
                }
            }), 201
    except Exception as e:
        return jsonify({"error": f"Error al crear la tarea: {str(e)}"}), 500

@app.route('/tareas/usuario/<int:usuario_id>', methods=['GET'])
def listar_tareas_usuario(usuario_id):
    #Retorna todas las tareas pertenecientes a un usuario.
    try:
        with obtener_conexion_bd() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM tareas WHERE usuario_id = ? ORDER BY fecha_creacion DESC", (usuario_id,))
            filas = cursor.fetchall()
            
            tareas_lista = [
                {
                    "id": fila["id"],
                    "titulo": fila["titulo"],
                    "descripcion": fila["descripcion"],
                    "completada": bool(fila["completada"]),
                    "fecha_creacion": fila["fecha_creacion"]
                }
                for fila in filas
            ]
            return jsonify({
                "usuario_id": usuario_id,
                "total_tareas": len(tareas_lista),
                "tareas": tareas_lista
            }), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener las tareas: {str(e)}"}), 500

@app.route('/tareas/<int:tarea_id>/completar', methods=['PUT'])
def completar_tarea(tarea_id):
    #Marca una tarea como completada.
    try:
        with obtener_conexion_bd() as conexion:
            cursor = conexion.cursor()
            cursor.execute("UPDATE tareas SET completada = 1 WHERE id = ?", (tarea_id,))
            if cursor.rowcount == 0:
                return jsonify({"error": "Tarea no encontrada"}), 404
            conexion.commit()
            return jsonify({"mensaje": f"Tarea {tarea_id} marcada como completada"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar tarea: {str(e)}"}), 500

# ==========================================
# INICIO DE LA APLICACIÓN FLASK
# ==========================================
if __name__ == '__main__':
    inicializar_bd()
    print("[SERVER] Servidor Flask corriendo en http://localhost:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
