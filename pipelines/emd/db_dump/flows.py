"""
Database dumping flows
"""

from uuid import uuid4

from prefect import Flow, Parameter
from prefect.run_configs import KubernetesRun
from prefect.storage import GCS
from pipelines.constants import constants
from pipelines.emd.db_dump.db import Database
from pipelines.emd.db_dump.schedules import (
    daily_update_schedule,
)
from pipelines.emd.db_dump.tasks import (
    create_bd_table,
    database_execute,
    database_fetch,
    database_get,
    dump_batches_to_csv,
    dump_header_to_csv,
    upload_to_gcs,
)
from pipelines.tasks import get_user_and_password
from pipelines.utils import log_task

with Flow("Ingerir tabela de banco SQL") as dump_sql_flow:

    #####################################
    #
    # Parameters
    #
    #####################################

    # SQL Server parameters
    hostname = Parameter("db_host")
    port = Parameter("db_port")
    database = Parameter("db_database")
    database_type = Parameter("db_type")
    query = Parameter("execute_query")

    # Use Vault for credentials
    secret_path = Parameter("vault_secret_path")

    # CSV file parameters
    batch_size = Parameter("batch_size", default=50000)

    # BigQuery parameters
    dataset_id = Parameter("dataset_id")
    table_id = Parameter("table_id")
    dump_type = Parameter("dump_type", default="append")  # overwrite or append

    #####################################
    #
    # Tasks section #0 - Get credentials
    #
    #####################################

    # Get credentials from Vault
    user, password = get_user_and_password(secret_path=secret_path)

    #####################################
    #
    # Tasks section #1 - Create table
    #
    #####################################

    # Execute query on SQL Server
    db_object: Database = database_get(
        database_type=database_type,
        hostname=hostname,
        port=port,
        user=user,
        password=password,
        database=database,
    )

    wait_db_execute = database_execute(  # pylint: disable=invalid-name
        database=db_object,
        query=query,
    )

    # Dump batches to CSV files
    wait_batches_path = dump_batches_to_csv(
        database=db_object,
        batch_size=batch_size,
        prepath=f"data/{uuid4()}/",
        wait=wait_db_execute,
    )

    # Create CSV file with headers
    wait_header_path = dump_header_to_csv(
        header_path=f"data/{uuid4()}/",
        data_path=wait_batches_path,
        wait=wait_batches_path,
    )

    # Create table in BigQuery
    wait_create_db = create_bd_table(  # pylint: disable=invalid-name
        path=wait_header_path,
        dataset_id=dataset_id,
        table_id=table_id,
        dump_type=dump_type,
        wait=wait_header_path,
    )

    #####################################
    #
    # Tasks section #2 - Dump batches
    #
    #####################################

    # Upload to GCS
    upload_to_gcs(
        path=wait_batches_path,
        dataset_id=dataset_id,
        table_id=table_id,
        wait=wait_create_db,
    )


dump_sql_flow.storage = GCS(constants.GCS_FLOWS_BUCKET.value)
dump_sql_flow.run_config = KubernetesRun(image=constants.DOCKER_IMAGE.value)
dump_sql_flow.schedule = daily_update_schedule


with Flow("Executar query SQL") as run_sql_flow:

    #####################################
    #
    # Parameters
    #
    #####################################

    # SQL Server parameters
    hostname = Parameter("db_host")
    port = Parameter("db_port")
    database = Parameter("db_database")
    database_type = Parameter("db_type")
    query = Parameter("execute_query")

    # Use Vault for credentials
    secret_path = Parameter("vault_secret_path")

    # CSV file parameters
    batch_size = Parameter("no_of_rows", default="all")

    #####################################
    #
    # Tasks section #0 - Get credentials
    #
    #####################################

    # Get credentials from Vault
    user, password = get_user_and_password(secret_path=secret_path)

    #####################################
    #
    # Tasks section #1 - Execute query
    #
    #####################################

    # Execute query on SQL Server
    db_object: Database = database_get(
        database_type=database_type,
        hostname=hostname,
        port=port,
        user=user,
        password=password,
        database=database,
    )
    wait_db_execute = database_execute(  # pylint: disable=invalid-name
        database=db_object,
        query=query,
    )

    # Log results
    database_fetch(
        database=db_object,
        batch_size=batch_size,
        wait=wait_db_execute,
    )


run_sql_flow.storage = GCS(constants.GCS_FLOWS_BUCKET.value)
run_sql_flow.run_config = KubernetesRun(image=constants.DOCKER_IMAGE.value)