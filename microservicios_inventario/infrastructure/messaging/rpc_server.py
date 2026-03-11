import pika
import json
from application.use_cases import ProductoUseCases

casos_uso = ProductoUseCases()

credentials = pika.PlainCredentials('admin', 'secretpassword')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=credentials)
)
channel = connection.channel()

channel.queue_declare(queue='rpc_queue_productos')

def procesar_peticion(payload):
    accion = payload.get("accion")
    datos = payload.get("datos")

    try:
        if accion == "crear_producto":
            resultado = casos_uso.crear_producto(datos)
            # si la creación devolvió un id, consideramos que fue exitosa y generamos
            # un reporte de alta en un archivo de texto
            try:
                if resultado and isinstance(resultado, dict) and resultado.get("id") is not None:
                    with open("reporte_altas.txt", "a", encoding="utf-8") as f:
                        from datetime import datetime
                        ts = datetime.utcnow().isoformat()
                        f.write(f"[{ts}] Alta producto: {resultado}\n")
            except Exception:
                # no queremos romper el flujo por errores de I/O
                pass
            return {"status": "exito", "data": resultado}
        elif accion == "obtener_producto":
            resultado = casos_uso.obtener_producto(datos.get("id"))
            if resultado:
                return {"status": "exito", "data": resultado}
            return {"status": "error", "mensaje": "Producto no encontrado"}
        else:
            return {"status": "error", "mensaje": "Acción no reconocida"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def on_request(ch, method, props, body):
    payload = json.loads(body)
    respuesta = procesar_peticion(payload)

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(respuesta)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue_productos', on_message_callback=on_request)

channel.start_consuming()

