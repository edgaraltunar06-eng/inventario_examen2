from infrastructure.database.postgres_repo import PostgresProductoRepository

class ProductoUseCases:
    def __init__(self):
        self.repo = PostgresProductoRepository()

    def crear_producto(self, datos_producto):
        nuevo_id = self.repo.guardar(datos_producto)
        return {"id": nuevo_id, **datos_producto}

    def obtener_producto(self, producto_id):
        return self.repo.obtener_por_id(producto_id)