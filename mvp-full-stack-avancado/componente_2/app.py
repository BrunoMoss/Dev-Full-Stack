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
import numpy as np
import requests
from utils.calculator import Calculator
import requests

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

@app.get('/optimize', tags=[user_tag],
         description='Cria um portfolio ótimo',security=security,responses={200:PortfolioSchema})
@jwt_required()
def optimaze(query: OptimizatonSchema):
    n_assets_portfolio = query.n_assets_portfolio
    asset_list = query.asset_list

    end_date = datetime.today().replace(hour=0,minute=0,second=0)
    start_date = (datetime.today()- timedelta(days=252)).replace(hour=0,minute=0,second=0)

    if asset_list and asset_list != '':
        url = f"http://localhost:5003/prices?n={n_assets_portfolio}&start_date={start_date}&end_date={end_date}"
    else:
        url = f"http://localhost:5003/prices?assets={asset_list}&start_date={start_date}&end_date={end_date}"

    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    calc = Calculator(200,50)
    calc.returns_list = calc.calculate_log_return(data)
    portfolio = calc.optimize_portfolio()

    return [{"asset":a,  'weight':round(w,2),'start_date': datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)} for (a,w) in portfolio.items()]

    
    



    