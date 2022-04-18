"""
Helper tasks that could fit any pipeline.
"""
from pathlib import Path
from typing import Union
from datetime import timedelta
from uuid import uuid4

import glob
import basedosdados as bd
import pandas as pd
from prefect import task

from pipelines.constants import constants
from pipelines.utils.utils import get_username_and_password_from_secret, log

##################
#
# Hashicorp Vault
#
##################


@task(checkpoint=False, nout=2)
def get_user_and_password(secret_path: str):
    """
    Returns the user and password for the given secret path.
    """
    log(f"Getting user and password for secret path: {secret_path}")
    return get_username_and_password_from_secret(secret_path)


###############
#
# Upload to GCS
#
###############
@task(
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=timedelta(seconds=constants.TASK_RETRY_DELAY.value),
)
def dump_header_to_csv(
    data_path: Union[str, Path], wait=None  # pylint: disable=unused-argument
):
    """
    Writes a header to a CSV file.
    """
    # Remove filename from path
    path = Path(data_path)
    if not path.is_dir():
        path = path.parent
    files = glob.glob(f"{path}/*")
    file = files[0] if files else ""

    # Read just first row
    dataframe = pd.read_csv(file, nrows=1)

    # Create directory if it doesn't exist
    save_header_path = Path(f"data/{uuid4()}/header.csv")
    save_header_path.parent.mkdir(parents=True, exist_ok=True)

    # Write dataframe to CSV
    dataframe.to_csv(save_header_path, index=False, encoding="utf-8")
    log(f"Wrote header CSV: {path}")

    return save_header_path


@task(
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=timedelta(seconds=constants.TASK_RETRY_DELAY.value),
)
def upload_to_gcs(
    path: Union[str, Path],
    dataset_id: str,
    table_id: str,
    wait=None,  # pylint: disable=unused-argument
) -> None:
    """
    Uploads a bunch of CSVs using BD+
    """
    # pylint: disable=C0103
    tb = bd.Table(dataset_id=dataset_id, table_id=table_id)
    # st = bd.Storage(dataset_id=dataset_id, table_id=table_id)

    if tb.table_exists(mode="staging"):
        # the name of the files need to be the same or the data doesn't get overwritten
        tb.append(
            filepath=path,
            if_exists="replace",
        )

        log(
            f"Successfully uploaded {path} to {tb.bucket_name}.staging.{dataset_id}.{table_id}"
        )

    else:
        # pylint: disable=C0301
        log(
            "Table does not exist in STAGING, need to create it in local first.\nCreate and publish the table in BigQuery first."
        )


@task(
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=timedelta(seconds=constants.TASK_RETRY_DELAY.value),
)
def create_bd_table(
    path: Union[str, Path],
    dataset_id: str,
    table_id: str,
    dump_type: str,
    wait=None,  # pylint: disable=unused-argument
) -> None:
    """
    Create table using BD+
    """
    # pylint: disable=C0103
    tb = bd.Table(dataset_id=dataset_id, table_id=table_id)

    # pylint: disable=C0103
    st = bd.Storage(dataset_id=dataset_id, table_id=table_id)

    # full dump
    if dump_type == "append":
        if tb.table_exists(mode="staging"):
            log(
                f"Mode append: Table {st.bucket_name}.{dataset_id}.{table_id} already exists"
            )
        else:
            tb.create(
                path=path,
                location="southamerica-east1",
            )
            log(
                f"Mode append: Sucessfully created a new table {st.bucket_name}.{dataset_id}.{table_id}"
            )  # pylint: disable=C0301

            st.delete_table(
                mode="staging", bucket_name=st.bucket_name, not_found_ok=True
            )
            log(
                f"Mode append: Sucessfully remove header data from {st.bucket_name}.{dataset_id}.{table_id}"
            )  # pylint: disable=C0301
    elif dump_type == "overwrite":
        if tb.table_exists(mode="staging"):
            log(
                f"Mode overwrite: Table {st.bucket_name}.{dataset_id}.{table_id} already exists, DELETING OLD DATA!"
            )  # pylint: disable=C0301
            st.delete_table(
                mode="staging", bucket_name=st.bucket_name, not_found_ok=True
            )
        # prod datasets is public if the project is datario. staging are private im both projects
        dataset_is_public = tb.client["bigquery_prod"].project == "datario"
        tb.create(
            path=path,
            if_storage_data_exists="replace",
            if_table_config_exists="replace",
            if_table_exists="replace",
            location="southamerica-east1",
            dataset_is_public=dataset_is_public,
        )

        log(
            f"Mode overwrite: Sucessfully created table {st.bucket_name}.{dataset_id}.{table_id}"
        )
        st.delete_table(mode="staging", bucket_name=st.bucket_name, not_found_ok=True)
        log(
            f"Mode overwrite: Sucessfully remove header data from {st.bucket_name}.{dataset_id}.{table_id}"
        )  # pylint: disable=C0301