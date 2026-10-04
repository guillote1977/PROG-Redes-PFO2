import requests
import sys
import time

URL_BASE = "http://localhost:5000"

def mostrar_encabezado():
    print("\n" + "="*55)
    print("   SISTEMA DE GESTIÓN DE TAREAS - CLIENTE DE CONSOLA")
    print("   Programación sobre Redes | PFO2 - API REST & SQLite")
    print("="*55)

def probar_conexion_servidor():
    """Verifica que el servidor Flask esté corriendo en localhost:5000."""
    try:
        respuesta = requests.get(f"{URL_BASE}/", timeout=3)
        if respuesta.status_code == 200:
            print("[✓] Conexión establecida con el servidor API REST (localhost:5000).")
            return True
    except requests.exceptions.ConnectionError:
        print("\n[X] Error de conexión: No se pudo conectar al servidor en 'http://localhost:5000'.")
        print("    Asegúrese de ejecutar 'python servidor.py' en otra terminal antes de iniciar el cliente.")
        return False
    except Exception as e:
        print(f"\n[X] Error inesperado al verificar el servidor: {e}")
        return False

def registrar_usuario():
    """Solicita credenciales y realiza una petición POST /registro al servidor."""
    print("\n--- REGISTRO DE NUEVO USUARIO ---")
    usuario = input("Ingrese nombre de usuario: ").strip()
    contrasena = input("Ingrese contraseña: ").strip()
    
    if not usuario or not contrasena:
        print("[!] El usuario y la contraseña no pueden estar vacíos.")
        return

    payload = {
        "usuario": usuario,
        "contraseña": contrasena
    }
    
    try:
        respuesta = requests.post(f"{URL_BASE}/registro", json=payload, timeout=5)
        datos = respuesta.json()
        
        if respuesta.status_code == 201:
            print(f"\n[✓] ¡ÉXITO! {datos.get('mensaje')}. Usuario: '{datos.get('usuario')}'")
            print("    La contraseña fue almacenada de manera segura con hasheo PBKDF2/SHA256 en la base de datos.")
        else:
            print(f"\n[X] Error en el registro ({respuesta.status_code}): {datos.get('error')}")
    except Exception as e:
        print(f"\n[X] Ocurrió un error al comunicarse con la API: {e}")

def iniciar_sesion():
    """Solicita credenciales y realiza una petición POST /login."""
    print("\n--- INICIO DE SESIÓN ---")
    usuario = input("Nombre de usuario: ").strip()
    contrasena = input("Contraseña: ").strip()
    
    if not usuario or not contrasena:
        print("[!] Ingrese tanto el usuario como la contraseña.")
        return None

    payload = {
        "usuario": usuario,
        "contraseña": contrasena
    }
    
    try:
        respuesta = requests.post(f"{URL_BASE}/login", json=payload, timeout=5)
        datos = respuesta.json()
        
        if respuesta.status_code == 200:
            print(f"\n[✓] ¡LOGIN CORRECTO! {datos.get('mensaje')}")
            print(f"    Bienvenido, {datos.get('usuario')} (ID de usuario: {datos.get('usuario_id')})")
            return {
                "id": datos.get('usuario_id'),
                "nombre": datos.get('usuario')
            }
        else:
            print(f"\n[X] Error al iniciar sesión ({respuesta.status_code}): {datos.get('error')}")
            return None
    except Exception as e:
        print(f"\n[X] Error al comunicarse con el servidor: {e}")
        return None

def consultar_vista_tareas_html():
    """Solicita la ruta GET /tareas y muestra información del HTML / JSON devuelto."""
    print("\n--- CONSULTA DE VISTA GET /tareas ---")
    try:
        # Petición solicitando JSON explícitamente
        respuesta_json = requests.get(f"{URL_BASE}/tareas", headers={"Accept": "application/json"}, timeout=5)
        # Petición estándar (devuelve HTML)
        respuesta_html = requests.get(f"{URL_BASE}/tareas", timeout=5)
        
        print(f"[✓] Respuesta servidor GET /tareas (Status {respuesta_html.status_code}):")
        if respuesta_json.status_code == 200:
            print(f"    Respuesta JSON: {respuesta_json.json().get('mensaje')}")
        print(f"    Respuesta HTML (primeros 200 caracteres):\n    '{respuesta_html.text.strip()[:200]}...'")
        print("\n    Nota: Si abre 'http://localhost:5000/tareas' en su navegador, verá la página completa de bienvenida.")
    except Exception as e:
        print(f"[X] Error al consultar la ruta /tareas: {e}")

