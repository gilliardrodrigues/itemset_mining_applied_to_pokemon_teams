import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import logging

from itertools import combinations
from tqdm import tqdm
from src.utils.utils import get_logger, Clock
from IPython import display

logger = logging.getLogger(__name__)
logger = get_logger(logger=logger)

__all__ = [
    'add_edge',
    'add_edges_from_transaction_df',
    'show_adj_matrix',
    'get_nodes',
    'get_adj_matrix',
    'draw_graph',
    'export_graph_viz',
    'get_networkx_graph',
    'export_to_gephi'
]


class UndirectedMultiGraph:

    def __init__(self, nodes):
        """
        Classe para criar um multi-grafo não direcionado representado por matriz de adjacência na forma de um dataframe.

        Parâmetros
        ----------
        nodes : list or array
            Lista ou array contendo os nomes dos vértices.
        """
        self.nodes = nodes
        self.graph = pd.DataFrame(0, index=nodes, columns=nodes)

    def add_edge(self, u, v):
        """
        Adiciona uma aresta ao grafo.
        Parâmetros
        ----------
        u : str
            Nó de origem.
        v : str
            Nó de destino.
        """
        self.graph.loc[u, v] += 1
        self.graph.loc[v, u] += 1

    def add_edges_from_transaction_df(self, df):
        """
        Monta a matriz de adjacência a partir de um dataframe de transações.
        Parâmetros
        ----------
        df : pd.DataFrame
            Dataframe contendo as transações.
        """
        for _, row in df.iterrows():
            for pair in combinations(row, 2):
                self.add_edge(pair[0], pair[1])

    def show_adj_matrix(self):
        """
        Exibe a matriz de adjacência.
        """
        display(self.graph)

    def get_nodes(self):
        """
        Retorna a lista de vértices do grafo.
        """
        return self.nodes

    def get_adj_matrix(self):
        """
        Retorna o dataframe contendo a matriz de adjacência.
        """
        return self.graph

    def draw_graph(self, list_of_pokemons, layout) -> nx.Graph:
        """
        Plota o grafo através da biblioteca Networkx.
        Parâmetros
        ----------
        list_of_pokemons : pd.Series
            Série contendo todos os pokémons.
        layout
            Layout a ser utilizado no plot do grafo.
            Layouts aceitos:
                    - nx.spring_layout;
                    - nx.random_layout;
                    - nx.circular_layout;
                    - nx.shell_layout;
                    - nx.spectral_layout.
        Retorno
        ----------
        nx.Graph
            O grafo plotado.
        """
        plt.clf()
        fig = plt.figure(figsize=(100, 50))
        G = nx.from_pandas_adjacency(self.graph)

        pos = layout(G)
        node_weights = list_of_pokemons.value_counts(sort=False)
        edge_weights = [G[u][v]['weight'] for u, v in G.edges()]

        nx.draw_networkx_nodes(G, pos, node_size=node_weights, node_color=range(G.number_of_nodes()), cmap=plt.cm.hsv)
        nx.draw_networkx_edges(G, pos, width=edge_weights)
        nx.draw_networkx_labels(G, pos, font_weight='bold', font_size=10, verticalalignment='baseline')

        return G

    def export_graph_viz(self, list_of_pokemons, layouts_dict: dict):
        """
        Exporta o grafo como imagem.
        Parâmetros
        ----------
        list_of_pokemons : pd.Series
            Série contendo todos os pokémons.
        layouts_dict : dict
            Dicionário com os layouts a serem utilizados nos plots do grafo.
            Layouts aceitos:
                    - nx.spring_layout;
                    - nx.random_layout;
                    - nx.circular_layout;
                    - nx.shell_layout;
                    - nx.spectral_layout.
        """
        logger.info("Iniciando a exportação do grafo...")
        size = len(layouts_dict)
        exporting_images = Clock("Exportação do grafo como png")
        with tqdm(total=size) as pbar:
            pbar.set_description("Exportando os grafos...")
            for layout, filename in layouts_dict.items():
                self.draw_graph(list_of_pokemons, layout)
                plt.savefig(f"{filename}")
                pbar.update(1)
        exporting_images.stop_watch()
        logger.info("Grafos exportados!")

    def get_networkx_graph(self):
        """
        Retorna o grafo como nx.Graph.
        """
        return nx.from_pandas_adjacency(self.graph)

    def export_to_gephi(self, graph, gefx_file_path):
        """
        Exporta o grafo como arquivo GEFX para utilizar no Gephi.
        Parâmetros
        ----------
        graph : nx.Graph
            Grafo a ser exportado.
        """
        logger.info("Criando arquivo GEFX...")
        exporting_gefx = Clock("Exportação do grafo para o Gephi")
        nx.write_gexf(graph, f'{gefx_file_path}' + 'graph.gexf')
        exporting_gefx.stop_watch()
        logger.info(" Arquivo GEFX criado!")
