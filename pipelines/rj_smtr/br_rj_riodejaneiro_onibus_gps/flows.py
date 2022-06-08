# -*- coding: utf-8 -*-
"""
Flows for br_rj_riodejaneiro_onibus_gps
"""

from prefect import Parameter, case
from prefect.run_configs import KubernetesRun
from prefect.storage import GCS

# EMD Imports #

from pipelines.constants import constants as emd_constants
from pipelines.utils.decorators import Flow
from pipelines.utils.execute_dbt_model.tasks import get_k8s_dbt_client

# SMTR Imports #

from pipelines.rj_smtr.constants import constants

from pipelines.rj_smtr.schedules import (
    # every_minute,
    every_hour,
)
from pipelines.rj_smtr.tasks import (
    create_current_date_hour_partition,
    create_local_partition_path,
    fetch_dataset_sha,
    get_materialization_date_range,
    # get_local_dbt_client,
    get_raw,
    run_dbt_command,
    save_raw_local,
    save_treated_local,
    set_last_run_timestamp,
    upload_logs_to_bq,
    bq_upload,
)
from pipelines.rj_smtr.br_rj_riodejaneiro_onibus_gps.tasks import (
    pre_treatment_br_rj_riodejaneiro_onibus_gps,
)

# Flows #

with Flow(
    "SMTR: GPS SPPO - Materialização",
    code_owners=["@hellcassius#1223", "@fernandascovino#9750"],
) as materialize_sppo:

    # Get default parameters #
    dataset_id = Parameter("dataset_id", default=constants.GPS_SPPO_DATASET_ID.value)
    table_id = Parameter("table_id", default=constants.GPS_SPPO_TREATED_TABLE_ID.value)
    raw_table_id = Parameter(
        "raw_table_id", default=constants.GPS_SPPO_RAW_TABLE_ID.value
    )
    rebuild = Parameter("rebuild", False)

    # Set dbt client #
    dbt_client = get_k8s_dbt_client(mode="prod")
    # Use the command below to get the dbt client in dev mode:
    # dbt_client = get_local_dbt_client(host="localhost", port=3001)

    # Set specific run parameters #
    date_range = get_materialization_date_range(
        dataset_id=dataset_id,
        table_id=table_id,
        raw_table_id=raw_table_id,
        table_date_column_name="data",
    )
    dataset_sha = fetch_dataset_sha(
        dataset_id=dataset_id,
    )

    # Run materialization #
    with case(rebuild, True):
        RUN = run_dbt_command(
            dbt_client=dbt_client,
            dataset_id=dataset_id,
            table_id=table_id,
            command="run",
            _vars=[date_range, dataset_sha],
            upstream=True,
            downstream=True,
            flags="--full-refresh",
        )
        set_last_run_timestamp(dataset_id=dataset_id, table_id=table_id, wait=RUN)
    with case(rebuild, False):
        RUN = run_dbt_command(
            dbt_client=dbt_client,
            dataset_id=dataset_id,
            table_id=table_id,
            command="run",
            _vars=[date_range, dataset_sha],
            upstream=True,
            downstream=True,
        )
        set_last_run_timestamp(dataset_id=dataset_id, table_id=table_id, wait=RUN)


with Flow(
    "SMTR: GPS SPPO - Captura",
    code_owners=["@hellcassius#1223", "@fernandascovino#9750"],
) as captura_sppo:

    # Get default parameters #
    dataset_id = Parameter("dataset_id", default=constants.GPS_SPPO_DATASET_ID.value)
    table_id = Parameter("table_id", default=constants.GPS_SPPO_RAW_TABLE_ID.value)
    url = Parameter("url", default=constants.GPS_SPPO_API_BASE_URL.value)
    secret_path = Parameter(
        "secret_path", default=constants.GPS_SPPO_API_SECRET_PATH.value
    )

    # Run tasks #
    file_dict = create_current_date_hour_partition()

    filepath = create_local_partition_path(
        dataset_id=dataset_id,
        table_id=table_id,
        filename=file_dict["filename"],
        partitions=file_dict["partitions"],
    )

    status_dict = get_raw(url=url, source=secret_path)

    raw_filepath = save_raw_local(data=status_dict["data"], file_path=filepath)

    treated_status = pre_treatment_br_rj_riodejaneiro_onibus_gps(
        status_dict=status_dict
    )

    upload_logs_to_bq(
        dataset_id=dataset_id,
        parent_table_id=table_id,
        timestamp=status_dict["timestamp"],
        error=status_dict["error"],
    )

    treated_filepath = save_treated_local(
        dataframe=treated_status["df"], file_path=filepath
    )

    bq_upload(
        dataset_id=dataset_id,
        table_id=table_id,
        filepath=treated_filepath,
        raw_filepath=raw_filepath,
        partitions=file_dict["partitions"],
    )

materialize_sppo.storage = GCS(emd_constants.GCS_FLOWS_BUCKET.value)
materialize_sppo.run_config = KubernetesRun(
    image=emd_constants.DOCKER_IMAGE.value,
    labels=[emd_constants.RJ_SMTR_AGENT_LABEL.value],
)
materialize_sppo.schedule = every_hour

captura_sppo.storage = GCS(emd_constants.GCS_FLOWS_BUCKET.value)
captura_sppo.run_config = KubernetesRun(
    image=emd_constants.DOCKER_IMAGE.value,
    labels=[emd_constants.RJ_SMTR_AGENT_LABEL.value],
)
# captura_sppo.schedule = every_minute