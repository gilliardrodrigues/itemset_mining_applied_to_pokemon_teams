import pandas as pd
import networkx as nx

import logging

from src.features.UndirectedMultiGraph import UndirectedMultiGraph
from src.utils.utils import get_logger, Clock

logger = logging.getLogger(__name__)
logger = get_logger(logger=logger)

filepath = 'C:\\Users\\User\\Desktop\\8º período\\MSI I\\Repositórios\\itemset_mining_applied_to_pokemon_teams\\'

logger.info("Importando base de dados...")
all_teams_df = pd.read_csv(filepath + 'data\\processed\\merged_teams.csv')
logger.info("Feito!")

logger.info("Coletando pokémons da base...")
pokemons = all_teams_df.stack().reset_index(drop=True)
logger.info("Feito!")
logger.info("Coletando pokémons distintos...")
unique_pokemons = pokemons.unique()
logger.info("Feito!")

logger.info("A construção do grafo começará agora...")
build_time = Clock("Construção do grafo")
g = UndirectedMultiGraph(unique_pokemons)
g.add_edges_from_transaction_df(all_teams_df)
build_time.stop_watch()
"""
logger.info("Plotando o grafo e exportando como png...")
test_layouts = {
        nx.spring_layout: "layout_test_plot_spring.jpg",
        nx.circular_layout: "layout_test_plot_circular.jpg",
        nx.random_layout: "layout_test_plot_random.jpg",
        nx.shell_layout: "layout_test_plot_shell.jpg",
        nx.spectral_layout: "layout_test_plot_spectral.jpg"
    }
g.export_graph_viz(pokemons, test_layouts)
logger.info("Feito!")
"""
logger.info("Exportando o grafo como gefx...")
networkx_graph = g.get_networkx_graph()
g.export_to_gephi(networkx_graph, '../../data/')
logger.info("Feito!")

print("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
print("!! Todos os passos foram executados com sucesso!")
print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
