from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime, time, timedelta
import os

app = Flask(__name__)

# =========================
#   CORS
# =========================
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)


@app.after_request
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add(
        "Access-Control-Allow-Headers",
        "Content-Type,Authorization"
    )
    response.headers.add(
        "Access-Control-Allow-Methods",
        "GET,POST,PUT,DELETE,OPTIONS"
    )
    return response


# =========================
#   CONFIG DB
# =========================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "admin",
    "database": "la_media_docena",
    "port": 3306
}


def get_db():
    """Crea y regresa una conexión a MySQL."""
    return mysql.connector.connect(**DB_CONFIG)


# =========================
#   CONFIG UPLOADS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Servir archivos subidos (imágenes)."""
    return send_from_directory(UPLOAD_FOLDER, filename)


# =========================
#   RUTA DE PRUEBA
# =========================
@app.route("/api/ping")
def ping():
    return jsonify({"ok": True, "message": "Backend La Media Docena activo"})


# =========================
#   SUBIR IMAGEN (platillos)
# =========================
@app.route("/api/upload-imagen", methods=["POST", "OPTIONS"])
def upload_imagen():
    if request.method == "OPTIONS":
        return ("", 200)

    if "imagen" not in request.files:
        return jsonify({"ok": False, "error": "No se recibió archivo 'imagen'"}), 400

    file = request.files["imagen"]
    if file.filename == "":
        return jsonify({"ok": False, "error": "Nombre de archivo vacío"}), 400

    filename = file.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    file_url = f"http://127.0.0.1:5000/uploads/{filename}"

    return jsonify({"ok": True, "path": file_url})


# =========================
#   PLATILLOS / MENÚ
# =========================
@app.route("/api/platillos", methods=["GET"])
def get_platillos():
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT p.id, p.nombre, p.descripcion, p.precio,
                   p.id_categoria, c.nombre AS categoria,
                   p.disponible, p.imagen
            FROM platillos p
            LEFT JOIN categorias c ON p.id_categoria = c.id
            ORDER BY c.nombre, p.nombre
        """)
        rows = cur.fetchall()
        return jsonify(rows)
    except Error as e:
        print("Error en get_platillos:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/platillos", methods=["POST"])
def create_platillo():
    data = request.get_json() or {}
    nombre = data.get("nombre")
    precio = data.get("precio")
    id_categoria = data.get("id_categoria")
    descripcion = data.get("descripcion", "")
    disponible = data.get("disponible", True)
    imagen = data.get("imagen", "")

    if not nombre or precio is None:
        return jsonify({"ok": False, "error": "Nombre y precio son obligatorios"}), 400

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO platillos (nombre, descripcion, precio, id_categoria, disponible, imagen)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, precio, id_categoria, int(bool(disponible)), imagen))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({"ok": True, "id": new_id}), 201
    except Error as e:
        print("Error en create_platillo:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/platillos/<int:platillo_id>", methods=["PUT"])
def update_platillo(platillo_id):
    data = request.get_json() or {}

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()

        fields = []
        values = []

        for col in ["nombre", "descripcion", "precio", "id_categoria", "disponible", "imagen"]:
            if col in data:
                fields.append(f"{col} = %s")
                if col == "disponible":
                    values.append(int(bool(data[col])))
                else:
                    values.append(data[col])

        if not fields:
            return jsonify({"ok": False, "error": "No hay campos para actualizar"}), 400

        values.append(platillo_id)
        query = f"UPDATE platillos SET {', '.join(fields)} WHERE id = %s"
        cur.execute(query, tuple(values))
        conn.commit()

        return jsonify({"ok": True})
    except Error as e:
        print("Error en update_platillo:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/platillos/<int:platillo_id>", methods=["DELETE"])
def delete_platillo(platillo_id):
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM platillos WHERE id = %s", (platillo_id,))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en delete_platillo:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================
#   CATEGORÍAS
# =========================
@app.route("/api/categorias", methods=["GET"])
def get_categorias():
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, nombre, descripcion
            FROM categorias
            ORDER BY nombre
        """)
        rows = cur.fetchall()
        return jsonify(rows)
    except Error as e:
        print("Error en get_categorias:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/categorias", methods=["POST"])
