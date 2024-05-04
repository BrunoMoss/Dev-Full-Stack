import numpy as np
import random
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
import pandas as pd
from datetime import datetime,timedelta

class Calculator():

  # init method or constructor
  def __init__(self, population_size,ngen,return_list=None):
      self.population_size = population_size
      #self.nr_max_asset = nr_max_asset
      self.returns_list = return_list
      self.ngen= ngen
      

  # Função de restrição que o problema tiver (nem todos os problemas contém restrições)
  def FuncaoDeRestricao(self,individual):
    return sum(individual) == 1 and min(individual) >= 0


  # Função utilizada para gerar os individuos -> Repare que não há nenhum mistério, os valores v1 e v2 utilizam a função que é passada por parâmetro que por sua vez
  # é uma função que gera numeros aleatorios inteiros entre 0 e 50, como está declarado mais abaixo
  # outro ponto importante é como fazer a declaração do cromossomo, procure sempre utilizar tal forma como está decrito, para cada valor, adicionar (append) o mesmo ao cromossomo
  # GeradorDeIndividuos(ClasseDoIndividuo, FunçãoDeGeraçãoDeNºAleatorio):
  def GeradorDeIndividuos(self,icls, attr_bool_function):

    for i in range(10):
      cromossomo = list()
      for _ in range(len(self.returns_list.columns)):
          v = attr_bool_function()
          cromossomo.append(v)
      if self.FuncaoDeRestricao(cromossomo):
        break
    cromossomo = cromossomo/np.sum(cromossomo)
    return icls(cromossomo)

  def CrossoverFunction(self,ind1, ind2, icls, attr_bool_function):
    new_ind1, new_ind2 = tools.cxTwoPoint(ind1, ind2)
    if(not(self.FuncaoDeRestricao(new_ind1))):
      new_ind1,trash = tools.cxOnePoint(ind1, ind2)
      if(not(self.FuncaoDeRestricao(new_ind1))):
        new_ind1,trash = tools.cxUniform(ind1, ind2, indpb=0.2)
        if(not(self.FuncaoDeRestricao(new_ind1))):
          tries = 0
          while(not(self.FuncaoDeRestricao(new_ind1))):
            if tries >= 20:
              new_ind1 = ind1
              break
            new_ind1 = self.GeradorDeIndividuos(icls, attr_bool_function)
            tries = tries + 1
    if(not(self.FuncaoDeRestricao(new_ind2))):
      trash,new_ind1 = tools.cxOnePoint(ind1, ind2)
      if(not(self.FuncaoDeRestricao(new_ind2))):
        trash,new_ind2 = tools.cxUniform(ind1, ind2, indpb=0.2)
        if(not(self.FuncaoDeRestricao(new_ind2))):
          tries = 0
          while(not(self.FuncaoDeRestricao(new_ind2))):
            if tries >= 20:
              new_ind2 = ind2
              break
            new_ind2 = self.GeradorDeIndividuos(icls, attr_bool_function)
            tries = tries + 1
    return new_ind1,new_ind2


  def fitness_function(self,weights):
    portfolio_returns = np.dot(self.returns_list, weights)
    portfolio_mean = np.mean(portfolio_returns)*252
    covariance = np.cov(self.returns_list,rowvar=False)*252
    portfolio_variance = np.transpose(weights) @ covariance @ weights
    sharpe_ratio = (portfolio_mean / np.sqrt(portfolio_variance)) 
    return sharpe_ratio,

  def distance(self,individual):
    
    constraintA = abs(sum(individual)-1)
    constraintB = abs(sum([c for c in individual if c < 0]))
    
    return ((constraintA + constraintB) * self.fitness_function(individual)[0],)

  creator.create("FitnessMax", base.Fitness, weights=(1.0,))        # função objetivo: nome, tipo(f.o.), peso de cada objetivo (no caso só um objetivo); peso positivo = maximização
  creator.create("Individual", list,  fitness=creator.FitnessMax) 

  def optimize_portfolio(self):

    toolbox = base.Toolbox()
    # Definir o gerador de numeros aleatórios de numeros inteiros entre o intervalo (0 e 50)
    toolbox.register("attr_bool", random.random)
    # Inicialização do cromossomo (quantos genes o cromossomo deve possuir)
    #toolbox.register("individualCreator", GeradorDeIndividuos, toolbox.attr_bool)
    toolbox.register("individual", self.GeradorDeIndividuos, creator.Individual, toolbox.attr_bool)
    # toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 9)
    # Registro do individuo na população
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    # Registro do nome da função objetivo
    toolbox.register("evaluate", self.fitness_function)
    # Registro da função de penalidade caso o individuo não obedeça as restrições
    toolbox.decorate("evaluate", tools.DeltaPenalty(self.FuncaoDeRestricao, 0, self.distance))
    # Registro de qual o tipo de cruzamento deve ser utilizado (cruzamento de 2 pontos)
    #toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mate", self.CrossoverFunction, icls=creator.Individual, attr_bool_function=toolbox.attr_bool)
    # Registro de qual tipo de mutação deve ser utilizado (probabilidade de um individuo sofrer mutação)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    #toolbox.register("mutate", MutationFunction, indpb=0.1)
    # Registro de qual o tipo do método de seleção que será utilizado
    toolbox.register("select", tools.selRoulette)

    pop = toolbox.population(n=self.population_size)                           # inicialização da pop
    hof = tools.HallOfFame(1)                                 # melhor indivíduo
    stats = tools.Statistics(lambda ind: ind.fitness.values)  # estatísticas
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.7,stats=stats, ngen=self.ngen,  halloffame=hof, verbose=True) #aumentei mut = 0.7
  
    # Melhor solução
    print("Melhor Indivíduo:")
    print(hof[0])

    # Verificação da função de restrição
    print(self.FuncaoDeRestricao(hof[0]))


    # Melhor resultado da função objetivo
    print("Melhor Resultado da Função Objetivo:")
    print(self.fitness_function(hof[0]))

    return dict(zip(list(self.returns_list.columns),list(hof[0])))

  def calculate_log_return(self,data):
    prices_dict = {}
    for asset_data in data["all_prices"]:
      asset_prices = [price["price"] for price in asset_data["prices"]]
      prices_dict[asset_data["asset"]] = asset_prices

    # Criar um DataFrame a partir do dicionário
    df = pd.DataFrame(prices_dict)
    asset_returns = np.log(df)-np.log(df.shift(1))
    asset_returns.dropna(inplace= True)

    return asset_returns
        


if __name__ == '__main__':
    import requests
    n_assets_portfolio = 20
    
    start_date = (datetime.today()- timedelta(days=252)).replace(hour=0,minute=0,second=0,microsecond=0)
    end_date = datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)

    url = f"http://localhost:5000/prices?n={n_assets_portfolio}&start_date={start_date}&end_date={end_date}"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    calc = Calculator(200,50)
    calc.returns_list = calc.calculate_log_return(data)
    portfolio = calc.optimize_portfolio()
    print(portfolio)
    
    print([{"asset":a,  'weight':round(w,2),'start_date': datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)} for (a,w) in portfolio.items()])
