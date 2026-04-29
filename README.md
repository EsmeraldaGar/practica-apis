# Práctica de APIs — Fase 1
 
API para consultar clima actual y guardar snapshots localmente.
 
## Requisitos
 
- Python >= 3.13
- `uv` (gestor de paquetes)

## Requisitos
 
- Python >= 3.13
- `uv` (gestor de paquetes)
 
## Instalación y ejecución local
 
1. Clonar el repositorio.
2. Sincronizar dependencias: `uv sync`
3. Copiar `.env.example` a `.env` y añadir tu `API_KEY` de OpenWeatherMap.
4. Ejecutar el servidor: `uv run uvicorn main:app --reload`
5. Abrir `http://localhost:8000/docs` para probar.

## Posibles configuraciones
Para instalas AWS CLI se deben pedir permisos de administrador en: https://nttlimitedinternal.service-now.com/esc?id=sc_cat_item&sys_id=2288d30d97447ed0495cb077f053af25


 
## Despliegue en AWS (Fase 2)
 
### Prerrequisitos
- AWS CLI configurado con perfil `esmeralda-lab`
- Node.js 18+ y AWS CDK instalado globalmente
- Variables de entorno: `export API_KEY="tu_clave"`
 
### Pasos
1. Clonar el repositorio.
2. Sincronizar dependencias: `uv sync` (opcional)
3. Copiar `.env.example` a `.env` y añadir tu `API_KEY` de OpenWeatherMap.
4. `cd infra`
5. `uv sync`
6. `npx cdk synth`
7. `npx cdk deploy`
 
### Prueba

 
## Autor
 
[Esmeralda]


 

 

 
