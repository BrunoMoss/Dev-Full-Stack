from urllib.parse import unquote
from email.mime import base
from sqlalchemy.exc import IntegrityError
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask_cors import CORS
from flask import redirect
from model import Session,Fundo,Cota
from logger import logger
from schemas import *
from schemas.fundo import *
from schemas.cota import *
from carga import DadosCVM,gerar_lista_meses


info = Info(title="Api Fundos", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
atualiza_tag = Tag(name="Atualiza", description="Download e atualização dos dados")
fundo_tag = Tag(name="Fundo", description="Visualização de fundos")
cota_tag = Tag(name="Cota", description="Visualização de Cotas")

@app.get('/')
def home():
    return redirect('/openapi')


@app.post('/atualiza', tags=[atualiza_tag],
          responses={"200": AtualizaViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def atualiza_dados(form: AtualizaSchema):
    """Atualiza os dados de acordo com a tarefa selecionada

    Retorna o status da execução da tarefa.
    """
    startdate=form.datainicial
    enddate=form.datafinal
    descricao_job=form.tarefa
    
    logger.debug(f"Executando o job: '{descricao_job}'.")
    try:
        c = DadosCVM()
        count = 0
        if descricao_job == 'portfolio':
            lista_fundos = c.getFundosValidos()
            datas = gerar_lista_meses(startdate,enddate)
            
            for dt in datas:
                c.deleteTableData('portfolio',dt)
                count+= c.loadDadosPortfolio(dt,lista_fundos)
            logger.debug(f"Job '{descricao_job}' executado.")
        elif descricao_job == 'cota':
            lista_fundos = c.getFundosValidos()
            datas = gerar_lista_meses(startdate,enddate)
            
            for dt in datas:
                c.deleteTableData('cota',dt)
                count+= c.loadDadosCotas(dt,lista_fundos)
            logger.debug(f"Job '{descricao_job}' executado.")
        elif descricao_job == 'cadastro':
            c.cleanTableData('fundo')
            count+= c.loadDadosFundos()
        else:
            raise Exception("Job não encontrado")
        return resultado_atualizacao((descricao_job,"OK",count)), 200  
    except Exception as e:
        error_msg = f"Erro na execução do job '{descricao_job}'."
        logger.warning(f"Erro ao executar o job '{descricao_job}', {e}")
        return {"message": error_msg,"description":str(e)}, 400


@app.get('/fundo', tags=[fundo_tag],
         responses={"200": FundoListaViewSchema, "404": ErrorSchema})
def get_fundo(query: BuscaFundoSchema):
    """Faz a busca por uma lista de fundos a partir do cnpj do fundo ou do nome do fundo.

    Retorna as características dos fundos solicitados.
    """
    cnpj = query.cnpj
    tag = query.razao_social
    session = Session()
    if cnpj is None:
        logger.debug(f"Busca pelo cnpj, coletando dados sobre o fundo #{cnpj}")
        search = "%{}%".format(tag)
        fundos = session.query(Fundo).filter(Fundo.razao_social.like(search)).all()
    else:
        logger.debug(f"Busca pelo nome, coletando dados sobre o fundo #{tag}")
        fundo = session.query(Fundo).filter(Fundo.cnpj == cnpj).first()
        fundos = [fundo]
    if not fundos:
        error_msg = "Fundo não encontrado na base :/"
        logger.warning(f"Erro ao buscar fundo pelos dados'{cnpj,tag}', {error_msg}")
        return {"message": error_msg}, 400
    else:
        logger.debug(f"Produto econtrado: '{[f.cnpj for f in fundos]}'")
        return apresenta_lista_fundos(fundos), 200


@app.get('/cota', tags=[cota_tag],
         responses={"200": CotaListaViewSchema, "404": ErrorSchema})
def get_cota(query: BuscaCotaSchema):
    """Faz a busca das cotas de um fundo em um intervalo de datas.

    Retorna o valor das cotas no intervalo definido para o fundo especificado.
    """
    cnpj = query.cnpj
    data_inicial = query.data_inicial
    data_final = query.data_final
    session = Session()
    
    #logger.debug(f"Busca pelo nome, coletando dados sobre o fundo #{tag}")
    cotas = session.query(Cota).filter(Cota.cnpj == cnpj,Cota.dt_comptc >= data_inicial,Cota.dt_comptc <= data_final).all()

    if not cotas:
        error_msg = "Não existem cotas no intervalo de datas para o fundo especificado :/"
        logger.warning(f"Erro ao buscar fundo pelos dados'{cnpj,data_inicial,data_final}', {error_msg}")
        return {"message": error_msg}, 400
    else:
        logger.debug(f"Cotas encontradas para o fundo: '{cnpj}'")
        return apresenta_lista_cotas(cotas), 200