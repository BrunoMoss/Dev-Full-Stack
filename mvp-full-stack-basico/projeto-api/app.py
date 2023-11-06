from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session
from model.fundo import Fundo
#from logger import logger
#from schemas import *
from flask_cors import CORS