# Técnicas de Mineração de Dados Aplicadas no Contexto de Pokémon

![Language](https://img.shields.io/badge/Made%20with%20Python-v%200.2-blue)

## 📜 Resumo
Este repositório é dedicado à parte de implementação do meu TCC sobre "Técnicas de Mineração de Padrões Frequentes aplicadas no contexto de
Formação de Equipes para o Pokémon Showdown", cuja proposta definida por mim trata-se da aplicação de técnicas de mineração de padrões frequentes numa amostra contendo dados de equipes de pokémons utilizadas em batalhas competitivas na _tier_ popular _OU_ (_OverUsed_) no simulador de batalhas online _Pokémon Showdown_ a fim de construir um algoritmo formador de equipes, a visualização dos relacionamentos entre os pokémons da amostra através de grafos e uma análise exploratória de dados sobre os pokémons da 1ª à 9ª geração.

## ✔️ Progresso
- [x] Fazer o _web scraping_ da _ladder_ do _Pokémon Showdown_;
- [x] Aplicar o algoritmo de mineração de padrões frequentes e construir o _team builder_;
- [x] Modelar os dados da amostra como um grafo e exportar a visualização;
- [x] Fazer a análise exploratória dos dados dos pokémons da 1ª à 9ª geração;

## 📁 Estrutura de arquivos:
O projeto é estruturado conforme a descrição abaixo:
```
├── data
│   ├── original    -> bases de dados no formato original e sem tratamento.
│   └── processed   -> dados transformados.
└── src
    ├── features    -> contém os scripts ".py". 
    ├── notebooks   -> notebooks com pré-processamento dos dados, web scraping, 
    |                  aplicação do algoritmo de mineração de padrões frequentes e EDA.
    └── utils       -> funções úteis.
```
![Grafo](data/processed/grafo_resultante_gen9_12_10_2023.png)