def create_categoria():
    data = request.get_json() or {}
    nombre = data.get("nombre")
    descripcion = data.get("descripcion", "")

    if not nombre:
        return jsonify({"ok": False, "error": "El nombre es obligatorio"}), 400

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO categorias (nombre, descripcion)
            VALUES (%s, %s)
        """, (nombre, descripcion))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({"ok": True, "id": new_id}), 201
    except Error as e:
        print("Error en create_categoria:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/categorias/<int:cat_id>", methods=["PUT"])
def update_categoria(cat_id):
    data = request.get_json() or {}

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        fields = []
        values = []

        for col in ["nombre", "descripcion"]:
            if col in data:
                fields.append(f"{col} = %s")
                values.append(data[col])

        if not fields:
            return jsonify({"ok": False, "error": "No hay campos para actualizar"}), 400

        values.append(cat_id)
        query = f"UPDATE categorias SET {', '.join(fields)} WHERE id = %s"
        cur.execute(query, tuple(values))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en update_categoria:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/categorias/<int:cat_id>", methods=["DELETE"])
def delete_categoria(cat_id):
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM categorias WHERE id = %s", (cat_id,))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en delete_categoria:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================
#   RESERVACIONES
# =========================
@app.route("/api/reservaciones", methods=["POST"])
def create_reservacion():
    data = request.get_json() or {}
    nombre = data.get("nombre")
    telefono = data.get("telefono")
    personas = data.get("personas")
    fecha = data.get("fecha")
    hora = data.get("hora")

    if not (nombre and telefono and personas and fecha and hora):
        return jsonify({"ok": False, "error": "Todos los campos son obligatorios"}), 400

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO reservaciones (nombre, telefono, personas, fecha, hora)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, telefono, personas, fecha, hora))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({"ok": True, "id": new_id}), 201
    except Error as e:
        print("Error en create_reservacion:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/reservaciones", methods=["GET"])
def get_reservaciones():
    telefono = request.args.get("telefono")
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)

        if telefono:
            cur.execute("""
                SELECT id, nombre, telefono, personas, fecha, hora, estado, ts
                FROM reservaciones
                WHERE telefono = %s
                ORDER BY fecha DESC, hora DESC
            """, (telefono,))
        else:
            cur.execute("""
                SELECT id, nombre, telefono, personas, fecha, hora, estado, ts
                FROM reservaciones
                ORDER BY fecha DESC, hora DESC
            """)

        rows = cur.fetchall()

        # Normalizar tipos (date/time/timedelta) para JSON
        for r in rows:
            f = r.get("fecha")
            if isinstance(f, (date, datetime)):
                r["fecha"] = f.isoformat()

            h = r.get("hora")
            if isinstance(h, time):
                r["hora"] = h.strftime("%H:%M")
            elif isinstance(h, timedelta):
                total_seconds = int(h.total_seconds())
                hours = (total_seconds // 3600) % 24
                minutes = (total_seconds % 3600) // 60
                r["hora"] = f"{hours:02d}:{minutes:02d}"

            ts = r.get("ts")
            if isinstance(ts, (date, datetime)):
                r["ts"] = ts.isoformat(sep=" ")

        return jsonify(rows)

    except Error as e:
        print("Error en get_reservaciones:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/reservaciones/<int:res_id>", methods=["PUT", "OPTIONS"])
def update_reservacion(res_id):
    if request.method == "OPTIONS":
        return ("", 200)

    data = request.get_json(silent=True) or {}

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        fields = []
        values = []

        for col in ["nombre", "telefono", "personas", "fecha", "hora", "estado"]:
            if col in data:
                fields.append(f"{col} = %s")
                values.append(data[col])

        if not fields:
            return jsonify({"ok": False, "error": "No hay campos para actualizar"}), 400

        values.append(res_id)
        query = f"UPDATE reservaciones SET {', '.join(fields)} WHERE id = %s"
        cur.execute(query, tuple(values))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en update_reservacion:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================
#   CONTACTOS (MÓDULO CONTACTO)
# =========================
@app.route("/api/contactos", methods=["POST"])
def create_contacto():
    """
    Endpoint para el formulario público de contacto.
    Espera JSON con: nombre, correo, telefono, asunto, mensaje.
    estado se deja como 'nuevo' por default.
    """
    data = request.get_json() or {}
    nombre = data.get("nombre")
    correo = data.get("correo")
    telefono = data.get("telefono")
    asunto = data.get("asunto")
    mensaje = data.get("mensaje")

    if not (nombre and mensaje):
        return jsonify({"ok": False, "error": "Nombre y mensaje son obligatorios"}), 400

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO contactos (nombre, correo, telefono, asunto, mensaje)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, correo, telefono, asunto, mensaje))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({"ok": True, "id": new_id}), 201
    except Error as e:
        print("Error en create_contacto:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/contactos", methods=["GET"])
def get_contactos():
    """
    Lista de mensajes de contacto.
    Parámetro opcional: ?estado=nuevo|en_proceso|cerrado
    """
    estado = request.args.get("estado")
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)

        if estado:
            cur.execute("""
                SELECT id, nombre, correo, telefono, asunto, mensaje, ts, estado
                FROM contactos
                WHERE estado = %s
                ORDER BY ts DESC
            """, (estado,))
        else:
            cur.execute("""
                SELECT id, nombre, correo, telefono, asunto, mensaje, ts, estado
                FROM contactos
                ORDER BY ts DESC
            """)

        rows = cur.fetchall()

        # Normalizar ts (datetime) a string
        for r in rows:
            ts = r.get("ts")
            if isinstance(ts, (date, datetime)):
                r["ts"] = ts.isoformat(sep=" ")

        return jsonify(rows)
    except Error as e:
        print("Error en get_contactos:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/contactos/<int:contacto_id>", methods=["PUT"])
def update_contacto(contacto_id):
    """
    Para el admin: actualizar estado o campos de un mensaje.
    Puede recibir: nombre, correo, telefono, asunto, mensaje, estado
    """
    data = request.get_json() or {}

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        fields = []
        values = []

        for col in ["nombre", "correo", "telefono", "asunto", "mensaje", "estado"]:
            if col in data:
                # validar estado permitido
                if col == "estado" and data[col] not in ("nuevo", "en_proceso", "cerrado"):
                    continue
                fields.append(f"{col} = %s")
                values.append(data[col])

        if not fields:
            return jsonify({"ok": False, "error": "No hay campos para actualizar"}), 400

        values.append(contacto_id)
        query = f"UPDATE contactos SET {', '.join(fields)} WHERE id = %s"
        cur.execute(query, tuple(values))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en update_contacto:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/contactos/<int:contacto_id>", methods=["DELETE"])
def delete_contacto(contacto_id):
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM contactos WHERE id = %s", (contacto_id,))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en delete_contacto:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================
#   RESEÑAS
# =========================
@app.route("/api/resenas", methods=["POST"])
def create_resena():
    data = request.get_json() or {}
    nombre = data.get("nombre")
    calificacion = data.get("calificacion")
    comentario = data.get("comentario")

    if not (nombre and calificacion and comentario):
        return jsonify({"ok": False, "error": "Todos los campos son obligatorios"}), 400

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO resenas (nombre, calificacion, comentario)
            VALUES (%s, %s, %s)
        """, (nombre, calificacion, comentario))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({"ok": True, "id": new_id}), 201
    except Error as e:
        print("Error en create_resena:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/resenas", methods=["GET"])
