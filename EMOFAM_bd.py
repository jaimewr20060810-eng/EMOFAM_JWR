import sqlite3

conexion = sqlite3.connect("emofam.db")
conexion.execute("PRAGMA foreign_keys = ON")
cursor = conexion.cursor()

#tablas

cursor.execute("""
CREATE TABLE IF NOT EXISTS FAMILIA (
    id_familia INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_familia TEXT NOT NULL,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS USUARIO (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    id_familia INTEGER,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    edad INTEGER,
    correo TEXT NOT NULL UNIQUE,
    telefono TEXT,
    rol TEXT NOT NULL,
    contrasena_hash TEXT NOT NULL,
    FOREIGN KEY (id_familia)
        REFERENCES FAMILIA(id_familia)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ACTIVIDAD (
    id_actividad INTEGER PRIMARY KEY AUTOINCREMENT,
    id_familia INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    fecha_propuesta TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_familia)
        REFERENCES FAMILIA(id_familia)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS PARTICIPACION_ACTIVIDAD (
    id_usuario INTEGER NOT NULL,
    id_actividad INTEGER NOT NULL,
    PRIMARY KEY (id_usuario, id_actividad),
    FOREIGN KEY (id_usuario)
        REFERENCES USUARIO(id_usuario),
    FOREIGN KEY (id_actividad)
        REFERENCES ACTIVIDAD(id_actividad)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS REGISTRO_EMOCIONAL (
    id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_actividad INTEGER,
    fecha TEXT DEFAULT CURRENT_TIMESTAMP,
    emocion TEXT NOT NULL,
    comentario TEXT,
    FOREIGN KEY (id_usuario)
        REFERENCES USUARIO(id_usuario),
    FOREIGN KEY (id_actividad)
        REFERENCES ACTIVIDAD(id_actividad)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS MENSAJE (
    id_mensaje INTEGER PRIMARY KEY AUTOINCREMENT,
    id_familia INTEGER NOT NULL,
    id_usuario_emisor INTEGER NOT NULL,
    contenido TEXT NOT NULL,
    fecha_envio TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_familia)
        REFERENCES FAMILIA(id_familia),
    FOREIGN KEY (id_usuario_emisor)
        REFERENCES USUARIO(id_usuario)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS NOTIFICACION (
    id_notificacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario_destinatario INTEGER,
    id_familia_destinataria INTEGER,
    texto TEXT NOT NULL,
    fecha_envio TEXT DEFAULT CURRENT_TIMESTAMP,
    leida INTEGER DEFAULT 0,
    FOREIGN KEY (id_usuario_destinatario)
        REFERENCES USUARIO(id_usuario),
    FOREIGN KEY (id_familia_destinataria)
        REFERENCES FAMILIA(id_familia)
)
""")

conexion.commit()



def existe_familia(cursor, nombre):
    cursor.execute(
        "SELECT id_familia FROM FAMILIA WHERE nombre_familia = ?",
        (nombre,)
    )

    familia = cursor.fetchone()

    if familia is not None:
        return True
    else:
        return False


def existe_usuario(cursor, correo):
    cursor.execute(
        "SELECT id_usuario FROM USUARIO WHERE correo = ?",
        (correo,)
    )

    usuario = cursor.fetchone()

    if usuario is not None:
        return True
    else:
        return False


def imprimir_familias(cursor):
    print()
    print("IMPRIMIR FAMILIAS")

    cursor.execute(
        "SELECT id_familia, nombre_familia, fecha_creacion FROM FAMILIA"
    )

    familias = cursor.fetchall()

    for familia in familias:
        print(
            "ID:", familia[0],
            "- Nombre:", familia[1],
            "- Fecha:", familia[2]
        )


def crear_familia(conexion, cursor):
    print()
    print("CREAR FAMILIA")

    nombre = input("Dame el nombre de la familia: ")

    if existe_familia(cursor, nombre):
        print("ERROR: La familia ya existe")
        return

    try:
        cursor.execute(
            "INSERT INTO FAMILIA(nombre_familia) VALUES (?)",
            (nombre,)
        )

        conexion.commit()

        print("La familia <" + nombre + "> se ha creado correctamente")

    except sqlite3.Error:
        conexion.rollback()
        print("ERROR: No se ha podido crear la familia")


