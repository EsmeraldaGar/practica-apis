#!/usr/bin/env python
import os
import sys
import json
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("API_KEY")
SNAPSHOTS_BUCKET = os.environ.get("SNAPSHOTS_BUCKET")


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from lambda_function.handler import handler
 
def build_event_get(ciudad):
    """Construye un evento simulado para GET /clima?ciudad=X"""
    return {
        "rawPath": "/clima",
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "ciudad": ciudad
        }
    }
 
def build_event_post(ciudad, nota=None):
    """Construye evento para POST /clima/snapshot"""
    body = {"ciudad": ciudad}
    if nota:
        body["nota"] = nota
    return {
        "rawPath": "/clima/snapshot",
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": json.dumps(body)
    }
 
def build_event_get_snapshots(ciudad):
    """Construye evento para GET /clima/snapshots/ciudad"""
    return {
        "rawPath": f"/clima/snapshots/{ciudad}",
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }
 
if __name__ == "__main__":
    # Prueba GET /clima
    print("=== Probando GET /clima ===")
    event_get = build_event_get("monterrey")
    resp = handler(event_get, None)
    print(json.dumps(resp, indent=2, ensure_ascii=False))
    
    # Prueba POST /clima/snapshot
    print("\n=== Probando POST /clima/snapshot ===")
    event_post = build_event_post("monterrey", "prueba local")
    resp = handler(event_post, None)
    print(json.dumps(resp, indent=2, ensure_ascii=False))
    
    # Prueba GET /clima/snapshots/monterrey (como no hay bucket dara un error relaciondo a eso)
    print("\n=== Probando GET /clima/snapshots/monterrey ===")
    event_list = build_event_get_snapshots("monterrey")
    resp = handler(event_list, None)
    print(json.dumps(resp, indent=2, ensure_ascii=False))