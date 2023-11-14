import pandas as pd
from .data_access import get_sprites_df, get_rules_df, get_teams_df, get_pokedex_df


__all__ = [
    'find_suggestions_by_team',
    'get_all_sprites'
]


def _is_team_complete(team: list) -> bool:

    return len(team) == 6


def _has_suggestions(suggestions_df: pd.DataFrame) -> bool:

    return len(suggestions_df) > 0


def _get_unique_pokemons() -> list:

    teams_df = get_teams_df()
    pokemons = teams_df.stack().reset_index(drop=True)
    return pokemons.unique()


def _is_pokemon_weak_against(pokemon: pd.core.series.Series, against_type_column: str) -> bool:
    
    return pokemon[against_type_column] >= 2.0


def _is_pokemon_strong_against(pokemon: pd.core.series.Series, against_type_column: str) -> bool:
    
    return pokemon[against_type_column] <= 0.5


def _format_suggestions(suggestions_df: pd.DataFrame, sprites_df: pd.DataFrame) -> pd.DataFrame:

    suggestions_df.rename(columns={'antecedents': 'Freq. utilizado com', 'consequents': 'Pokémon', 'confidence': 'Confiança', 'lift': 'Lift', 'choice_advantage': 'É um reforço contra'}, inplace=True)
    suggestions_df['Confiança'] = [round(valor * 100, 2) for valor in suggestions_df['Confiança']]
    suggestions_df['Lift'] = [round(valor, 2) for valor in suggestions_df['Lift']]
    suggestions_df['Pokémon'] = suggestions_df['Pokémon'].apply(lambda x: str(x)[11:-2].replace("'", ""))
    suggestions_df = pd.merge(sprites_df, suggestions_df, on='Pokémon', how='inner')
    suggestions_df = suggestions_df.sort_values(by=['Confiança', 'Lift'], ascending=False).reset_index(drop=True)
    suggestions_df['Freq. utilizado com'] = suggestions_df['Freq. utilizado com'].apply(lambda equipe: list(equipe))
    return suggestions_df[['Sprite', 'Pokémon', '1º tipo', '2º tipo', 'Freq. utilizado com', 'Confiança', 'Lift', 'É um reforço contra']]


def _get_team_weakness_columns(against_type_columns: list, df: pd.DataFrame, team: list) -> set:
    
    team_effectiveness = {
        'strengths': set(), 
        'weaknesses': set()
    }
    for pokemon_name in team:
        pokemon = df[df['name'] == pokemon_name]
        for against_type_column in against_type_columns:
            if _is_pokemon_weak_against(pokemon, against_type_column).any():
                team_effectiveness['weaknesses'].add(against_type_column)
            elif _is_pokemon_strong_against(pokemon, against_type_column).any():
                team_effectiveness['strengths'].add(against_type_column)
    team_weakness_columns = team_effectiveness['weaknesses'] - team_effectiveness['strengths']
    return team_weakness_columns 


def _get_team_weaknesses(team_weakness_columns) -> list:

    team_weaknesses = [col[8:] for col in team_weakness_columns]
    return team_weaknesses


def _filter_suggestions(team: list, rules_df: pd.DataFrame) -> pd.DataFrame:
    
    suggestions_df = rules_df[rules_df['antecedents'].apply(lambda pokemon: pokemon.issubset(frozenset(team)))].copy()
    suggestions_df = suggestions_df[~suggestions_df['consequents'].isin(suggestions_df['antecedents'])]
    suggestions_df = suggestions_df[suggestions_df['consequent_len'] == 1]

    return suggestions_df


def _fill_choice_advantage_column(team_weakness_columns: set, pokedex: pd.DataFrame, suggestions_df: pd.DataFrame) -> pd.DataFrame:
    
    suggestions_df['choice_advantage'] = ''
    for suggestion in suggestions_df['consequents']:    
        name = list(suggestion)[0]
        pokemon = pokedex[pokedex['name'] == name]
        choice_advantage = ''
        for team_weakness in team_weakness_columns:
            if _is_pokemon_strong_against(pokemon, team_weakness).any():
                choice_advantage += (team_weakness[8:] + ', ')
        suggestions_df.loc[suggestions_df['consequents'] == suggestion, 'choice_advantage'] = choice_advantage[:-2]
    return suggestions_df


def _group_suggestions(suggestions_df: pd.DataFrame) -> pd.DataFrame:
    
    suggestions_df = suggestions_df.groupby('Pokémon').agg({
        'Sprite': lambda x: x.unique()[0],
        '1º tipo': lambda x: x.unique()[0],
        '2º tipo': lambda x: x.unique()[0],
        'Freq. utilizado com': lambda x: list(x),
        'Confiança': lambda x: list(x),
        'Lift': lambda x: list(x),
        'É um reforço contra': lambda x: list(x.unique())
    }).reset_index(names='Pokémon')
    return suggestions_df


def find_suggestions_by_team(team: list) -> object:

    team = [pokemon.title() for pokemon in team]
    interest_columns = ['name', 'against_bug', 'against_dark', 'against_dragon', 'against_electric', 'against_fairy', 
                        'against_fighting', 'against_fire', 'against_flying', 'against_ghost', 'against_grass', 
                        'against_ground', 'against_ice', 'against_normal', 'against_poison', 'against_psychic', 
                        'against_rock', 'against_steel', 'against_water']
    pokedex = get_pokedex_df(interest_columns)
    against_type_columns = interest_columns[1:]
    team_weakness_columns = _get_team_weakness_columns(against_type_columns, pokedex, team)
    team_weaknesses = _get_team_weaknesses(team_weakness_columns)
    rules_df = get_rules_df()
    sprites_df = get_sprites_df()
    
    if _is_team_complete(team):
        return {
            'Resultado': 'Equipe completa!',
            'Fraquezas': team_weaknesses
        }
    else:
        suggestions = _filter_suggestions(team, rules_df)
        if _has_suggestions(suggestions):
            suggestions = _fill_choice_advantage_column(team_weakness_columns, pokedex, suggestions)
            suggestions = _format_suggestions(suggestions, sprites_df)
            suggestions = _group_suggestions(suggestions)

            suggestions = suggestions.to_dict('records')
            suggestions.append({'Fraquezas': team_weaknesses})
            return suggestions
        return 'Não temos sugestões para essa equipe :('


def get_all_sprites() -> dict:

    sprites_df = get_sprites_df()
    return sprites_df.to_dict('records')
