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
La API está desplegada en AWS Lambda + S3 con Function URL pública.

### Arquitectura
```text
Cliente → Function URL (HTTPS)
│
├─▶ Lambda (Python 3.13)
│ ├─▶ OpenWeatherMap (HTTPS)
│ └─▶ S3 (snapshots)
└─▶ CloudWatch Logs
```

### Requisitos previos para desplegar
 
- Node.js 20+ (recomendado 22 LTS)
- AWS CLI configurado con perfil `esmeralda-lab`
- AWS CDK instalado globalmente: `npm install -g aws-cdk`
- Variable de entorno `API_KEY` con tu clave de OpenWeatherMap

 
### Endpoints disponibles (Function URL)
 
- **GET /clima?ciudad={nombre}** → consulta el clima actual.
- **POST /clima/snapshot** → guarda un snapshot (body: `{"ciudad": "...", "nota": "..."}`).
- **GET /clima/snapshots/{ciudad}** → lista los snapshots guardados.

### Estructura del proyecto
```text
practica-apis
|
├── src/
│ └── lambda_function/
│ └── handler.py # Código Lambda (reescritura síncrona)
├── infra/
│ ├── app.py # Punto de entrada CDK
│ ├── infra_stack.py # Stack: Bucket S3, Lambda, Function URL
│ └── cdk.json # Configuración CDK
├── scripts/
│ └── invoke_local.py # Prueba local del handler sin deployar
├── main.py # FastAPI original (referencia local)
├── pyproject.toml # Dependencias (uv)
├── .env # API_KEY (solo local)
└── README.md
```

### Despliegue desde cero 
 
1. Clonar el repositorio  `cd practica-apis && uv sync` y entrar a `cd infra/`.
2. Instalar dependencias: `uv sync`.
3. Configurar AWS CLI con perfil `esmeralda-lab`.

        ### Configuración del perfil AWS

        ```bash
        aws configure --profile esmeralda-lab
        # Introduce Access Key, Secret Key, region us-east-1, formato json
        export AWS_PROFILE=esmeralda-lab

4. Exportar `API_KEY` de OpenWeatherMap `export API_KEY="tu_clave_aqui"`.
5. npx cdk synth               # opcional, genera plantilla
6. npx cdk deploy              # despliega los recursos

 
> **Nota:** La Lambda usa `urllib` (sin dependencias externas), por lo que no se necesita Docker para empaquetar.
 
### Estado actual
 
Último despliegue: 2026-05-05. Function URL: `https://ijyvrn2cbgip5ahl6lxvbalnji0umyre.lambda-url.us-east-1.on.aws/`
 
## Autor
 
[Esmeralda]


 

 

 
