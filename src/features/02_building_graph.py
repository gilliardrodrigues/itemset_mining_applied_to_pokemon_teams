import pandas as pd
import logging
from src.features.UndirectedMultiGraph import UndirectedMultiGraph
from src.utils.utils import get_logger, Clock

if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    logger = get_logger(logger=logger)

    filepath = 'C:\\Users\\User\\Documents\\jupyter_notebooks\\ufmg\\itemset_mining_applied_to_pokemon_teams\\'

    logger.info("Importando base de dados...")
    teams_df = pd.read_csv(filepath + 'data\\processed\\ladder_teams.csv')
    logger.info("Feito!")

    logger.info("Coletando pokémons da base...")
    pokemons = teams_df.stack().reset_index(drop=True)
    logger.info("Feito!")
    logger.info("Coletando pokémons distintos...")
    unique_pokemons = pokemons.unique()
    logger.info("Feito!")

    logger.info("A construção do grafo começará agora...")
    build_time = Clock("Construção do grafo")
    g = UndirectedMultiGraph(unique_pokemons)
    g.add_edges_from_transaction_df(teams_df)
    build_time.stop_watch()

    logger.info("Exportando o grafo como gefx...")
    g.export_to_gephi('../../data/processed/')
    logger.info("Feito!")

    print("\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!! Todos os passos foram executados com sucesso!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
