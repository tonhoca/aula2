"""
Tasks for emd
"""


from datetime import datetime, timedelta

import basedosdados as bd
from google.cloud import bigquery
import pandas as pd
from prefect import task
import requests
from shapely.wkt import loads

from pipelines.constants import constants


@task(
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=timedelta(seconds=constants.TASK_RETRY_DELAY.value),
)
def load_geometries() -> pd.DataFrame:
    """
    Loads the geometries from the database.
    """
    areas_dict = {
        "geometry": {
            0: "POLYGON ((-43.62216601277018 -23.08289269734031, -43.79653853090349 -23.08289269734031, -43.79653853090349 -22.91445704293636, -43.62216601277018 -22.91445704293636, -43.62216601277018 -23.08289269734031))",
            1: "POLYGON ((-43.62216601277018 -22.74602138853241, -43.62216601277018 -22.91445704293636, -43.79653853090349 -22.91445704293636, -43.79653853090349 -22.74602138853241, -43.62216601277018 -22.74602138853241))",
            2: "POLYGON ((-43.44779349463688 -23.08289269734031, -43.62216601277018 -23.08289269734031, -43.62216601277018 -22.91445704293636, -43.44779349463688 -22.91445704293636, -43.44779349463688 -23.08289269734031))",
            3: "POLYGON ((-43.44779349463688 -22.91445704293636, -43.62216601277018 -22.91445704293636, -43.62216601277018 -22.74602138853241, -43.44779349463688 -22.74602138853241, -43.44779349463688 -22.91445704293636))",
            4: "POLYGON ((-43.44779349463688 -23.08289269734031, -43.44779349463688 -22.91445704293636, -43.36060723557023 -22.91445704293636, -43.36060723557023 -23.08289269734031, -43.44779349463688 -23.08289269734031))",
            5: "POLYGON ((-43.36060723557023 -23.08289269734031, -43.36060723557023 -22.91445704293636, -43.27342097650357 -22.91445704293636, -43.27342097650357 -23.08289269734031, -43.36060723557023 -23.08289269734031))",
            6: "POLYGON ((-43.44779349463688 -22.83023921573439, -43.36060723557023 -22.83023921573439, -43.36060723557023 -22.91445704293636, -43.44779349463688 -22.91445704293636, -43.44779349463688 -22.83023921573439))",
            7: "POLYGON ((-43.44779349463688 -22.74602138853241, -43.36060723557023 -22.74602138853241, -43.36060723557023 -22.83023921573439, -43.44779349463688 -22.83023921573439, -43.44779349463688 -22.74602138853241))",
            8: "POLYGON ((-43.36060723557023 -22.91445704293636, -43.36060723557023 -22.83023921573439, -43.27342097650357 -22.83023921573439, -43.27342097650357 -22.91445704293636, -43.36060723557023 -22.91445704293636))",
            9: "POLYGON ((-43.3170141060369 -22.74602138853241, -43.3170141060369 -22.83023921573439, -43.36060723557023 -22.83023921573439, -43.36060723557023 -22.74602138853241, -43.3170141060369 -22.74602138853241))",
            10: "POLYGON ((-43.27342097650357 -22.74602138853241, -43.27342097650357 -22.83023921573439, -43.3170141060369 -22.83023921573439, -43.3170141060369 -22.74602138853241, -43.27342097650357 -22.74602138853241))",
            11: "POLYGON ((-43.27342097650357 -22.99867487013834, -43.18623471743692 -22.99867487013834, -43.18623471743692 -23.08289269734031, -43.27342097650357 -23.08289269734031, -43.27342097650357 -22.99867487013834))",
            12: "POLYGON ((-43.22982784697025 -22.91445704293636, -43.22982784697025 -22.99867487013834, -43.27342097650357 -22.99867487013834, -43.27342097650357 -22.91445704293636, -43.22982784697025 -22.91445704293636))",
            13: "POLYGON ((-43.18623471743692 -22.91445704293636, -43.18623471743692 -22.99867487013834, -43.22982784697025 -22.99867487013834, -43.22982784697025 -22.91445704293636, -43.18623471743692 -22.91445704293636))",
            14: "POLYGON ((-43.18623471743692 -23.08289269734031, -43.18623471743692 -22.91445704293636, -43.09904845837026 -22.91445704293636, -43.09904845837026 -23.08289269734031, -43.18623471743692 -23.08289269734031))",
            15: "POLYGON ((-43.22982784697025 -22.83023921573439, -43.22982784697025 -22.91445704293636, -43.27342097650357 -22.91445704293636, -43.27342097650357 -22.83023921573439, -43.22982784697025 -22.83023921573439))",
            16: "POLYGON ((-43.18623471743692 -22.83023921573439, -43.18623471743692 -22.91445704293636, -43.22982784697025 -22.91445704293636, -43.22982784697025 -22.83023921573439, -43.18623471743692 -22.83023921573439))",
            17: "POLYGON ((-43.27342097650357 -22.74602138853241, -43.18623471743692 -22.74602138853241, -43.18623471743692 -22.83023921573439, -43.27342097650357 -22.83023921573439, -43.27342097650357 -22.74602138853241))",
            18: "POLYGON ((-43.18623471743692 -22.91445704293636, -43.18623471743692 -22.74602138853241, -43.09904845837026 -22.74602138853241, -43.09904845837026 -22.91445704293636, -43.18623471743692 -22.91445704293636))",
        },
        "bounds": {
            0: "POLYGON ((-43.79653853090349 -23.08289269734031, -43.62216601277018 -23.08289269734031, -43.62216601277018 -22.91445704293636, -43.79653853090349 -22.91445704293636, -43.79653853090349 -23.08289269734031))",
            1: "POLYGON ((-43.79653853090349 -22.91445704293636, -43.62216601277018 -22.91445704293636, -43.62216601277018 -22.74602138853241, -43.79653853090349 -22.74602138853241, -43.79653853090349 -22.91445704293636))",
            2: "POLYGON ((-43.62216601277018 -23.08289269734031, -43.44779349463688 -23.08289269734031, -43.44779349463688 -22.91445704293636, -43.62216601277018 -22.91445704293636, -43.62216601277018 -23.08289269734031))",
            3: "POLYGON ((-43.62216601277018 -22.91445704293636, -43.44779349463688 -22.91445704293636, -43.44779349463688 -22.74602138853241, -43.62216601277018 -22.74602138853241, -43.62216601277018 -22.91445704293636))",
            4: "POLYGON ((-43.44779349463688 -23.08289269734031, -43.36060723557023 -23.08289269734031, -43.36060723557023 -22.91445704293636, -43.44779349463688 -22.91445704293636, -43.44779349463688 -23.08289269734031))",
            5: "POLYGON ((-43.36060723557023 -23.08289269734031, -43.27342097650357 -23.08289269734031, -43.27342097650357 -22.91445704293636, -43.36060723557023 -22.91445704293636, -43.36060723557023 -23.08289269734031))",
            6: "POLYGON ((-43.44779349463688 -22.91445704293636, -43.36060723557023 -22.91445704293636, -43.36060723557023 -22.83023921573439, -43.44779349463688 -22.83023921573439, -43.44779349463688 -22.91445704293636))",
            7: "POLYGON ((-43.44779349463688 -22.83023921573439, -43.36060723557023 -22.83023921573439, -43.36060723557023 -22.74602138853241, -43.44779349463688 -22.74602138853241, -43.44779349463688 -22.83023921573439))",
            8: "POLYGON ((-43.36060723557023 -22.91445704293636, -43.27342097650357 -22.91445704293636, -43.27342097650357 -22.83023921573439, -43.36060723557023 -22.83023921573439, -43.36060723557023 -22.91445704293636))",
            9: "POLYGON ((-43.36060723557023 -22.83023921573439, -43.3170141060369 -22.83023921573439, -43.3170141060369 -22.74602138853241, -43.36060723557023 -22.74602138853241, -43.36060723557023 -22.83023921573439))",
            10: "POLYGON ((-43.3170141060369 -22.83023921573439, -43.27342097650357 -22.83023921573439, -43.27342097650357 -22.74602138853241, -43.3170141060369 -22.74602138853241, -43.3170141060369 -22.83023921573439))",
            11: "POLYGON ((-43.27342097650357 -23.08289269734031, -43.18623471743692 -23.08289269734031, -43.18623471743692 -22.99867487013834, -43.27342097650357 -22.99867487013834, -43.27342097650357 -23.08289269734031))",
            12: "POLYGON ((-43.27342097650357 -22.99867487013834, -43.22982784697025 -22.99867487013834, -43.22982784697025 -22.91445704293636, -43.27342097650357 -22.91445704293636, -43.27342097650357 -22.99867487013834))",
            13: "POLYGON ((-43.22982784697025 -22.99867487013834, -43.18623471743692 -22.99867487013834, -43.18623471743692 -22.91445704293636, -43.22982784697025 -22.91445704293636, -43.22982784697025 -22.99867487013834))",
            14: "POLYGON ((-43.18623471743692 -23.08289269734031, -43.09904845837026 -23.08289269734031, -43.09904845837026 -22.91445704293636, -43.18623471743692 -22.91445704293636, -43.18623471743692 -23.08289269734031))",
            15: "POLYGON ((-43.27342097650357 -22.91445704293636, -43.22982784697025 -22.91445704293636, -43.22982784697025 -22.83023921573439, -43.27342097650357 -22.83023921573439, -43.27342097650357 -22.91445704293636))",
            16: "POLYGON ((-43.22982784697025 -22.91445704293636, -43.18623471743692 -22.91445704293636, -43.18623471743692 -22.83023921573439, -43.22982784697025 -22.83023921573439, -43.22982784697025 -22.91445704293636))",
            17: "POLYGON ((-43.27342097650357 -22.83023921573439, -43.18623471743692 -22.83023921573439, -43.18623471743692 -22.74602138853241, -43.27342097650357 -22.74602138853241, -43.27342097650357 -22.83023921573439))",
            18: "POLYGON ((-43.18623471743692 -22.91445704293636, -43.09904845837026 -22.91445704293636, -43.09904845837026 -22.74602138853241, -43.18623471743692 -22.74602138853241, -43.18623471743692 -22.91445704293636))",
        },
        "ts": {
            0: "2022-02-08T11:21:53.205525",
            1: "2022-02-08T11:21:53.205525",
            2: "2022-02-08T11:21:53.205525",
            3: "2022-02-08T11:21:53.205525",
            4: "2022-02-08T11:21:53.205525",
            5: "2022-02-08T11:21:53.205525",
            6: "2022-02-08T11:21:53.205525",
            7: "2022-02-08T11:21:53.205525",
            8: "2022-02-08T11:21:53.205525",
            9: "2022-02-08T11:21:53.205525",
            10: "2022-02-08T11:21:53.205525",
            11: "2022-02-08T11:21:53.205525",
            12: "2022-02-08T11:21:53.205525",
            13: "2022-02-08T11:21:53.205525",
            14: "2022-02-08T11:21:53.205525",
            15: "2022-02-08T11:21:53.205525",
            16: "2022-02-08T11:21:53.205525",
            17: "2022-02-08T11:21:53.205525",
            18: "2022-02-08T11:21:53.205525",
        },
        "coords": {
            0: "{'left': -43.79653853090349, 'bottom': -23.08289269734031, 'right': -43.62216601277018, 'top': -22.91445704293636}",
            1: "{'left': -43.79653853090349, 'bottom': -22.91445704293636, 'right': -43.62216601277018, 'top': -22.74602138853241}",
            2: "{'left': -43.62216601277018, 'bottom': -23.08289269734031, 'right': -43.44779349463688, 'top': -22.91445704293636}",
            3: "{'left': -43.62216601277018, 'bottom': -22.91445704293636, 'right': -43.44779349463688, 'top': -22.74602138853241}",
            4: "{'left': -43.44779349463688, 'bottom': -23.08289269734031, 'right': -43.36060723557023, 'top': -22.91445704293636}",
            5: "{'left': -43.36060723557023, 'bottom': -23.08289269734031, 'right': -43.27342097650357, 'top': -22.91445704293636}",
            6: "{'left': -43.44779349463688, 'bottom': -22.91445704293636, 'right': -43.36060723557023, 'top': -22.83023921573439}",
            7: "{'left': -43.44779349463688, 'bottom': -22.83023921573439, 'right': -43.36060723557023, 'top': -22.74602138853241}",
            8: "{'left': -43.36060723557023, 'bottom': -22.91445704293636, 'right': -43.27342097650357, 'top': -22.83023921573439}",
            9: "{'left': -43.36060723557023, 'bottom': -22.83023921573439, 'right': -43.3170141060369, 'top': -22.74602138853241}",
            10: "{'left': -43.3170141060369, 'bottom': -22.83023921573439, 'right': -43.27342097650357, 'top': -22.74602138853241}",
            11: "{'left': -43.27342097650357, 'bottom': -23.08289269734031, 'right': -43.18623471743692, 'top': -22.99867487013834}",
            12: "{'left': -43.27342097650357, 'bottom': -22.99867487013834, 'right': -43.22982784697025, 'top': -22.91445704293636}",
            13: "{'left': -43.22982784697025, 'bottom': -22.99867487013834, 'right': -43.18623471743692, 'top': -22.91445704293636}",
            14: "{'left': -43.18623471743692, 'bottom': -23.08289269734031, 'right': -43.09904845837026, 'top': -22.91445704293636}",
            15: "{'left': -43.27342097650357, 'bottom': -22.91445704293636, 'right': -43.22982784697025, 'top': -22.83023921573439}",
            16: "{'left': -43.22982784697025, 'bottom': -22.91445704293636, 'right': -43.18623471743692, 'top': -22.83023921573439}",
            17: "{'left': -43.27342097650357, 'bottom': -22.83023921573439, 'right': -43.18623471743692, 'top': -22.74602138853241}",
            18: "{'left': -43.18623471743692, 'bottom': -22.91445704293636, 'right': -43.09904845837026, 'top': -22.74602138853241}",
        },
    }

    areas = pd.DataFrame.from_dict(areas_dict)
    areas["bounds"] = areas["bounds"].apply(loads)
    areas["coords"] = areas["bounds"].apply(
        lambda x: dict(zip(["left", "bottom", "right", "top"], x.bounds))
    )

    return areas


