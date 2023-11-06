import pandas as pd
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

    def truncateTable(self,tbl):
        with self.__engine.connect() as conn:
            conn.execute(sa_text(f"TRUNCATE TABLE {tbl}").execution_options(autocommit=True))

    def loadDadosFundos(self):
        url = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"
        df = pd.read_csv(url,encoding='ISO-8859-1',delimiter=';')
        df.query('SIT=="EM FUNCIONAMENTO NORMAL" & CLASSE=="Fundo de Ações" & FUNDO_COTAS=="N" & VL_PATRIM_LIQ > 100000000',inplace=True)
        df_filtered = df[['CNPJ_FUNDO','DENOM_SOCIAL','CLASSE','ADMIN','GESTOR','CLASSE_ANBIMA']]
        df_filtered.rename(columns={'CNPJ_FUNDO':'cnpj','DENOM_SOCIAL':'razao_social','ADMIN':'administrador','CLASSE':'tipo_fundo','CLASSE_ANBIMA':'classe_fundo','GESTOR':'gestor'},inplace=True)
        df_filtered.drop_duplicates(subset=['cnpj'],keep='first',inplace=True)
        df_filtered['data_insercao'] = datetime.now()
        df_filtered.to_sql(name='fundo',con=self.__engine,if_exists='append',index=False)
        


if __name__ == "__main__":
    c = DadosCVM()
    c.loadDadosFundos()
