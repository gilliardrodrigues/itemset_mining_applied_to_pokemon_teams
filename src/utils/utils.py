import logging
import time
import json
import plotly.express as px
import plotly.offline as pyo
import pandas as pd
from timeit import default_timer as timer
from datetime import datetime
pyo.init_notebook_mode()


"""
Utils
Funções úteis:
visualize_missing_data -> mostra os dados faltantes através de um gráfico de barras.
load_json -> carrega um arquivo JSON armazenado em disco.
export_json -> exporta um dicionário como JSON.
frozenset_converter -> reconstrói um frozenset a partir de uma string e o retorna.
getlogger -> retorna um objeto do tipo logger.
format_time -> retorna o tempo formatado de acordo com o necessário.
"""

__all__ = [
    'visualize_missing_data',
    'load_json',
    'export_json',
    'frozenset_converter',
    'get_logger',
    'format_time',
    'Clock'
]


def visualize_missing_data(df: pd.DataFrame):
    """
    Para as colunas que possuem dados faltantes, mostra as porcentagens na foram de um gráfico de barras.     
    Parâmetros:
    ----------
    df : pd.DataFrame
        DataFrame com os dados.
    Retorno:
    -------
    """
    if df.isna().sum().sum() != 0:
        missing_values = df.isna().sum() / df.shape[0] * 100      
        only_missing_values = missing_values.drop(missing_values[missing_values == 0].index).sort_values(ascending=True)
        missing_values_df = pd.DataFrame({'Percentual de valores faltantes (%)': only_missing_values})
        fig = px.bar(missing_values_df, x=missing_values_df['Percentual de valores faltantes (%)'], y=missing_values_df.index,
                     orientation='h', title='Colunas com dados faltantes e seus percentuais',
                     labels={"index": "Coluna"}, height=400, width=700)
        fig.update_traces(
            hovertemplate='%{x:.2f}%',
        )
        fig.show()
        pyo.plot(fig)
    else:
        print('Sem valores faltantes no dataframe!')

        
def load_json(file_path: str) -> dict:
    """
    Carrega o JSON armazenado no caminho informado.
    Parâmetros
    ----------
    file_path
        Caminho para o arquivo JSON armazenado em disco.
    Retorno
    -------
    dict
        JSON na forma de um dicionário.
    """
    with open(file_path, "r", encoding="utf-8") as readfile:
        data = json.load(readfile)
    return data


def export_json(json_file: dict, file_path: str):
    """
    Exporta o dicionário como um JSON.
    Parâmetros
    ----------
    json_file
        JSON na forma de dicionário.
    file_path
        Caminho onde o JSON deverá ser armazenado em disco.
    Retorno
    -------
    """
    with open(file_path, "w", encoding="utf-8") as outfile:
        json.dump(json_file, outfile, indent = 4, ensure_ascii=False)


def frozenset_converter(text: str):
    """
    Reconstrói um frozenset a partir de uma string e o retorna.
    Parâmetros
    ----------
    text: str
        Frozenset na forma de string, ex: "frozenset({'a', 'b'})"
    Retorno
    -------
    frozenset, str
        Frozenset ou o próprio texto em caso de erro.
    """
    try:
        elements = [elem.strip() for elem in text[12:-3].replace("'", "").split(", ")]
        return frozenset(elements)
    except (AttributeError, ValueError):
        return text


def get_logger(logger: logging.Logger, level: int = 10) -> logging.Logger:
    """
    Retorna um objeto do tipo logger
    Parâmetros
    ----------
    logger: logging.Logger
        Objeto do tipo logger
    level: int
        Nível do log. Default: 10 - DEBUG
    Retorno
    -------
    logging.Logger
        Objeto logger configurado
    """
    today = datetime.today()
    filename = f'experimento_{today.day}_{today.month}_{today.year}.log'

    logger.setLevel(level)

    _format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(_format)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.FileHandler(filename=filename, mode='a', encoding='utf-8')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def format_time(elapsed_time: float) -> str:
    """
    Formata o tempo de acordo com a quantidade e retorna.
    Parâmetros
    ----------
    elapsed_time
        Tempo como float.
    Retorno
    -------
    str
        Tempo formatado.
    """
    if elapsed_time >= 86400:
        return time.strftime("%dd%Hh%Mm%Ss", time.gmtime(elapsed_time))
    elif elapsed_time >= 3600:
        return time.strftime("%Hh%Mm%Ss", time.gmtime(elapsed_time))
    elif elapsed_time >= 60:
        return time.strftime("%Mm%Ss", time.gmtime(elapsed_time))
    else:
        return time.strftime("%Ss", time.gmtime(elapsed_time))


logger_ = logging.getLogger(__name__)
logger_ = get_logger(logger=logger_)


class Clock:
    def __init__(self, process_label: str = 'default'):
        """
        Classe para calcular o tempo que uma tarefa leva para ser executada.

        Parâmetros
        ----------
        process_label : str, optional
            Processo que terá o tempo medido, por padrão 'default'.
        """
        self.start = timer()
        self.end = None
        self.elapsed_time = None
        self.label = process_label

    def stop_watch(self) -> None:
        """
        Calcula o tempo e registra a diferença de tempo para executar a tarefa rotulada.
        """
        self.end = timer()
        elapsed_time = self.end - self.start

        logger_.info(f"{self.label} levou {format_time(elapsed_time)} para ser executado.")

