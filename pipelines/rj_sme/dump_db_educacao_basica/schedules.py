# -*- coding: utf-8 -*-
"""
Schedules for the database dump pipeline
"""

from datetime import timedelta, datetime

from prefect.schedules import Schedule
import pytz

from pipelines.constants import constants
from pipelines.utils.dump_db.utils import generate_dump_db_schedules
from pipelines.utils.utils import untuple_clocks as untuple


#####################################
#
# SME Schedules
#
#####################################

sme_queries = {
    "aluno": {
        "materialize_after_dump": True,
        "materialize_to_datario": False,
        "dump_to_gcs": False,
        "materialization_mode": "prod",
        "dump_mode": "overwrite",
        "dbt_model_secret_parameters": {"hash_seed": "hash_seed"},
        "execute_query": """
            SELECT
                Ano,
                Matricula,
                Nome,
                Sexo,
                Endereco,
                Bairro,
                CEP,
                Filiacao_1,
                Filiacao_2,
                Mora_com_Filiacao,
                CPF,
                NIS_Aluno,
                NIS_Resp,
                Raça_Cor as Raca_Cor,
                Cod_def,
                Deficiência as Deficiencia,
                Tipo_Transporte,
                Bolsa_Familia,
                CFC,
                Territorios_Sociais,
                Clube_Escolar,
                Nucleo_Artes,
                Mais_Educacao,
                DataNascimento,
                Idade_Atual,
                Idade_3112,
                Turma,
                UP_Aval,
                Situacao,
                Cod_Ult_Mov,
                Ult_Movimentação as Ult_Movimentacao,
                Tot_Aluno,
                alu_id,
                tur_id
            FROM GestaoEscolar.dbo.VW_BI_Aluno_lgpd
        """,
    },
    "aluno_historico": {
        "materialize_after_dump": True,
        "materialize_to_datario": False,
        "dump_to_gcs": False,
        "partition_columns": "Ano",
        "partition_date_format": "%Y",
        "materialization_mode": "prod",
        "dump_mode": "append",
        "dbt_model_secret_parameters": {"hash_seed": "hash_seed"},
        "execute_query": """
            SELECT
                *
            FROM GestaoEscolar.dbo.VW_BI_Aluno_Todos_LGPD
        """,
        "interval": timedelta(days=180),
    },
    "aluno_turma": {
        "materialize_after_dump": True,
        "materialize_to_datario": False,
        "dump_to_gcs": False,
        "partition_columns": "Ano",
        "partition_date_format": "%Y",
        "materialization_mode": "prod",
        "dump_mode": "append",
        "execute_query": """
            SELECT
                *
            FROM GestaoEscolar.dbo.VW_BI_Aluno_Turma
        """,
    },
    "avaliacao": {
        "materialize_after_dump": True,
        "materialize_to_datario": False,
        "dump_to_gcs": False,
        "partition_columns": "Ano",
        "partition_date_format": "%Y",
        "materialization_mode": "prod",
        "dump_mode": "append",
        "dbt_model_secret_parameters": {"hash_seed": "hash_seed"},
        "execute_query": "SELECT * FROM GestaoEscolar.dbo.VW_BI_Avaliacao",
    },
    "coc": {  # essa tabela utiliza a view coc0 pois contem o coc 0 e de 1 a 5
        "materialize_after_dump": True,
        "materialize_to_datario": False,
        "dump_to_gcs": False,
        "partition_columns": "Ano",
        "partition_date_format": "%Y",
        "materialization_mode": "prod",
        "dump_mode": "append",
        "execute_query": """
            SELECT
                Ano AS Ano,
                CRE AS CRE,
                Unidade AS Unidade,
                Grupamento AS Grupamento,
                Turma AS Turma,
                Turno AS Turno,
                COC AS COC,
                Turmas AS Turmas,
                Alunos AS Alunos,
                Masculinos AS Masculinos,
                Femininos AS Femininos,
                Não_Def AS Nao_Def,
                Def AS Def,
                Masculinos_Não_Def AS Masculinos_Nao_Def,
                Masculinos_Def AS Masculinos_Def,
                Femininos_Não_Def AS Femininos_Nao_Def,
                Femininos_Def AS Femininos_Def,
                Vagas AS Vagas,
                capacidade AS capacidade,
                tur_id AS tur_id,
                pft_capacidade AS pft_capacidade
            FROM GestaoEscolar.dbo.VW_BI_Aluno_Turma_com_COC0
        """,
    },
    "dependencia": {
        "materialize_after_dump": True,
        "materialize_to_datario": False,
        "dump_to_gcs": False,
        "materialization_mode": "prod",
        "dump_mode": "overwrite",
        "execute_query": "SELECT * FROM GestaoEscolar.dbo.VW_BI_Dependencia",
    },
    "escola": {
        "materialize_after_dump": True,
        "materialize_to_datario": False,
        "dump_to_gcs": False,
        "materialization_mode": "prod",
        "dump_mode": "overwrite",
        "execute_query": """
            SELECT
                CRE,
                Designacao,
                Denominacao,
                Endereco,
                Bairro,
                CEP,
                eMail,
                Telefone,
                Direçao as Direcao,
                MicroArea,
                Polo,
                Tipo_Unidade,
                INEP,
                SICI,
                Salas_Recurso,
                Salas_Aula,
                Salas_Aula_Utilizadas,
                Tot_Escola,
                esc_id
            FROM GestaoEscolar.dbo.VW_BI_Escola
        """,
    },
    "frequencia": {
        "partition_columns": "datainicio",
        "partition_date_format": "%Y-%m-%d",
        "lower_bound_date": "2022-03-01",
        "materialize_after_dump": True,
        "materialize_to_datario": False,
        "dump_to_gcs": False,  # exceeds minimum (2022-05-31 -> 20,41GB)
        "materialization_mode": "prod",
        "dump_mode": "append",
        "dbt_model_secret_parameters": {"hash_seed": "hash_seed"},
        "execute_query": """
            SELECT
                esc_id AS esc_id,
                tur_id AS tur_id,
                turma AS turma,
                alu_id AS alu_id,
                coc AS coc,
                dataInicio AS datainicio,
                dataFim AS datafim,
                diasLetivos AS diasletivos,
                temposLetivos AS temposletivos,
                faltasGlb AS faltasglb,
                dis_id AS dis_id,
                disciplinaCodigo AS disciplinacodigo,
                disciplina AS disciplina,
                faltasDis AS faltasdis,
                cargaHorariaSemanal AS cargahorariasemanal
            FROM GestaoEscolar.dbo.VW_BI_Frequencia
        """,
    },
    "movimentacao": {
        "partition_columns": "Data_mov",
        "partition_date_format": "%Y-%m-%d",
        "lower_bound_date": "2022-03-01",
        "materialize_after_dump": True,
        "materialize_to_datario": False,
        "dump_to_gcs": False,
        "materialization_mode": "prod",
        "dump_mode": "append",
        "dbt_model_secret_parameters": {"hash_seed": "hash_seed"},
        "execute_query": "SELECT * FROM GestaoEscolar.dbo.VW_BI_Movimentacao_lgpd",
    },
    "turma": {
        "dump_mode": "overwrite",
        "materialize_after_dump": True,
        "materialize_to_datario": False,
        "dump_to_gcs": False,
        "materialization_mode": "prod",
        "execute_query": "SELECT * FROM GestaoEscolar.dbo.VW_BI_Turma",
    },
}

sme_clocks = generate_dump_db_schedules(
    interval=timedelta(days=1),
    start_date=datetime(2022, 8, 5, 12, 50, tzinfo=pytz.timezone("America/Sao_Paulo")),
    labels=[
        constants.RJ_SME_AGENT_LABEL.value,
    ],
    db_database="GestaoEscolar",
    db_host="10.70.6.103",
    db_port="1433",
    db_type="sql_server",
    dataset_id="educacao_basica",
    vault_secret_path="clustersqlsme",
    table_parameters=sme_queries,
)

sme_educacao_basica_daily_update_schedule = Schedule(clocks=untuple(sme_clocks))
