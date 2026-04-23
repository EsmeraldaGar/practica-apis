from fastapi import FastAPI, Query, HTTPException
import httpx, json
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from pathlib import Path

# cargar variables desde el archivo .env
load_dotenv()

app = FastAPI()

# la API key
API_KEY = os.getenv("API_KEY")


# modelo Pydantic
class SnapshotRequest(BaseModel):
    ciudad: str
    nota: Optional[str] = None



 # extraer la llamada a OpenWeatherMap a una función auxiliar reutilizable para get y post
async def obtener_datos_clima(ciudad: str):
    
    
    
    # la construccion de la url weathermap
    url = "https://api.openweathermap.org/data/2.5/weather"

    # ?q=London,uk&APPID=a7064514ee7eb431bc63683bfca93ddb
    params = {
        "q": ciudad,
        "appid": API_KEY,
        "units": "metric", # temperatura en cels
        "lang": "es" # descripciones en español
    }
    en_lambda = os.environ.get("AWS_EXECUTION_ENV") is not None
    verify_ssl = en_lambda
    
    try:
        async with httpx.AsyncClient(verify=verify_ssl) as client:
            response = await client.get(url, params=params)

            response.raise_for_status() # http es codigo 404
            data = response.json()
            return data

                        # captura error y traducir a errores Bad Request
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"Error de OpenWeatherMap: {e.response.text}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")
    



@app.get("/clima")
                                    # hacer que el parametro sea obligatorio, agremos descrpcion
async def obtener_clima(ciudad: str = Query(..., description= "Nombre de la ciudad")):
    data = await obtener_datos_clima(ciudad)
    return data


@app.post("/clima/snapshot")
async def crear_snapshot(request: SnapshotRequest):
    
    # ontener datos con funcion auxiliar 
    clima_data = await obtener_datos_clima(request.ciudad)
    
    # generar timestamp "2026-04-20T15-30-00Z"
    timestamp_utc = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z').replace(':','-')
    
    # objeto snapshot 
    snapshot = {
        "ciudad": request.ciudad,
        "nota": request.nota,
        "timestamp_utc": timestamp_utc,
        "clima": clima_data
    }
    
    #crear carpeta
    Path("snapshots").mkdir(exist_ok=True)
    
    # nombre del archivo, limpiar espacios, carateres
    ciudad_limpia = request.ciudad.lower().replace(" ","_")
    nombre_archivo = f"{ciudad_limpia}_{timestamp_utc}.json"
    ruta_archivo = Path("snapshots")/nombre_archivo
    
    # guardar
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
    # Devolver un resumen con la ruta del archivo, temperatura y descripción
    temperatura =clima_data.get("main", {}).get("temp")
    descripcion = clima_data.get("weather", [{}])[0].get("description")
    
    return {
        "mensaje": "Snapshot se guardo",
        "archivo": str(ruta_archivo),
        "temperatura": temperatura,
        "descripcion": descripcion,
        "timestamp": timestamp_utc
        
    }
    
    # usar path parameter
@app.get("/clima/snapshots/{ciudad}")
async def listar_snapshots(ciudad: str):
    
    # limpiar el nombre de la ciudad como en el post
    ciudad_normalizada = ciudad.lower().replace(" ", "_")
    
    carpeta = Path("snapshots")
    if not carpeta.exists():
        return []
    
    # buscar archivos que coincidan con el patron nombre ciudad y termine .json 
    patron = f"{ciudad_normalizada}_*.json"
    archivos = list(carpeta.glob(patron))
    
   
    snapshots= []
    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
            
            # extraemos lo que nos interesa
            timestamp= datos.get("timestamp_utc")
            nota = datos.get("nota")
            clima = datos.get("clima", {})
            temperatura =clima.get("main", {}).get("temp")
            description = clima.get("weather", [{}])[0].get("description")
            
            snapshots.append({
                "archivo": archivo.name,
                "timestamp": timestamp,
                "nota": nota,
                "temperatura": temperatura,
                "descripcion": description
            })
            
        except Exception as e:
            continue
        
    # orden cronológico
    snapshots.sort(key=lambda x: x["archivo"])
    return snapshots
                
                
    




