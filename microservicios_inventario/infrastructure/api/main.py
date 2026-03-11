from fastapi import FastAPI
import json
import uvicorn
from infrastructure.messaging.rpc_client import RpcClient
from domain.models import Producto

app = FastAPI(title="Microservicio de Inventarios")
rpc = RpcClient()

@app.post("/inventario/")
async def crear_Producto(producto: Producto):
    payload = {
        "accion": "crear_producto",
        "datos": producto.model_dump()
    }
    respuesta = rpc.call(json.dumps(payload))
    return respuesta

@app.get("/inventario/{producto_id}")
async def obtener_producto(producto_id: int):
    payload = {
        "accion": "obtener_producto",
        "datos": {"id": producto_id}
    }
    respuesta = rpc.call(json.dumps(payload))
    return respuesta

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)