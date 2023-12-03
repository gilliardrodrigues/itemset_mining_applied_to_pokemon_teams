# Técnicas de Mineração de Dados Aplicadas no Contexto de Pokémon

![Language](https://img.shields.io/badge/Made%20with%20Python-v%200.2-blue)

[![Web App](https://img.shields.io/badge/deployed%20on-pythonanywhere-blue)](https://gilliardrodrigues.pythonanywhere.com)

## 📜 Resumo
Este repositório é dedicado à parte de implementação do meu TCC sobre "Técnicas de Mineração de Padrões Frequentes aplicadas no contexto de
Formação de Equipes para o Pokémon Showdown", cuja proposta definida por mim trata-se da aplicação de técnicas de mineração de padrões frequentes numa amostra contendo dados de equipes de pokémons utilizadas em batalhas competitivas na _tier_ popular _OU_ (_OverUsed_) no simulador de batalhas online _Pokémon Showdown_ a fim de construir um algoritmo formador de equipes, a visualização dos relacionamentos entre os pokémons da amostra através de grafos e uma análise exploratória de dados sobre os pokémons da 1ª à 9ª geração.

## ✔️ Progresso
- [x] Fazer o _web scraping_ da _ladder_ do _Pokémon Showdown_;
- [x] Aplicar o algoritmo de mineração de padrões frequentes e construir o _team builder_;
- [x] Modelar os dados da amostra como um grafo e exportar a visualização;
- [x] Fazer a análise exploratória dos dados dos pokémons da 1ª à 9ª geração;
- [x] Converter os códigos das etapas de coleta de dados e construção da base de regras para _scripts_ _.py_;
- [x] Desenvolver uma _API_ em _Flask_ que disponilize _endpoints_ para o usuário utilizar o algoritmo formador de equipes desenvolvido;
- [x] Desenvolver o _Front-end_ que consumirá a _API_ e será utilizado pelo usuário;
- [x] Implantar a aplicação web para que fique disponível ao público;

## 📁 Estrutura de arquivos:
O projeto é estruturado conforme a descrição abaixo:
```
├── data
│   ├── original    -> bases de dados no formato original e sem tratamento.
│   └── processed   -> dados transformados.
│
├── resources
│   ├── static
│   │   ├── css     -> arquivos de estilização (_.css_).
│   │   ├── img     -> imagens utilizadas no _Front-end_ da aplicação web.
│   │   └── js      -> código-fonte em _JavaScript_.
│   │
│   └── templates   -> código-fonte da aplicação web em _.HTML_.
└── src
    ├── features    
    │   ├── api     -> contém os scripts _.py_ da _API_ desenvolvida em _Flask_.
    |   └── ...     -> scripts _.py_ referente às etapas de coleta de dados e construção da base de regras de associação.
    ├── notebooks   -> notebooks com pré-processamento dos dados, web scraping, 
    |                  aplicação do algoritmo de mineração de padrões frequentes e EDA.
    └── utils       -> funções úteis.
```
![Grafo](data/processed/grafo_resultante_gen9_12_10_2023.png)
