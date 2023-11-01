import pprint
import pandas as pd
pd.set_option('max_colwidth', None)
import sys
sys.path.insert(0, '../')
from utils.utils import frozenset_converter


def is_team_complete(team: list) -> bool:
    return len(team) == 6


def has_suggestions(suggestions: pd.DataFrame) -> bool:
    return len(suggestions) > 0


def is_pokemon_weak_against(pokemon: pd.core.series.Series, type: str) -> bool:
    return pokemon[type] >= 2.0


def is_pokemon_strong_against(pokemon: pd.core.series.Series, type: str) -> bool:
    return pokemon[type] <= 0.5


def get_team_weaknesses(types: list, df: pd.DataFrame, team: list) -> set:
    team_effectiveness = {
        'strengths': set(), 
        'weaknesses': set()
    }
    for pokemon_name in team:
        pokemon = df[df['name'] == pokemon_name]
        for type in types:
            if is_pokemon_weak_against(pokemon, type).any():
                team_effectiveness['weaknesses'].add(type)
            elif is_pokemon_strong_against(pokemon, type).any():
                team_effectiveness['strengths'].add(type)
    team_weaknesses = team_effectiveness['weaknesses'] - team_effectiveness['strengths']
    return team_weaknesses 


def display_grouped_suggestions(suggestions: pd.DataFrame) -> pd.DataFrame:
    pprint.pprint(suggestions.groupby('Sugestão').agg({
                'Freq. utilizado com': lambda x: list(x),
                'Confiança': lambda x: list(x),
                'Lift': lambda x: list(x),
                'É um reforço contra': lambda x: list(x.unique())
            }).reset_index(names='Sugestão'))


def fill_choice_advantage(team_weaknesses: list, pokedex: pd.DataFrame, suggestions: pd.DataFrame, col_name: str) -> pd.DataFrame:
    suggestions[col_name] = ''
    for suggestion in suggestions['consequents']:    
        name = list(suggestion)[0]
        pokemon = pokedex[pokedex['name'] == name]
        choice_advantage = ''
        for team_weakness in team_weaknesses:
            if is_pokemon_strong_against(pokemon, team_weakness).any():
                choice_advantage += (team_weakness[8:] + ', ')
        suggestions.loc[suggestions['consequents'] == suggestion, col_name] = choice_advantage[:-2]
    return suggestions


if __name__ == '__main__':

    # Importando a base de equipes e as regras de associação:
    datapath = 'C:\\Users\\User\\Documents\\jupyter_notebooks\\ufmg\\itemset_mining_applied_to_pokemon_teams\\data\\processed\\'
    teams_df = pd.read_csv(datapath + 'ladder_teams.csv')
    rules_df = pd.read_csv(datapath + 'association_rules.csv',
                           converters={
                               'antecedents': frozenset_converter,
                               'consequents': frozenset_converter
                           })
    interest_columns = ['name', 'against_bug', 'against_dark', 'against_dragon', 'against_electric', 'against_fairy', 
                    'against_fighting', 'against_fire', 'against_flying', 'against_ghost', 'against_grass', 
                    'against_ground', 'against_ice', 'against_normal', 'against_poison', 'against_psychic', 
                    'against_rock', 'against_steel', 'against_water']
    #pokedex = pd.read_csv(datapath + 'pokedex_atualizada.csv', delimiter=',', encoding='utf8', usecols=interest_columns)
    pokedex = pd.read_csv(datapath + 'pokedex_atualizada.csv', delimiter=',', encoding='utf8', usecols=interest_columns)


    # Extraindo os pokémons únicos:
    pokemons = teams_df.stack().reset_index(drop=True)
    unique_pokemons = pokemons.unique()

    # Algoritmo para formar equipes:
    team = []
    pokemon = ''
    nth_pokemon = 1
    while True:
        pokemon = input(f'Insira o nome do {nth_pokemon}º pokémon da sua equipe: ').title()
        nth_pokemon += 1
        team.append(pokemon)
        if is_team_complete(team):
            print("Resultado: " + str(team)[1:-1])
            team_weaknesses = get_team_weaknesses(against_types, pokedex, team)
            print("Fraquezas da equipe final: " + str([weakness[8:] for weakness in team_weaknesses]))
            break
        elif pokemon not in unique_pokemons:
            team.pop()
            print('O pokémon escolhido não está disponível ainda, tente outro nome válido.')
            print("Pokémons atuais: " + str(team))
            if len(team) > 0:
                display_grouped_suggestions(suggestions)
            nth_pokemon -= 1
        else: 
            suggestions = rules_df[rules_df['antecedents'].apply(lambda x: x.issubset(frozenset(team)))].copy()
            suggestions = suggestions[~suggestions['consequents'].isin(suggestions['antecedents'])]
            suggestions = suggestions[suggestions['consequent_len'] == 1]

            against_types = interest_columns[1:]
            team_weaknesses = get_team_weaknesses(against_types, pokedex, team)
            col_name = 'É um reforço contra'
            suggestions = fill_choice_advantage(team_weaknesses, pokedex, suggestions, col_name)
            
            suggestions = suggestions[['antecedents', 'consequents', 'confidence', 'lift', 'É um reforço contra']]
            suggestions = suggestions.sort_values(by=['confidence', 'lift'], ascending=False).reset_index(drop=True)
            suggestions.rename(columns = {'antecedents':'Freq. utilizado com', 'consequents':'Sugestão',
                                        'confidence':'Confiança', 'lift':'Lift'}, inplace = True)
            suggestions['Confiança'] = [str(round(valor * 100, 2)) + '%' for valor in suggestions['Confiança']]
            
            if has_suggestions(suggestions):
                print("Pokémons atuais: " + str(team))
                print("Fraquezas da equipe atual: " + str([weakness[8:] for weakness in team_weaknesses]))
                print(f"\nEssas são as sugestões para o {nth_pokemon}º:")
                display_grouped_suggestions(suggestions)
            else:
                print("Oops, não temos mais sugestões para essa equipe :(")
                print("\nResultado: " + str(team)[1:-1])
                nth_pokemon -= 1
                break

