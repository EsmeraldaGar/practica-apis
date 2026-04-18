from fastapi import FastAPI, Query
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

    #?q=London,uk&APPID=a7064514ee7eb431bc63683bfca93ddb
    params = {
        "q": ciudad,
        "appid": API_KEY,
        "lang": "es" # descripciones en español
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    return data