@task(
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=timedelta(seconds=constants.TASK_RETRY_DELAY.value),
)
def fecth_waze(areas: pd.DataFrame) -> list:
    """
    Fetch data from waze.
    """
    coords = areas["coords"].to_list()

    base_url = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom={bottom}&left={left}&ma=200&mj=200&mu=20&right={right}&top={top}&types=alerts"
    headers = {}
    payload = {}

    res = []
    for coord in coords:

        url = base_url.format(**coord)

        response = requests.request("GET", url, headers=headers, data=payload)
        res.append(response.json())

    return res


@task(
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=timedelta(seconds=constants.TASK_RETRY_DELAY.value),
)
def normalize_data(responses: list) -> pd.DataFrame:
    """
    Normalize data.
    """
    normalized = []
    for data in responses:
        alerts = data.get("alerts", [])
        for dictionary in alerts:

            normalized.append(
                {
                    "date": datetime.fromisoformat(data["startTime"][:10]),
                    "ts": datetime.fromisoformat(data["startTime"]),
                    "ts_alert_creation": datetime.fromtimestamp(
                        int(str(dictionary.get("pubMillis"))[:10])
                    ),
                    "uuid": dictionary.get("uuid"),
                    "country": dictionary.get("country"),
                    "city": dictionary.get("city"),
                    "street": dictionary.get("street"),
                    "type": dictionary.get("type"),
                    "subtype": dictionary.get("subtype"),
                    # TODO change to road_type
                    "roadType": dictionary.get("roadType"),
                    "reliability": dictionary.get("reliability"),
                    "confidence": dictionary.get("confidence"),
                    "number_thumbs_up": dictionary.get("nThumbsUp"),
                    "number_comments": dictionary.get("nComments"),
                    "report_mood": dictionary.get("reportMood"),
                    "magvar": dictionary.get("magvar"),
                    "report_rating": dictionary.get("reportRating"),
                    "geometry": "POINT ({x} {y})".format(**dictionary.get("location")),  # pylint: disable=consider-using-f-string
                }
            )

    return pd.concat([pd.DataFrame([r]) for r in normalized])


