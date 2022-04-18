# -*- coding: utf-8 -*-
"""
General utilities for interacting with datario-dump
"""

from datetime import timedelta, datetime
from typing import List

from prefect.schedules.clocks import IntervalClock


def generate_dump_datario_schedules(  # pylint: disable=too-many-arguments,too-many-locals
    interval: timedelta,
    start_date: datetime,
    labels: List[str],
    table_parameters: dict,
    runs_interval_minutes: int = 15,
) -> List[IntervalClock]:
    """
    Generates multiple schedules for dumping datario tables.
    """
    clocks = []
    for count, (table_id, parameters) in enumerate(table_parameters.items()):
        parameter_defaults = {
            "url": parameters["url"],
            "dataset_id": parameters["dataset_id"],
            "dump_type": parameters["dump_type"],
            "table_id": table_id,
        }
        clocks.append(
            IntervalClock(
                interval=interval,
                start_date=start_date
                + timedelta(minutes=runs_interval_minutes * count),
                labels=labels,
                parameter_defaults=parameter_defaults,
            )
        )
    return clocks