# -*- coding: utf-8 -*-
"""
Constant values for the rj_smtr.veiculo flows
"""

from enum import Enum


class constants(Enum):  # pylint: disable=c0103
    """
    Constant values for the rj_smtr.veiculo flows
    """

    DATASET_ID = "veiculo"

    # VEÍCULOS LICENCIADOS
    # flake8: noqa: E501
    SPPO_LICENCIAMENTO_URL = "https://siurblab.rio.rj.gov.br/SMTR/DADOS%20CADASTRAIS/Cadastro%20de%20Veiculos.txt"
    SPPO_LICENCIAMENTO_TABLE_ID = "sppo_licenciamento_stu"
    SPPO_LICENCIAMENTO_MAPPING_KEYS = {
        "placa": "placa",
        "ordem": "id_veiculo",
        "permissao": "permissao",
        "modal": "modo",
        "ultima_vistoria": "data_ultima_vistoria",
        "cod_planta": "id_planta",
        "cod_mod_carroceria": "id_carroceria",
        "cod_fab_carroceria": "id_interno_carroceria",
        "des_mod_carroceria": "carroceria",
        "cod_mod_chassi": "id_chassi",
        "cod_fab_chassi": "id_fabricante_chassi",
        "des_mod_chassi": "nome_chassi",
        "lotacao_sentado": "quantidade_lotacao_sentado",
        "lotacao_pe": "quantidade_lotacao_pe",
        "elevador": "indicador_elevador",
        "ar_condicionado": "indicador_ar_condicionado",
        "tipo_veiculo": "tipo_veiculo",
        "combustivel": "tipo_combustivel",
        "portas": "quantidade_portas",
        "ano_fabricacao": "ano_fabricacao",
        "wifi": "indicador_wifi",
        "usb": "indicador_usb",
    }