@task(
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=timedelta(seconds=constants.TASK_RETRY_DELAY.value),
)
def upload_to_native_table(
    dataset_id: str, table_id: str, dataframe: pd.DataFrame
) -> None:
    """
    Upload data to native table.
    """
    table = bd.Table(dataset_id=dataset_id, table_id=table_id)

    schema = [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("ts", "TIMESTAMP"),
        bigquery.SchemaField("ts_alert_creation", "TIMESTAMP"),
        bigquery.SchemaField("uuid", "STRING"),
        bigquery.SchemaField("country", "STRING"),
        bigquery.SchemaField("city", "STRING"),
        bigquery.SchemaField("street", "STRING"),
        bigquery.SchemaField("type", "STRING"),
        bigquery.SchemaField("subtype", "STRING"),
        bigquery.SchemaField("roadType", "INT64"),  # TODO change to road_type
        bigquery.SchemaField("reliability", "INT64"),
        bigquery.SchemaField("confidence", "INT64"),
        bigquery.SchemaField("number_thumbs_up", "INT64"),
        bigquery.SchemaField("number_comments", "INT64"),
        bigquery.SchemaField("report_mood", "INT64"),
        bigquery.SchemaField("magvar", "INT64"),
        bigquery.SchemaField("report_rating", "INT64"),
        bigquery.SchemaField("geometry", "GEOGRAPHY"),
    ]

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        # Optionally, set the write disposition. BigQuery appends loaded rows
        # to an existing table by default, but with WRITE_TRUNCATE write
        # disposition it replaces the table with the loaded data.
        write_disposition="WRITE_APPEND",
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="date",  # name of column to use for partitioning
        ),
    )

    job = table.client["bigquery_prod"].load_table_from_dataframe(
        dataframe, table.table_full_name["prod"], job_config=job_config
    )

    job.result()