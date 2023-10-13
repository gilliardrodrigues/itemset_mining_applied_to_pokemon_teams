import logging
import pandas as pd
from src.utils.utils import get_logger
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules


if __name__ == '__main__':

    # Inicializando o logger:
    logger_ = logging.getLogger(__name__)
    logger_ = get_logger(logger=logger_)

    # Importando a base de equipes:
    filepath = 'C:\\Users\\User\\Documents\\jupyter_notebooks\\ufmg\\itemset_mining_applied_to_pokemon_teams\\data\\processed\\'
    teams_df = pd.read_csv(filepath + 'ladder_teams.csv')
    logger_.info(f"O dataframe contém {teams_df.shape[0]} equipes.")

    # Convertendo o dataset de equipes para o formato que o algoritmo fpgrowth espera como entrada:
    logger_.info('Convertendo o dataset para o formato que o fpgrowth espera')
    tr_encoder = TransactionEncoder()
    tr_encoder = tr_encoder.fit(teams_df.values)
    tr_arr = tr_encoder.transform(teams_df.values)
    tr_team_df = pd.DataFrame(tr_arr, columns=tr_encoder.columns_)

    # Aplicando o algoritmo fpgrowth nos dados e gerando a base de regras de associação:
    logger_.info('Gerando os itemsets frequentes...')
    freq_itemsets = fpgrowth(tr_team_df, min_support=0.01, use_colnames=True)
    logger_.info('Gerando as regras de associação...')
    rules_df = association_rules(freq_itemsets, metric="lift", min_threshold=1)
    rules_df = rules_df.sort_values(by='confidence', ascending=False).reset_index(drop=True)
    rules_df["antecedent_len"] = rules_df["antecedents"].apply(lambda x: len(x))
    rules_df["consequent_len"] = rules_df["consequents"].apply(lambda x: len(x))

    # Exportando a base como csv:
    logger_.info('Exportando a base de regras de associação como csv...')
    rules_df.to_csv(filepath + 'association_rules.csv', index=False)
    logger_.info("A base foi exportada!")