def get_resenas():
    estado = request.args.get("estado")
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        if estado:
            cur.execute("""
                SELECT * FROM resenas
                WHERE estado = %s
                ORDER BY ts DESC
            """, (estado,))
        else:
            cur.execute("""
                SELECT * FROM resenas
                ORDER BY ts DESC
            """)
        rows = cur.fetchall()
        return jsonify(rows)
    except Error as e:
        print("Error en get_resenas:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/resenas/<int:resena_id>", methods=["PUT"])
def update_resena(resena_id):
    data = request.get_json() or {}

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        fields = []
        values = []

        for col in ["nombre", "calificacion", "comentario", "estado"]:
            if col in data:
                fields.append(f"{col} = %s")
                values.append(data[col])

        if not fields:
            return jsonify({"ok": False, "error": "No hay campos para actualizar"}), 400

        values.append(resena_id)
        query = f"UPDATE resenas SET {', '.join(fields)} WHERE id = %s"
        cur.execute(query, tuple(values))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en update_resena:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/resenas/<int:resena_id>", methods=["DELETE"])
def delete_resena(resena_id):
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM resenas WHERE id = %s", (resena_id,))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en delete_resena:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================
#   PEDIDOS
# =========================
@app.route("/api/pedidos", methods=["POST"])
def create_pedido():
    data = request.get_json() or {}
    items = data.get("items", [])
    total = data.get("total")
    customer = data.get("customer", "Invitado")

    if not items or total is None:
        return jsonify({"ok": False, "error": "Faltan items o total"}), 400

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO pedidos (cliente_nombre, total)
            VALUES (%s, %s)
        """, (customer, total))
        pedido_id = cur.lastrowid

        for item in items:
            id_platillo = item.get("id_platillo")
            nombre_platillo = item.get("nombre_platillo")
            precio = item.get("precio_unitario")
            qty = item.get("cantidad")
            subtotal = item.get("subtotal")

            cur.execute("""
                INSERT INTO pedido_detalle
                  (id_pedido, id_platillo, nombre_platillo, precio_unitario, cantidad, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (pedido_id, id_platillo, nombre_platillo, precio, qty, subtotal))

        conn.commit()
        return jsonify({"ok": True, "id": pedido_id}), 201
    except Error as e:
        print("Error en create_pedido:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/pedidos", methods=["GET"])
