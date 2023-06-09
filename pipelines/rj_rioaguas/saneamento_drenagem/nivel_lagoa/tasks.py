# -*- coding: utf-8 -*-

"""
Tasks para pipeline de dados de nível da Lagoa Rodrigo de Freitas.
Fonte: Squitter.
"""
# pylint: disable= C0327,W0106,R0913,R0914
from datetime import timedelta
from pathlib import Path
from typing import Union, Tuple
import pandas as pd
import pendulum
from bs4 import BeautifulSoup
from prefect import task

from pipelines.constants import constants

# from pipelines.rj_cor.meteorologia.utils import save_updated_rows_on_redis
from pipelines.rj_rioaguas.utils import login
from pipelines.utils.utils import (
    get_vault_secret,
    log,
    to_partitions,
    parse_date_columns,
    save_updated_rows_on_redis,
)


@task
def download_file(download_url):
    """
    Função para download de tabela com os dados.

    Args:
    download_url (str): URL onde a tabela está localizada.
    """
    # Acessar username e password
    dicionario = get_vault_secret("rioaguas_nivel_lagoa_squitter")
    url = dicionario["data"]["url"]
    user = dicionario["data"]["user"]
    password = dicionario["data"]["password"]
    session = login(url, user, password)
    page = session.get(download_url)
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find_all("table")
    dfr = pd.read_html(str(table))[0]
    return dfr


@task(
    nout=2,
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=timedelta(seconds=constants.TASK_RETRY_DELAY.value),
)
def tratar_dados(
    dfr: pd.DataFrame, dataset_id: str, table_id: str, mode: str = "prod"
) -> Tuple[pd.DataFrame, bool]:
    """
    Tratar dados para o padrão estabelecido.
    """

    # Renomeia colunas
    dfr = dfr.rename(
        columns={"Hora Leitura": "data_medicao", "Nível [m]": "nivel_agua"}
    )
    # Adiciona coluna para id e nome da lagoa
    dfr["id_estacao"] = "1"
    dfr["nome_estacao"] = "Lagoa rodrigo de freitas"
    # Remove duplicados
    dfr = dfr.drop_duplicates(subset=["id_estacao", "data_medicao"], keep="first")
    # Acessa o redis e mantem apenas linhas que ainda não foram salvas
    log(f"[DEBUG]: dados coletados\n{dfr.tail()}")
    dfr = save_updated_rows_on_redis(
        dfr,
        dataset_id,
        table_id,
        unique_id="id_estacao",
        date_column="data_medicao",
        date_format="%d/%m/%Y %H:%M",
        mode=mode,
    )
    log(f"[DEBUG]: dados que serão salvos no df\n{dfr.tail()}")

    # If df is empty stop flow
    empty_data = dfr.shape[0] == 0
    log(f"[DEBUG]: dataframe is empty: {empty_data}")

    return (
        dfr[["data_medicao", "id_estacao", "nome_estacao", "nivel_agua"]],
        empty_data,
    )


@task
def salvar_dados(dados: pd.DataFrame) -> Union[str, Path]:
    """
    Salvar dados em csv.
    """
    prepath = Path("/tmp/nivel_lagoa/")
    prepath.mkdir(parents=True, exist_ok=True)

    partition_column = "data_medicao"
    dataframe, partitions = parse_date_columns(dados, partition_column)
    current_time = pendulum.now("America/Sao_Paulo").strftime("%Y%m%d%H%M")

    # Cria partições a partir da data
    to_partitions(
        data=dataframe,
        partition_columns=partitions,
        savepath=prepath,
        data_type="csv",
        suffix=current_time,
    )
    log(f"[DEBUG] Files saved on {prepath}")
    return prepath
