# -*- coding: utf-8 -*-
"""
Flows for veiculos
"""

# from prefect import Parameter, case
from prefect.run_configs import KubernetesRun
from prefect.storage import GCS

# EMD Imports #

from pipelines.constants import constants as emd_constants
from pipelines.utils.decorators import Flow

from pipelines.utils.tasks import (
    rename_current_flow_run_now_time,
    get_current_flow_mode,
    get_current_flow_labels,
)

# SMTR Imports #

from pipelines.rj_smtr.veiculo.constants import constants

from pipelines.rj_smtr.schedules import (
    every_day_hour_five,
)
from pipelines.rj_smtr.tasks import (
    create_date_partition,
    create_local_partition_path,
    get_current_timestamp,
    get_raw,
    parse_timestamp_to_string,
    save_raw_local,
    save_treated_local,
    upload_logs_to_bq,
    bq_upload,
)

from pipelines.rj_smtr.veiculo.tasks import (
    pre_treatment_sppo_licenciamento,
    pre_treatment_sppo_infracao,
)

# Flows #

# flake8: noqa: E501
sppo_licenciamento_captura_name = f"SMTR: Captura - {constants.DATASET_ID.value}.{constants.SPPO_LICENCIAMENTO_TABLE_ID.value}"
with Flow(
    sppo_licenciamento_captura_name,
    code_owners=["rodrigo", "fernanda"],
) as sppo_licenciamento_captura:

    timestamp = get_current_timestamp()

    LABELS = get_current_flow_labels()
    MODE = get_current_flow_mode(LABELS)

    # Rename flow run
    rename_flow_run = rename_current_flow_run_now_time(
        prefix=f"{sppo_licenciamento_captura_name} - ", now_time=timestamp
    )

    # SETUP #
    partitions = create_date_partition(timestamp)

    filename = parse_timestamp_to_string(timestamp)

    filepath = create_local_partition_path(
        dataset_id=constants.DATASET_ID.value,
        table_id=constants.SPPO_LICENCIAMENTO_TABLE_ID.value,
        filename=filename,
        partitions=partitions,
    )

    # EXTRACT
    raw_status = get_raw(
        url=constants.SPPO_LICENCIAMENTO_URL.value,
        filetype="txt",
        csv_args=constants.SPPO_LICENCIAMENTO_CSV_ARGS.value,
    )

    raw_filepath = save_raw_local(status=raw_status, file_path=filepath)

    # TREAT
    treated_status = pre_treatment_sppo_licenciamento(
        status=raw_status, timestamp=timestamp
    )

    treated_filepath = save_treated_local(status=treated_status, file_path=filepath)

    # LOAD
    error = bq_upload(
        dataset_id=constants.DATASET_ID.value,
        table_id=constants.SPPO_LICENCIAMENTO_TABLE_ID.value,
        filepath=treated_filepath,
        raw_filepath=raw_filepath,
        partitions=partitions,
        status=treated_status,
    )
    upload_logs_to_bq(
        dataset_id=constants.DATASET_ID.value,
        parent_table_id=constants.SPPO_LICENCIAMENTO_TABLE_ID.value,
        timestamp=timestamp,
        error=error,
    )
    sppo_licenciamento_captura.set_dependencies(
        task=partitions, upstream_tasks=[rename_flow_run]
    )

sppo_licenciamento_captura.storage = GCS(emd_constants.GCS_FLOWS_BUCKET.value)
sppo_licenciamento_captura.run_config = KubernetesRun(
    image=emd_constants.DOCKER_IMAGE.value,
    labels=[emd_constants.RJ_SMTR_AGENT_LABEL.value],
)
sppo_licenciamento_captura.schedule = every_day_hour_five

sppo_infracao_captura_name = f"SMTR: Captura - {constants.DATASET_ID.value}.{constants.SPPO_INFRACAO_TABLE_ID.value}"
with Flow(
    sppo_infracao_captura_name,
    code_owners=["rodrigo", "fernanda"],
) as sppo_infracao_captura:

    timestamp = get_current_timestamp()

    LABELS = get_current_flow_labels()
    MODE = get_current_flow_mode(LABELS)

    # Rename flow run
    rename_flow_run = rename_current_flow_run_now_time(
        prefix=f"{sppo_infracao_captura_name} - ", now_time=timestamp
    )

    # SETUP #
    partitions = create_date_partition(timestamp)

    filename = parse_timestamp_to_string(timestamp)

    filepath = create_local_partition_path(
        dataset_id=constants.DATASET_ID.value,
        table_id=constants.SPPO_INFRACAO_TABLE_ID.value,
        filename=filename,
        partitions=partitions,
    )

    # EXTRACT
    raw_status = get_raw(
        url=constants.SPPO_INFRACAO_URL.value,
        filetype="txt",
        csv_args=constants.SPPO_INFRACAO_CSV_ARGS.value,
    )

    raw_filepath = save_raw_local(status=raw_status, file_path=filepath)

    # TREAT
    treated_status = pre_treatment_sppo_infracao(status=raw_status, timestamp=timestamp)

    treated_filepath = save_treated_local(status=treated_status, file_path=filepath)

    # LOAD
    error = bq_upload(
        dataset_id=constants.DATASET_ID.value,
        table_id=constants.SPPO_INFRACAO_TABLE_ID.value,
        filepath=treated_filepath,
        raw_filepath=raw_filepath,
        partitions=partitions,
        status=treated_status,
    )
    upload_logs_to_bq(
        dataset_id=constants.DATASET_ID.value,
        parent_table_id=constants.SPPO_INFRACAO_TABLE_ID.value,
        timestamp=timestamp,
        error=error,
    )
    sppo_infracao_captura.set_dependencies(
        task=partitions, upstream_tasks=[rename_flow_run]
    )

sppo_infracao_captura.storage = GCS(emd_constants.GCS_FLOWS_BUCKET.value)
sppo_infracao_captura.run_config = KubernetesRun(
    image=emd_constants.DOCKER_IMAGE.value,
    labels=[emd_constants.RJ_SMTR_AGENT_LABEL.value],
)
sppo_infracao_captura.schedule = every_day_hour_five
