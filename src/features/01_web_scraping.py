import pandas as pd
import logging
import asyncio
from aiohttp import ClientSession, ClientError
from tqdm import tqdm
from bs4 import BeautifulSoup, SoupStrainer
from src.utils.utils import get_logger, Clock


async def get_soup(session, target_url: str, subset_to_parse: SoupStrainer) -> BeautifulSoup:
    try:
        async with session.get(target_url) as response:
            response.raise_for_status()
            page = await response.text()
            soup = BeautifulSoup(page, 'lxml', parse_only=subset_to_parse)
        return soup
    except ClientError as e:
        print(f"\nErro ao obter a página: {str(e)}")
        return None


def get_player_names(logger: logging.Logger, tags: list) -> list:
    player_names = []
    num_tags = len(tags)
    logger.info("Uma nova iteração começará agora...")
    iteration_time = Clock("Construção da lista de jogadores")
    with tqdm(total=num_tags) as progress_bar:
        progress_bar.set_description("Montando lista com os nomes de usuário dos top 500 jogadores da ladder gen9ou...")
        for tag in tags:
            username = tag.get_text().replace(' ', '')
            player_names.append(username)
            progress_bar.update(1)
    iteration_time.stop_watch()
    return player_names


async def get_gen9ou_replay_ids(logger: logging.Logger, session, player_names: list, semaphore: asyncio.Semaphore) -> list:

    gen9ou_replay_ids = []
    replay_search_url = 'https://replay.pokemonshowdown.com/search/?output=html&user='
    num_players = len(player_names)

    logger.info("Uma nova iteração começará agora...")
    iteration_time = Clock("Coleta dos links de replays gen9ou")
    interest_subset = SoupStrainer('a')

    with tqdm(total=num_players) as progress_bar:
        progress_bar.set_description("Minerando os links de replay gen9ou de cada jogador e montando uma lista...")
        tasks = []

        async def process_player(player):
            async with semaphore:
                soup = await get_soup(session, replay_search_url + player, interest_subset)
                user_gen9ou_replay_ids = [link.get('href') for link in soup.find_all('a') if
                                          link.contents[0].contents[0][1:-1] == 'gen9ou']
                gen9ou_replay_ids.extend(user_gen9ou_replay_ids)
                return 1

        for name in player_names:
            tasks.append(asyncio.create_task(process_player(name)))
        for task in asyncio.as_completed(tasks):
            await task
            progress_bar.update(1)

    iteration_time.stop_watch()
    return gen9ou_replay_ids


async def fetch_replay(session, replay_url, replay_id):
    try:
        async with session.get(replay_url + replay_id) as response:
            response.raise_for_status()
            return await response.text()
    except ClientError as e:
        raise Exception(f"Erro ao buscar replay: {str(e)}")
    except Exception as e:
        raise Exception(f"Erro inesperado ao buscar replay: {str(e)}")


async def get_teams(logger: logging.Logger, replay_ids: list, semaphore: asyncio.Semaphore) -> list:
    teams = []
    replay_url = 'https://replay.pokemonshowdown.com/'
    num_replays_id = len(replay_ids)
    logger.info("Uma nova iteração começará agora...")
    iteration_time = Clock("Coleta de todas as equipes")

    async with ClientSession() as session:
        tasks = []
        interest_subset = SoupStrainer(class_="log")

        with tqdm(total=num_replays_id) as progress_bar:
            progress_bar.set_description("Coletando todas as equipes de cada replay...")

            async def fetch_and_process_replay(replay_id):
                async with semaphore:
                    try:
                        response = await fetch_replay(session, replay_url, replay_id)
                    except Exception as e:
                        logger.error(f"Erro ao buscar replay: {str(e)}")
                        return
                    try:
                        soup = BeautifulSoup(response, 'lxml', parse_only=interest_subset)
                        if soup.find(class_='log'):
                            log = soup.find(class_='log').get_text()
                            pokemons = log.split('|poke|')[1:13]
                            if len(pokemons) != 0:
                                clean_teams = extract_clean_teams(pokemons)
                                teams.extend(clean_teams)
                    except Exception as e:
                        logger.error(f"Erro no processamento do replay: {str(e)}")

            for id_ in replay_ids:
                task = asyncio.create_task(fetch_and_process_replay(id_))
                tasks.append(task)

            for task in asyncio.as_completed(tasks):
                await task
                progress_bar.update(1)

    iteration_time.stop_watch()
    return teams


