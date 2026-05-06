import json
import os
from datetime import datetime, timezone
import boto3
from typing import Optional, Tuple, Any
import urllib.request
import json

API_KEY = os.environ.get("API_KEY")
SNAPSHOTS_BUCKET = os.environ.get("SNAPSHOTS_BUCKET")

s3_client = boto3.client("s3")

def obtener_datos_clima(ciudad: str):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": ciudad,
        "appid": API_KEY,
        "units": "metric",
        "lang": "es"
    }
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    try:
        req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data, None
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode()
        return None, f"Error de OpenWeatherMap: {error_msg}"
    except Exception as e:
        return None, f"Error del servidor: {str(e)}"
    
# Construccion de la respuesta de lambda 
def _response(status_code: int, body_dict: dict) -> dict:
    
    return {
        "statusCode": status_code,
        "body": json.dumps(body_dict, ensure_ascii=False),
        "headers": {
            "Content-Type": "application/json"
        }
    }
def _error_response(status_code: int, detail: str) -> dict:
    return _response(status_code, {"detail": detail})

def _get_clima(event: dict) -> dict:
    # extraer query parameters
    qs = event.get("queryStringParameters") or {} # diccionario con los parametros de la url
    ciudad = qs.get("ciudad")
    
    if not ciudad:
        return _error_response(400, "Falta parámetro 'ciudad'")
    
    data, error = obtener_datos_clima(ciudad)
    
    if error:
        return _error_response(400, error)
    
    return _response(200, data)

def _post_snapshot(event: dict) -> dict:
    
    #leer body
    body_str = event.get("body") or "{}"
    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        return _error_response(400, "No es un JSON")
    
    ciudad = body.get("ciudad")
    nota = body.get("nota")
    if not ciudad:
        return _error_response(400, "Falta campo 'ciudad' en body")
    # obtener clima actual
    clima_data, error = obtener_datos_clima(ciudad)
    if error:
        return _error_response(400, error)
    
    # construir snapshot
    timestamp_utc = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z').replace(':','-')
    ciudad_limpia = ciudad.lower().replace(" ","_")
    snapshot = {
        "ciudad": ciudad,
        "nota": nota,
        "timestamp_utc": timestamp_utc,
        "clima": clima_data
    }
    
    #key en s3 
    key = f"snapshots/{ciudad_limpia}_{timestamp_utc}.json"
    try:
        s3_client.put_object(
            Bucket=SNAPSHOTS_BUCKET,
            Key=key,
            Body=json.dumps(snapshot, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json"
        )
    except Exception as e:
        return _error_response(500, f"Error al guardar en S3: {str(e)}")
    
    
    #print(f"[FAKE SAVE] Guardando snapshot en S3 con Key={key}")
    #print(f"Contenido del snapshot:\n{json.dumps(snapshot, ensure_ascii=False, indent=2)}")
    
    temperatura = clima_data.get("main", {}).get("temp")
    descripcion = clima_data.get("weather", [{}])[0].get("description")
    
    return _response(201, {
        "mensaje": "Snapshot se guardo",
        "ruta_s3": f"s3://{SNAPSHOTS_BUCKET}/{key}",
        "temperatura": temperatura,
        "descripcion": descripcion,
        "timestamp": timestamp_utc
        
    })
    
def _get_snapshots(ciudad: str) -> dict:
    
    ciudad_normalizada = ciudad.lower().replace(" ", "_")
    prefix = f"snapshots/{ciudad_normalizada}_"
    
    try:
        
        #listar los objetos con el prefix
        response =s3_client.list_objects_v2(
            Bucket=SNAPSHOTS_BUCKET,
            Prefix=prefix
        )
    except Exception as e:
        return _error_response(500, f"Error al listar S3: {str(e)}")
    
    if "Contents" not in response:
        return _response(200, [])
    
    snapshots= []
    for obj in response["Contents"]:
        key = obj["Key"]
        
        try:
            s3_obj = s3_client.get_object(Bucket=SNAPSHOTS_BUCKET, Key=key)
            data = json.loads(s3_obj["Body"].read().decode("utf-8"))
            
        except Exception:
            continue
        
        timestamp= data.get("timestamp_utc")
        nota = data.get("nota")
        clima = data.get("clima", {})
        temperatura =clima.get("main", {}).get("temp")
        descripcion = clima.get("weather", [{}])[0].get("description")
            
        snapshots.append({
            "archivo": key.split("/")[-1],
            "timestamp": timestamp,
            "nota": nota,
            "temperatura": temperatura,
            "descripcion": descripcion
        })
        
    snapshots.sort(key=lambda x: x["archivo"])
    return _response(200, snapshots)

# handle que invoca lambda
def handler(event: dict, context: Any) -> dict:
    
    try:
        # Extraer método HTTP y ruta desde el evento de Function URL
        http_method = event.get("requestContext", {}).get("http", {}).get("method")
        path = event.get("rawPath", "")
        
        # Ruteo manual
        if http_method == "GET" and path == "/clima":
            return _get_clima(event)
        elif http_method == "POST" and path == "/clima/snapshot":
            return _post_snapshot(event)
        elif http_method == "GET" and path.startswith("/clima/snapshots/"):
            # Extraer ciudad de la ruta: /clima/snapshots/'ciudad'
            # Usamos split y tomamos el último segmento
            parts = path.split("/")
            if len(parts) >= 4:
                ciudad = parts[3]  # [0]:'', [1]:'clima', [2]:'snapshots', [3]:'ciudad'
                if ciudad:
                    return _get_snapshots(ciudad)
        # Si no coincidió ninguna ruta
        return _error_response(404, "Ruta no encontrada")
    except Exception as e:
        return _error_response(500,f"Error interno: {str(e)}")
    
    
