from fastapi import FastAPI, Query, HTTPException
import httpx
import os
from dotenv import load_dotenv

# cargar variables desde el archivo .env
load_dotenv()

app = FastAPI()

# la API key
API_KEY = os.getenv("API_KEY")

@app.get("/clima")

                                    # hacer que el parametro sea obligatorio, agremos descrpcion
async def obtener_clima(ciudad: str = Query(..., description= "Nombre de la ciudad")):

    # la construccion de la url weathermap
    url = "http://api.openweathermap.org/data/2.5/weather"

    # ?q=London,uk&APPID=a7064514ee7eb431bc63683bfca93ddb
    params = {
        "q": ciudad,
        "appid": API_KEY,
        "units": "metric", # temperatura en cels
        "lang": "es" # descripciones en español
    }


    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

            response.raise_for_status() # http es codigo 404
            data = response.json()

                        # captura error y traducir a errores Bad Request
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"Error de OpenWeatherMap: {e.response.text}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")


    return data