def extract_clean_teams(pokemons: list) -> list[list[str]]:
    formatted_teams = []
    pokemons[-1] = pokemons[-1].split('\n')[0]
    pokemons = [text.split('|') for text in pokemons]
    pokemons = [text[1] for text in pokemons]
    pokemons = [text.split(',') for text in pokemons]
    pokemons = [text[0] for text in pokemons]
    formatted_teams.append(pokemons[:6])
    formatted_teams.append(pokemons[6:])
    return formatted_teams


def build_teams_df(logger: logging.Logger, teams: list) -> pd.DataFrame:
    columns = ['pokemon_1', 'pokemon_2', 'pokemon_3', 'pokemon_4', 'pokemon_5', 'pokemon_6']
    teams_df = pd.DataFrame(columns=columns)
    num_teams = len(teams)
    logger.info("Uma nova iteração começará agora...")
    iteration_time = Clock("Construção do DataFrame")
    with tqdm(total=num_teams) as progress_bar:
        progress_bar.set_description("Filtrando apenas as equipes de 6 pokémons e adicionando ao DataFrame...")
        for index, team in enumerate(teams):
            if len(team) == 6:
                teams_df.loc[index] = team
            progress_bar.update(1)
    iteration_time.stop_watch()
    return teams_df


async def main():

    # Inicializando o logger:
    logger_ = logging.getLogger(__name__)
    logger_ = get_logger(logger=logger_)

    ladder_url = 'https://pokemonshowdown.com/ladder/gen9ou'
    interest_class = 'subtle'
    interest_subset_ = SoupStrainer(class_=interest_class)

    # Coletando e criando uma lista com as tags que contém os nomes dos top 500 jogadores da ladder gen9ou:
    logger_.info("Buscando as tags que possuem os nomes dos top 500 jogadores da ladder gen9ou...")
    async with ClientSession() as session_:
        soup_ = await get_soup(session_, ladder_url, interest_subset_)
    top500_tag_list = soup_.find_all(class_=interest_class)
    logger_.info("Tags coletadas.")

    # Construíndo a lista de usernames dos top 500 jogadores:
    top500_players = get_player_names(logger_, top500_tag_list)

    # Semáforo para controlar o acesso concorrente às listas
    semaphore = asyncio.Semaphore(10)

    # Construíndo a lista de ids de replay gen9ou:
    async with ClientSession() as session_:
        gen9ou_replay_ids_ = await get_gen9ou_replay_ids(logger_, session_, top500_players, semaphore)
    logger_.info(f"Existem {len(gen9ou_replay_ids_)} id's de replay gen9ou na base!")

    # Construíndo a lista de equipes utilizadas pelos jogadores e seus adversários:
    teams_ = await get_teams(logger_, gen9ou_replay_ids_, semaphore)
    logger_.info(f'Existem {len(teams_)} equipes na base!')

    # Construíndo um dataframe pandas apenas com as equipes de 6 pokémons:
    teams_df_ = build_teams_df(logger_, teams_)
    logger_.info(f'Existem {len(teams_df_)} equipes de 6 pokémons na base!')

    # Exportando a base como csv:
    outfile_path = 'C:\\Users\\User\\Documents\\jupyter_notebooks\\ufmg\\itemset_mining_applied_to_pokemon_teams\\data\\processed\\'
    teams_df_.to_csv(outfile_path + 'ladder_teams.csv', index=False)
    logger_.info("A base foi exportada como csv!")


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
