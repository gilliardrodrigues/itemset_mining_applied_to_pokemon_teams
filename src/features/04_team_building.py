import pandas as pd
from src.utils.utils import frozenset_converter


def is_team_complete(team_: list) -> bool:
    return len(team_) == 6


def has_suggestions(suggestions_: pd.DataFrame) -> bool:
    return len(suggestions_) > 0


if __name__ == '__main__':

    # Importando a base de equipes e as regras de associação:
    filepath = 'C:\\Users\\User\\Documents\\jupyter_notebooks\\ufmg\\itemset_mining_applied_to_pokemon_teams\\data\\processed\\'
    teams_df = pd.read_csv(filepath + 'ladder_teams.csv')
    rules_df = pd.read_csv(filepath + 'association_rules.csv',
                           converters={
                               'antecedents': frozenset_converter,
                               'consequents': frozenset_converter
                           })

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
            break
        else:
            suggestions = rules_df[rules_df['antecedents'] == frozenset(team)].copy()
            suggestions = suggestions[suggestions['consequent_len'] == 1]
            suggestions = suggestions[['antecedents', 'consequents', 'confidence', 'lift']]
            suggestions = suggestions.sort_values(by=['confidence', 'lift'], ascending=False).reset_index(drop=True)
            suggestions.rename(columns={'antecedents': 'Equipe atual', 'consequents': 'Sugestão',
                                        'confidence': 'Confiança', 'lift': 'Lift'}, inplace=True)
            suggestions['Confiança'] = [str(round(valor * 100, 2)) + '%' for valor in suggestions['Confiança']]

            if has_suggestions(suggestions):
                print("Pokémons atuais: " + str(team))
                print(f"\nEssas são as sugestões para o {nth_pokemon}º:")
                print(suggestions.head(10))

            else:
                print("Pokémons atuais: " + str(team))
                if pokemon not in unique_pokemons:
                    team.pop()
                    print('O pokémon escolhido não está disponível ainda, tente outro nome válido.')
                else:
                    print("Oops, não temos mais sugestões para essa equipe :(")
                    print("\nResultado: " + str(team)[1:-1])
                    break
                nth_pokemon -= 1

