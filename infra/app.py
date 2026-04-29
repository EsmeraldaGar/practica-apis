#!/usr/bin/env python3
import os 
from aws_cdk import App # la clase app es el contenedor raiz de toda la aplicacion CDK
from infra_stack import PracticaStack

app = App()
PracticaStack(app, "EsmeraldaPracticaStack", #inicializa la pila, pasandole la aplicación y un identificador unico
    env = { 
        "account": os.environ.get("CDK_DEFAULT_ACCOUNT"),
        "region": os.environ.get("CDK_DEFAULT_REGION", "us-east-1")                          
    }                   
)
app.synth() 





