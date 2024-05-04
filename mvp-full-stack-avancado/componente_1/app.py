from flask import Flask, jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask_cors import CORS
from flask import redirect
import hmac
from models import Session,User,Portfolio
from schemas import *
from datetime import datetime, timedelta,date
import requests

jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}

security_schemes = {"jwt": jwt}

info = Info(title="Api Controle Usuário", version="1.0.0")
app = OpenAPI(__name__, info=info,security_schemes=security_schemes)
CORS(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

security = [{"jwt": []}]

str_to_bytes = lambda s: s.encode("utf-8") if isinstance(s, str) else s
safe_str_cmp = lambda a, b: hmac.compare_digest(str_to_bytes(a), str_to_bytes(b))

def authenticate(username, password):
    user = Session().query(User).filter_by(username=username).first()
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return Session().query(User).get(user_id)

# definindo tags
user_tag = Tag(name="Usuário", description="Gestão dos usuários")
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/users', tags=[user_tag],
          responses={"201": {'message': 'User created successfully'}},description='Cadastro de usuário')
def create_user(form: UserSchema):
    session = Session()
    user = User(form.name,form.email,form.username,form.password)
    session.add(user)
    session.commit()
    session.close()

    return jsonify({'message': 'User created successfully'}), 201


@app.get('/users/<string:username>', tags=[user_tag],responses={200:UserViewSchema,404:ErrorSchema},
         description='Consulta dados de um usuário',security=security)
@jwt_required()
def get_user(path: UserPathSchema):
    user = Session().query(User).filter_by(username=path.username).first()

    if user:
        return lista_usuario(user), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@app.post('/portfolio', tags=[user_tag],
          responses={"200": {'message': 'Portfolio created successfully'}},description='Cadastro do portfolio de um usuário',security=security)
@jwt_required()
def create_portfolio(body: PortfolioBodyJsonSchema):
    current_user = get_jwt_identity()
    session = Session()
    user = session.query(User).filter_by(username=current_user).first()
    if len(user.portfolios) > 0:
        next_id = max(user.portfolios,key=lambda x:x.id).id + 1
    else:
        next_id = 1
    for p in body.portifolio:
        portfolio = Portfolio(next_id,p.asset,p.weight,date.today(),None)
        user.add_portfolio(portfolio)

    session.commit()
    session.close()

    return jsonify({'message': 'Portfolio created successfully'}), 200


@app.put('/portfolio', tags=[user_tag],
          responses={"200": {'message': 'Portfolio updated successfully'}},description='Atualiza o portfolio de um usuário',security=security)
@jwt_required()
def update_portfolio(form: PortfolioUpdateSchema):
    current_user = get_jwt_identity()
    session = Session()
    id_portfolios = [p.id for p in form.portfolios]
    if form.close:
        user = session.query(User).filter_by(username=current_user).first()
        session.query(Portfolio).filter(Portfolio.user_id==user.id,Portfolio.id.in_(id_portfolios)).update({Portfolio.end_date:date.today()})
    else:
        for p in form.portfolios:
            session.query(Portfolio).filter(Portfolio.id_pk==p.id_pk).update({Portfolio.asset:p.asset,Portfolio.weight:p.weight})
    session.commit()
    session.close()

    return jsonify({'message': 'Portfolio updated successfully'}), 200

@app.delete('/portfolio', tags=[user_tag],
          responses={"200": {'message': 'Portfolio deleted successfully'}},description='Deleta o portfolio de um usuário',security=security)
@jwt_required()
def delete_portfolio(form: PortfolioDeleteSchema):
    current_user = get_jwt_identity()
    session = Session()
    user = session.query(User).filter_by(username=current_user).first()
    id_portfolio = form.id_portfolio
    session.query(Portfolio).filter(Portfolio.user_id==user.id,Portfolio.id==id_portfolio).delete()
   
    session.commit()
    session.close()

    return jsonify({'message': 'Portfolio deleted successfully'}), 200


@app.get('/portfolio', tags=[user_tag],
          responses={"200": PortfolioViewSchema},description='Busca portifolio por id do usuário',security=security)
@jwt_required()
def get_portfolio(query: QueryPortfolio):
    current_user = get_jwt_identity()
    session = Session()
    user_id = session.query(User).filter_by(username=current_user).first().id
    
    portfolios = session.query(Portfolio).filter(Portfolio.user_id==user_id)

    if query.id_portfolio:
        portfolios = portfolios.filter(Portfolio.id==query.id_portfolio)

    if query.start_date:
        portfolios = portfolios.filter(Portfolio.start_date>=query.start_date)

    if query.end_date:
        portfolios = portfolios.filter(Portfolio.end_date<=query.end_date)

    session.close()

    return apresenta_lista_portfolios(portfolios.all()), 200

@app.get('/portfolio_optimazer',tags=[user_tag],responses={"200":PortfolioBodyJsonSchema},description="Cria um portfolio otimizado")
@jwt_required()
def portfolio_optimizer(query:OptimizatonSchema):
    
    n = None
    asset_list= None
    if query.opt_parameter.isdigit():
        n = int(query.opt_parameter)
    else:
        asset_list = query.opt_parameter

    if n is not None:
        query = f"n_assets_portfolio={n}"
    else:
        query = f"asset_list={asset_list}"

    url = f"http://localhost:5002/optimize?{query}"

    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

   
    return [{"asset":p.asset,"weight":p.weight} for p in response.json()], 200
        

@app.post('/auth',tags=[user_tag])
def auth_user(form:UserLoginSchema):
    
    username = form.username
    password = form.password

    user = authenticate(username, password)
    if user:
        access_token = create_access_token(identity=username,expires_delta=timedelta(seconds=600))
        return jsonify(access_token=access_token)
    else:
        return jsonify({'message': 'Invalid credentials'}), 401
    



if __name__ == '__main__':
    app.run(debug=True)
