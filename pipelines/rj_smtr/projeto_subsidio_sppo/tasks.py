# -*- coding: utf-8 -*-
"""
Tasks for projeto_subsidio_sppo
"""

from typing import List
import datetime
import pandas as pd
from prefect import task

from pipelines.utils.tasks import log


@task
def get_run_dates(date_range_start: str, date_range_end: str) -> List:
    """
    Generates a list of dates between date_range_start and date_range_end.
    """
    if (date_range_start is False) or (date_range_end is False):
        dates = [{"run_date": datetime.date.today().strftime("%Y-%m-%d")}]
    else:
        dates = [
            {"run_date": d.strftime("%Y-%m-%d")}
            for d in pd.date_range(start=date_range_start, end=date_range_end)
        ]
    log(f"Will run the following dates: {dates}")
    return dates