def menu_gestion_tareas(usuario_activo):
    """Menú secundario para la creación y gestión de tareas una vez iniciada la sesión."""
    while True:
        print(f"\n--- PANEL DE TAREAS (Usuario: {usuario_activo['nombre']}) ---")
        print("1. Ver mis tareas")
        print("2. Crear una nueva tarea")
        print("3. Marcar tarea como completada")
        print("4. Volver al menú principal")
        
        opcion = input("Seleccione una opción (1-4): ").strip()
        
        if opcion == "1":
            try:
                res = requests.get(f"{URL_BASE}/tareas/usuario/{usuario_activo['id']}", timeout=5)
                datos = res.json()
                tareas = datos.get('tareas', [])
                
                print(f"\n[T] Tareas de {usuario_activo['nombre']} (Total: {len(tareas)}):")
                if not tareas:
                    print("    (No hay tareas registradas. Utilice la opción 2 para agregar una).")
                else:
                    for t in tareas:
                        estado = "[✓ COMPLETA]" if t['completada'] else "[  PENDIENTE]"
                        print(f"    ID {t['id']} | {estado} | {t['titulo']}")
                        if t['descripcion']:
                            print(f"         Descripción: {t['descripcion']}")
            except Exception as e:
                print(f"[X] Error al obtener tareas: {e}")
                
        elif opcion == "2":
            titulo = input("Título de la tarea: ").strip()
            descripcion = input("Descripción (opcional): ").strip()
            if not titulo:
                print("[!] El título es obligatorio.")
                continue
                
            payload = {
                "usuario_id": usuario_activo['id'],
                "titulo": titulo,
                "descripcion": descripcion
            }
            try:
                res = requests.post(f"{URL_BASE}/tareas", json=payload, timeout=5)
                if res.status_code == 201:
                    print(f"\n[✓] {res.json().get('mensaje')}")
                else:
                    print(f"\n[X] Error: {res.json().get('error')}")
            except Exception as e:
                print(f"[X] Error al crear tarea: {e}")
                
        elif opcion == "3":
            tarea_id = input("Ingrese el ID de la tarea a completar: ").strip()
            if not tarea_id.isdigit():
                print("[!] Ingrese un número de ID válido.")
                continue
            try:
                res = requests.put(f"{URL_BASE}/tareas/{tarea_id}/completar", timeout=5)
                if res.status_code == 200:
                    print(f"\n[✓] {res.json().get('mensaje')}")
                else:
                    print(f"\n[X] Error: {res.json().get('error')}")
            except Exception as e:
                print(f"[X] Error al actualizar tarea: {e}")
                
        elif opcion == "4":
            break
        else:
            print("[!] Opción inválida. Intente de nuevo.")

def main():
    mostrar_encabezado()
    if not probar_conexion_servidor():
        sys.exit(1)

    usuario_sesion = None

    while True:
        print("\n" + "-"*40)
        print("           MENÚ PRINCIPAL")
        print("-"*40)
        print("1. Registrar nuevo usuario (POST /registro)")
        print("2. Iniciar sesión (POST /login)")
        print("3. Consultar vista GET /tareas")
        if usuario_sesion:
            print(f"4. Gestionar tareas de '{usuario_sesion['nombre']}'")
        else:
            print("4. Gestionar tareas (requiere iniciar sesión)")
        print("5. Salir")
        
        opcion = input("\nSeleccione una opción (1-5): ").strip()
        
        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            usuario_sesion = iniciar_sesion()
        elif opcion == "3":
            consultar_vista_tareas_html()
        elif opcion == "4":
            if not usuario_sesion:
                print("\n[!] Debe iniciar sesión primero (Opción 2) para gestionar sus tareas.")
                intentar_login = input("¿Desea iniciar sesión ahora? (s/n): ").strip().lower()
                if intentar_login == 's':
                    usuario_sesion = iniciar_sesion()
                    if usuario_sesion:
                        menu_gestion_tareas(usuario_sesion)
            else:
                menu_gestion_tareas(usuario_sesion)
        elif opcion == "5":
            print("\n¡Gracias por utilizar el cliente API de la PFO2! Hasta luego.")
            break
        else:
            print("\n[!] Opción inválida. Por favor, seleccione un número entre 1 y 5.")

if __name__ == '__main__':
    main()
