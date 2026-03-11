import psycopg2

class PostgresProductoRepository:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="inventario_db",
            user="admin",
            password="secretpassword",
            host="localhost",
            port="5434"
        )
        self.cursor = self.conn.cursor()
        self._crear_tabla()

    def _crear_tabla(self):
        # create productos table if it does not exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100),
                precio FLOAT,
                stock INTEGER
            )
        """)
        # also create a simple report table to log altas (product registrations)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reportes (
                id SERIAL PRIMARY KEY,
                producto_id INTEGER NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def guardar(self, producto_dict):
        self.cursor.execute(
            "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s) RETURNING id",
            (producto_dict['nombre'], producto_dict['precio'], producto_dict['stock'])
        )
        new_id = self.cursor.fetchone()[0]
        # commit the product insertion first
        self.conn.commit()
        # after confirming the insert, log a report of type 'alta'
        try:
            self.guardar_reporte(new_id, tipo="alta")
        except Exception:
            # if reporting fails, we don't want to crash the whole flow; just log or ignore
            pass
        return new_id

    def obtener_por_id(self, producto_id):
        self.cursor.execute("SELECT id, nombre, precio, stock FROM productos WHERE id = %s", (producto_id,))
        row = self.cursor.fetchone()
        if row:
            return {"id": row[0], "nombre": row[1], "precio": row[2], "stock": row[3]}
        return None

    def guardar_reporte(self, producto_id, tipo="alta"):
        """Inserta un registro en la tabla `reportes`.
        Se puede usar para marcar altas, bajas u otros eventos sobre productos.
        """
        self.cursor.execute(
            "INSERT INTO reportes (producto_id, tipo) VALUES (%s, %s)",
            (producto_id, tipo)
        )
        self.conn.commit()