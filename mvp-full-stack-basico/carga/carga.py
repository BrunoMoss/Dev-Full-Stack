import pandas as pd
import pandasql as ps
import requests
import zipfile
from io import BytesIO
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sa_text
from datetime import datetime




class DadosCVM():

    def __init__(self):
        db_path = "mvp-full-stack-basico/projeto-api/database/"
        # url de acesso ao banco (essa é uma url de acesso ao sqlite local)
        db_url = 'sqlite:///%s/db.sqlite3' % db_path
        # cria a engine de conexão com o banco
        engine = create_engine(db_url, echo=False)
        self.__engine = engine
        self.__lista_fundos = []

    def deleteTableData(self,tbl):
        with self.__engine.connect() as conn:
            conn.execute(sa_text(f"DELETE FROM {tbl}"))
            conn.commit()

    def loadDadosFundos(self):
        url = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"
        df = pd.read_csv(url,encoding='ISO-8859-1',delimiter=';')
        df.query("""SIT=="EM FUNCIONAMENTO NORMAL" & CLASSE=="Fundo de Ações" & \
                  FUNDO_COTAS=="N" & VL_PATRIM_LIQ > 100000000 & \
                  DENOM_SOCIAL.str.contains("INVESTIMENTO NO EXTERIOR")==False & \
                  DT_INI_ATIV < "%s" """ % (pd.Timestamp.now().normalize() - pd.Timedelta(365*10,'d')),inplace=True)
        df_filtered = df[['CNPJ_FUNDO','DENOM_SOCIAL','CLASSE','ADMIN','GESTOR','CLASSE_ANBIMA']]
        df_filtered.rename(columns={'CNPJ_FUNDO':'cnpj','DENOM_SOCIAL':'razao_social','ADMIN':'administrador','CLASSE':'tipo_fundo','CLASSE_ANBIMA':'classe_fundo','GESTOR':'gestor'},inplace=True)
        df_filtered.drop_duplicates(subset=['cnpj'],keep='first',inplace=True)
        df_filtered['data_insercao'] = datetime.now()
        self.__lista_fundos = self.__lista_fundos + list(df_filtered['cnpj'])
        df_filtered.to_sql(name='fundo',con=self.__engine,if_exists='append',index=False)
        
    def loadDadosPortfolio(self,dt_ref=None):
        url = "https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_202307.zip"
        response = requests.get(url)
        if response.status_code == 200:
            with zipfile.ZipFile(BytesIO(response.content),'r') as zip_file:
                arquivo = [f for f in zip_file.namelist() if f.startswith('cda_fi_BLC_4_')][0]
                with zip_file.open(arquivo) as csv_file:
                    df = pd.read_csv(csv_file,encoding='ISO-8859-1',delimiter=';')
                    sql = """select dt_comptc,cnpj_fundo as cnpj,cd_ativo,cd_isin,
                            sum(qtd_negociada) as qtd_negociada,
                            sum(vl_negociado) as vl_negociado,
                            sum(qt_pos_final) as qt_pos_final,
                            sum(vl_merc_pos_final) as vl_merc_pos_final
                            from
                            (
                                select dt_comptc,
                                cnpj_fundo,tp_fundo,denom_social,cd_isin,
                                cd_ativo,-qt_venda_negoc + qt_aquis_negoc as qtd_negociada,
                                vl_venda_negoc - vl_aquis_negoc as vl_negociado,
                                qt_pos_final,vl_merc_pos_final
                                from
                                (
                                    select dt_comptc,cnpj_fundo,tp_fundo,denom_social,
                                    tp_aplic,tp_ativo,cd_ativo,cd_isin,
                                    coalesce(qt_venda_negoc,0)as qt_venda_negoc,
                                    coalesce(vl_venda_negoc,0) as vl_venda_negoc,
                                    coalesce(qt_aquis_negoc,0) as qt_aquis_negoc,
                                    coalesce(vl_aquis_negoc,0) as vl_aquis_negoc,
                                    case 
                                    when tp_aplic like '%recebidos em empréstimo' then
                                    coalesce(-qt_pos_final,0) 
                                    else
                                    coalesce(qt_pos_final,0)
                                    end as qt_pos_final,
                                    case
                                    when tp_aplic like '%recebidos em empréstimo' or tp_aplic like '%Posições lançadas' then
                                    coalesce(-vl_merc_pos_final,0)
                                    else
                                    coalesce(vl_merc_pos_final,0)
                                    end as vl_merc_pos_final
                                    from df
                                    where tp_aplic <> 'Vendas a termo a receber' and tp_aplic <> 'Compras a termo a receber'
                                    and tp_aplic not like 'Mercado Futuro%'
                                ) rv_t
                            ) rv_g GROUP BY dt_comptc,cnpj_fundo,cd_ativo,cd_isin"""   
                    df_portfolio = ps.sqldf(sql,locals()) 
                    df_portfolio = df_portfolio[df_portfolio['cnpj'].isin(self.__lista_fundos)]
                    df_portfolio['data_insercao'] = datetime.now()
                    df_portfolio.to_sql(name='portfolio',con=self.__engine,if_exists='append',index=False)
                    



if __name__ == "__main__":
    c = DadosCVM()
    c.deleteTableData('fundo')
    c.loadDadosFundos()
    c.deleteTableData('portfolio')
    c.loadDadosPortfolio()
    
    