def get_pedidos():
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
              p.id,
              p.cliente_nombre,
              p.total,
              p.estado,
              p.fecha_hora
            FROM pedidos p
            ORDER BY p.fecha_hora DESC
        """)
        pedidos = cur.fetchall()

        for ped in pedidos:
            cur.execute("""
                SELECT nombre_platillo, precio_unitario, cantidad, subtotal
                FROM pedido_detalle
                WHERE id_pedido = %s
            """, (ped["id"],))
            ped["detalles"] = cur.fetchall()

        return jsonify(pedidos)
    except Error as e:
        print("Error en get_pedidos:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/pedidos/<int:pedido_id>", methods=["PUT"])
def update_pedido(pedido_id):
    data = request.get_json() or {}
    estado = data.get("estado")

    if not estado:
        return jsonify({"ok": False, "error": "Estado requerido"}), 400

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE pedidos SET estado = %s WHERE id = %s", (estado, pedido_id))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en update_pedido:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================
#   ABOUT / ACERCA DE
# =========================
@app.route("/api/about", methods=["GET"])
def get_about():
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM about WHERE id = 1")
        row = cur.fetchone()
        return jsonify(row or {})
    except Error as e:
        print("Error en get_about:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/about", methods=["PUT"])
def update_about():
    data = request.get_json() or {}
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        fields = []
        values = []

        for col in ["nombre", "descripcion", "mision", "vision"]:
            if col in data:
                fields.append(f"{col} = %s")
                values.append(data[col])

        if not fields:
            return jsonify({"ok": False, "error": "No hay campos para actualizar"}), 400

        values.append(1)
        query = f"UPDATE about SET {', '.join(fields)} WHERE id = %s"
        cur.execute(query, tuple(values))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en update_about:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================
#   USUARIOS / LOGIN
# =========================
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    correo = data.get("correo")
    password = data.get("password")

    if not (correo and password):
        return jsonify({"ok": False, "error": "Correo y contraseña requeridos"}), 400

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, nombre, correo, role, telefono, activo
            FROM usuarios
            WHERE correo = %s AND password = %s AND activo = 1
        """, (correo, password))
        user = cur.fetchone()

        if not user:
            return jsonify({"ok": False, "error": "Credenciales inválidas"}), 401

        return jsonify({"ok": True, "user": user})
    except Error as e:
        print("Error en login:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/usuarios", methods=["GET"])
def get_usuarios():
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, nombre, correo, role, telefono, activo, fecha_registro
            FROM usuarios
            ORDER BY id ASC
        """)
        rows = cur.fetchall()
        return jsonify(rows)
    except Error as e:
        print("Error en get_usuarios:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/usuarios", methods=["POST"])
def create_usuario():
    data = request.get_json() or {}
    nombre = data.get("nombre")
    correo = data.get("correo")
    password = data.get("password")
    role = data.get("role", "user")
    telefono = data.get("telefono")

    if not (nombre and correo and password):
        return jsonify({"ok": False, "error": "Nombre, correo y password son obligatorios"}), 400

    if role not in ("admin", "user"):
        role = "user"

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO usuarios (nombre, correo, password, role, telefono)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, correo, password, role, telefono))
        conn.commit()
        new_id = cur.lastrowid
        return jsonify({"ok": True, "id": new_id}), 201
    except Error as e:
        print("Error en create_usuario:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/usuarios/<int:user_id>", methods=["PUT"])
def update_usuario(user_id):
    data = request.get_json() or {}

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        fields = []
        values = []

        for col in ["nombre", "correo", "password", "role", "telefono", "activo"]:
            if col in data:
                val = data[col]
                if col == "role" and val not in ("admin", "user"):
                    continue
                fields.append(f"{col} = %s")
                values.append(val)

        if not fields:
            return jsonify({"ok": False, "error": "No hay campos para actualizar"}), 400

        values.append(user_id)
        query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = %s"
        cur.execute(query, tuple(values))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en update_usuario:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/api/usuarios/<int:user_id>", methods=["DELETE"])
def delete_usuario(user_id):
    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
        conn.commit()
        return jsonify({"ok": True})
    except Error as e:
        print("Error en delete_usuario:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================
#   MAIN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
