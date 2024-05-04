import pandas as pd
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask_cors import CORS
from flask import redirect
from models import Session,Price,Asset
from schemas import *
from utils import *
from datetime import datetime
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import contains_eager

jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}

security_schemes = {"jwt": jwt}

info = Info(title="Api Market Data", version="1.0.0")
app = OpenAPI(__name__, info=info,security_schemes=security_schemes)
CORS(app)


# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
market_tag = Tag(name="Market Data", description="Adição, visualização e remoção de dados de mercado à base")



# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

security = [{"jwt": []}]

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.post('/asset', tags=[market_tag],
          responses={"200": AssetAddSchema},description='Insere no banco o preço dos ativos mais negociados')
def insert_asset(form:AssetFormSchema):
    """Insere no banco os ativos coletados.
    """
    n = form.n
    session = Session()
    assets_df = getAssetsInfo(n)
    count = 0
    for index,row in assets_df.iterrows():
        if session.query(Asset).filter_by(ticker=row['symbol']).count() ==0:
            session.add(Asset(row['symbol'],row['name_x'],row['average_volume']))
        else:
            session.query(Asset).filter_by(ticker=row['symbol']).update({'avg_volume':row['average_volume']})
        count+=1

    session.commit()
    session.close()

    return jsonify({'message': 'Registros de ativos inseridos','número de ativos':count}), 200


@app.post('/prices', tags=[market_tag],
          responses={"200": PriceAddSchema},description='Insere na tabela o preço dos ativos cadastrados')
def insert_prices(form: PriceFormSchema):
    """Calcula e insere no banco os preços coletados.
    """
    n = form.n
    page = form.page

    session = Session()
    top_assets = session.query(Asset.ticker).order_by(Asset.data_insercao.desc(),Asset.avg_volume.desc()).distinct().all()[n*(page-1):n*page]
    asset_list = [a[0] for a in top_assets]
    prices,cols = getPrices(asset_list)
    count = 0

    for c in cols:     
        asset = session.query(Asset).filter_by(ticker=c).first()
        if len(asset.prices) > 0:
            max_date = max(asset.prices,key=lambda x: x.date).date
        else:
            max_date = None
        for dt,p in prices[c].items():
            dt_obj = datetime.strptime(dt,'%Y-%m-%dT%H:%M:%SZ').replace(hour=0,minute=0,second=0)
            if max_date:
                if dt_obj > max_date:
                    asset.add_price(Price(dt_obj,p))
            else:
                asset.add_price(Price(dt_obj,p))

        count+=1
   
    session.commit()
    session.close()

    return jsonify({'message': 'Registros de preços de ativos inseridos','número de ativos':count}), 200


@app.get('/prices', tags=[market_tag],
          responses={"200": PriceDataViewSchema},description='Retorna os preços dos ativos consultados')
def get_prices(query:PriceQuerySchema):
    """Retorna os preços dos ativos.
    """
    session = Session()

    if  query.assets and query.assets != '':
        asset_list = query.assets.split(',')
        assets = session.query(Asset).filter(Asset.ticker.in_(asset_list))
        results = assets.join(Price).options(contains_eager(Asset.prices)).filter(Price.date>=query.start_date,Price.date<=query.end_date).all()
    else:
        n = query.n
       
        assets = session.query(Asset).join(Price).options(contains_eager(Asset.prices)).filter(Price.date>=query.start_date,Price.date<=query.end_date)
        results = assets.order_by(Asset.avg_volume.desc()).all()[0:n]
    
   
    return apresenta_lista_precos(results)

@app.get('/assets', tags=[market_tag],
          responses={"200": AssetViewSchema},description='Lista os ativos elegíveis')
def get_assets(query:AssetQuerySchema):
    """Retorna os n ativos mais negociados.
    """
    n = query.n
    session = Session()
    results = session.query(Asset.ticker).order_by(Asset.avg_volume.desc()).distinct().all()[0:n]

    return {'assets':[a[0] for a in results]}
    