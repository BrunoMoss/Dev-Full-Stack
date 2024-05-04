from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask_cors import CORS
from flask import redirect
from datetime import datetime, timedelta
from schemas import *

jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}

security_schemes = {"jwt": jwt}

info = Info(title="Api Otimização Portfolio", version="1.0.0")
app = OpenAPI(__name__, info=info,security_schemes=security_schemes)
CORS(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

security = [{"jwt": []}]

# definindo tags
user_tag = Tag(name="Usuário", description="Gestão dos usuários")
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.post('/optimize', tags=[user_tag],
         description='Cria um portfolio ótimo',security=security,responses={200:PortfolioSchema})
@jwt_required()
def optimaze(form: OptimizatonSchema):
    return [{"asset":'PETR4',  'weight':1,'start_date':datetime.now()}]
    