def imprimir_usuarios(cursor):
    print()
    print("IMPRIMIR USUARIOS")

    cursor.execute("""
        SELECT USUARIO.id_usuario, USUARIO.nombre, USUARIO.apellidos,
               USUARIO.correo, USUARIO.rol, FAMILIA.nombre_familia
        FROM USUARIO
        LEFT JOIN FAMILIA
        ON USUARIO.id_familia = FAMILIA.id_familia
    """)

    usuarios = cursor.fetchall()

    for usuario in usuarios:
        print(
            "ID:", usuario[0],
            "- Nombre:", usuario[1], usuario[2],
            "- Correo:", usuario[3],
            "- Rol:", usuario[4],
            "- Familia:", usuario[5]
        )


def insertar_usuario(conexion, cursor):
    print()
    print("INSERTAR USUARIO")

    correo = input("Dame el correo: ")

    if existe_usuario(cursor, correo):
        print("ERROR: El usuario ya existe")
        return

    nombre = input("Dame el nombre: ")
    apellidos = input("Dame los apellidos: ")

    try:
        edad_texto = input("Dame la edad: ")
        edad = int(edad_texto) if edad_texto else None
    except ValueError:
        print("ERROR: La edad debe ser un número")
        return

    telefono = input("Dame el teléfono: ")
    rol = input("Dame el rol: ")
    contrasena = input("Dame la contraseña: ")

    id_familia_texto = input("Dame el ID de la familia (Enter si no tiene): ")

    try:
        id_familia = int(id_familia_texto) if id_familia_texto else None

        cursor.execute("""
            INSERT INTO USUARIO
            (id_familia, nombre, apellidos, edad, correo,
             telefono, rol, contrasena_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_familia, nombre, apellidos, edad, correo,
              telefono, rol, contrasena))

        conexion.commit()

        print("El usuario <" + nombre + "> se ha insertado correctamente")

    except sqlite3.Error:
        conexion.rollback()
        print("ERROR: No se ha podido insertar el usuario")


def borrar_usuario(conexion, cursor):
    print()
    print("BORRAR USUARIO")

    correo = input("Dame el correo del usuario: ")

    if not existe_usuario(cursor, correo):
        print("ERROR: El usuario no existe")
        return

    try:
        cursor.execute(
            "DELETE FROM USUARIO WHERE correo = ?",
            (correo,)
        )

        conexion.commit()

        print("Se ha eliminado el usuario <" + correo + "> correctamente")

    except sqlite3.Error:
        conexion.rollback()
        print("ERROR: No se ha podido eliminar el usuario")


def crear_actividad(conexion, cursor):
    print()
    print("CREAR ACTIVIDAD")

    try:
        id_familia = int(input("Dame el ID de la familia: "))
    except ValueError:
        print("ERROR: El ID debe ser un número")
        return

    titulo = input("Dame el título de la actividad: ")
    descripcion = input("Dame la descripción: ")

    try:
        cursor.execute("""
            INSERT INTO ACTIVIDAD(id_familia, titulo, descripcion)
            VALUES (?, ?, ?)
        """, (id_familia, titulo, descripcion))

        conexion.commit()

        print("La actividad <" + titulo + "> se ha creado correctamente")

    except sqlite3.Error:
        conexion.rollback()
        print("ERROR: No se ha podido crear la actividad")


def imprimir_actividades(cursor):
    print()
    print("IMPRIMIR ACTIVIDADES")

    cursor.execute("""
        SELECT ACTIVIDAD.id_actividad, ACTIVIDAD.titulo,
               ACTIVIDAD.descripcion, FAMILIA.nombre_familia
        FROM ACTIVIDAD
        INNER JOIN FAMILIA
        ON ACTIVIDAD.id_familia = FAMILIA.id_familia
    """)

    actividades = cursor.fetchall()

    for actividad in actividades:
        print(
            "ID:", actividad[0],
            "- Título:", actividad[1],
            "- Descripción:", actividad[2],
            "- Familia:", actividad[3]
        )


def registrar_emocion(conexion, cursor):
    print()
    print("REGISTRAR EMOCIÓN")

    try:
        id_usuario = int(input("Dame el ID del usuario: "))
    except ValueError:
        print("ERROR: El ID debe ser un número")
        return

    emocion = input("Dame la emoción: ")
    comentario = input("Dame un comentario: ")
    id_actividad_texto = input("ID de actividad (Enter si no corresponde): ")

    try:
        id_actividad = int(id_actividad_texto) if id_actividad_texto else None

        cursor.execute("""
            INSERT INTO REGISTRO_EMOCIONAL
            (id_usuario, id_actividad, emocion, comentario)
            VALUES (?, ?, ?, ?)
        """, (id_usuario, id_actividad, emocion, comentario))

        conexion.commit()

        print("El registro emocional se ha guardado correctamente")

    except sqlite3.Error:
        conexion.rollback()
        print("ERROR: No se ha podido guardar el registro emocional")


def imprimir_registros_emocionales(cursor):
    print()
    print("IMPRIMIR REGISTROS EMOCIONALES")

    cursor.execute("""
        SELECT REGISTRO_EMOCIONAL.id_registro,
               USUARIO.nombre,
               REGISTRO_EMOCIONAL.fecha,
               REGISTRO_EMOCIONAL.emocion,
               REGISTRO_EMOCIONAL.comentario
        FROM REGISTRO_EMOCIONAL
        INNER JOIN USUARIO
        ON REGISTRO_EMOCIONAL.id_usuario = USUARIO.id_usuario
        ORDER BY REGISTRO_EMOCIONAL.fecha DESC
    """)

    registros = cursor.fetchall()

    for registro in registros:
        print(
            "ID:", registro[0],
            "- Usuario:", registro[1],
            "- Fecha:", registro[2],
            "- Emoción:", registro[3],
            "- Comentario:", registro[4]
        )


def enviar_mensaje(conexion, cursor):
    print()
    print("ENVIAR MENSAJE")

    try:
        id_familia = int(input("Dame el ID de la familia: "))
        id_usuario = int(input("Dame el ID del usuario emisor: "))
    except ValueError:
        print("ERROR: Los IDs deben ser números")
        return

    contenido = input("Dame el contenido del mensaje: ")

    try:
        cursor.execute("""
            INSERT INTO MENSAJE
            (id_familia, id_usuario_emisor, contenido)
            VALUES (?, ?, ?)
        """, (id_familia, id_usuario, contenido))

        conexion.commit()

        print("El mensaje se ha enviado correctamente")

    except sqlite3.Error:
        conexion.rollback()
        print("ERROR: No se ha podido enviar el mensaje")


def imprimir_mensajes(cursor):
    print()
    print("IMPRIMIR MENSAJES")

    cursor.execute("""
        SELECT MENSAJE.id_mensaje, FAMILIA.nombre_familia,
               USUARIO.nombre, MENSAJE.contenido, MENSAJE.fecha_envio
        FROM MENSAJE
        INNER JOIN FAMILIA
        ON MENSAJE.id_familia = FAMILIA.id_familia
        INNER JOIN USUARIO
        ON MENSAJE.id_usuario_emisor = USUARIO.id_usuario
        ORDER BY MENSAJE.fecha_envio DESC
    """)

    mensajes = cursor.fetchall()

    for mensaje in mensajes:
        print(
            "ID:", mensaje[0],
            "- Familia:", mensaje[1],
            "- Emisor:", mensaje[2],
            "- Mensaje:", mensaje[3],
            "- Fecha:", mensaje[4]
        )


def mostrar_menu():
    print()
    print("=================================")
    print("             EMOFAM")
    print("=================================")
    print(" 1 - Imprimir familias")
    print(" 2 - Crear familia")
    print(" 3 - Insertar usuario")
    print(" 4 - Imprimir usuarios")
    print(" 5 - Borrar usuario")
    print(" 6 - Crear actividad")
    print(" 7 - Imprimir actividades")
    print(" 8 - Registrar emoción")
    print(" 9 - Imprimir registros emocionales")
    print("10 - Enviar mensaje")
    print("11 - Imprimir mensajes")
    print(" 0 - SALIR")
    print("--------------------------")


# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================

def main():
    try:
        opcion = ""

        while opcion != "0":
            mostrar_menu()
            opcion = input("Dame la opción: ")

            if opcion == "1":
                imprimir_familias(cursor)

            elif opcion == "2":
                crear_familia(conexion, cursor)

            elif opcion == "3":
                insertar_usuario(conexion, cursor)

            elif opcion == "4":
                imprimir_usuarios(cursor)

            elif opcion == "5":
                borrar_usuario(conexion, cursor)

            elif opcion == "6":
                crear_actividad(conexion, cursor)

            elif opcion == "7":
                imprimir_actividades(cursor)

            elif opcion == "8":
                registrar_emocion(conexion, cursor)

            elif opcion == "9":
                imprimir_registros_emocionales(cursor)

            elif opcion == "10":
                enviar_mensaje(conexion, cursor)

            elif opcion == "11":
                imprimir_mensajes(cursor)

            elif opcion == "0":
                print("Programa terminado.")

            else:
                print("ERROR: La opción no existe")

    except sqlite3.Error as error:
        print("ERROR:", error)

    finally:
        conexion.close()


main()
