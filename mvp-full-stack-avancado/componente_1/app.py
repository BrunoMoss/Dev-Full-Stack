from flask import Flask, jsonify, request
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
from datetime import datetime, timedelta

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
