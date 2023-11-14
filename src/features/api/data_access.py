import pandas as pd
import sys

source_path = "/home/gilliardrodrigues/itemset_mining_applied_to_pokemon_teams/src"
sys.path.append(source_path)
from utils.utils import frozenset_converter


__all__ = [
    'get_sprites_df',
    'get_rules_df',
    'get_teams_df',
    'get_pokedex_df'
]

DATA_PATH = '/home/gilliardrodrigues/itemset_mining_applied_to_pokemon_teams/data/'


def get_sprites_df() -> pd.DataFrame:

    sprites_df = pd.read_csv(DATA_PATH + 'processed/sprites_showdown.csv')
    return sprites_df


def get_rules_df() -> pd.DataFrame:

    rules_df = pd.read_csv(DATA_PATH + 'processed/association_rules.csv',
                           converters={
                               'antecedents': frozenset_converter,
                               'consequents': frozenset_converter
                           })
    return rules_df


def get_teams_df() -> pd.DataFrame:

    teams_df = pd.read_csv(DATA_PATH + 'processed/ladder_teams.csv')
    return teams_df


def get_pokedex_df(interest_columns: list = []) -> pd.DataFrame:

    if len(interest_columns) != 0:
        return pd.read_csv(DATA_PATH + 'processed/pokedex_atualizada.csv', usecols=interest_columns)
    return pd.read_csv(DATA_PATH + 'processed/pokedex_atualizada.csv')