import logging
import time
from timeit import default_timer as timer

"""
Utils
Funções úteis
get_logger: Retorna um objeto do tipo logger
"""

__all__ = [
    'get_logger',
    'format_time',
]

def get_logger(logger, filename: str = 'experimento.log', level: int = 10):
    """
    Retorna um objeto do tipo logger
    Parâmetros
    ----------
    logger
        Objeto do tipo logger
    filename: str
        Nome do arquivo de logo. Default: 'experiment.log'
    level: int
        Nível do log. Default: 10 - DEBUG
    Retorno
    -------
    object
        Objeto logger configurado
    """

    logger.setLevel(level)

    FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(FORMAT)

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
        if elapsed_time >= 3600:
            return time.strftime("%Hh%Mm%Ss", time.gmtime(elapsed_time))
        elif elapsed_time >= 60:
            return time.strftime("%Mm%Ss", time.gmtime(elapsed_time))
        else:
            return time.strftime("%Ss", time.gmtime(elapsed_time))


logger = logging.getLogger(__name__)
logger = get_logger(logger=logger)

class Clock():
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
    
    def stop_watch(self)->None:        
        """
        Calcula o tempo e registra a diferença de tempo para executar a tarefa rotulada.
        """
        self.end = timer()
        elapsed_time = self.end - self.start
        
        logger.info(f"{self.label} levou {format_time(elapsed_time)} para ser executado.")

        