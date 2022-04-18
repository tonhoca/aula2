"""
Schedules for emd
"""

from datetime import timedelta, datetime
from prefect.schedules import Schedule
from prefect.schedules.clocks import IntervalClock
from pipelines.constants import constants

every_five_minutes = Schedule(
    clocks=[
        IntervalClock(
            interval=timedelta(minutes=5),
            start_date=datetime(2021, 1, 1),
            labels=[
                constants.EMD_AGENT_LABEL.value,
            ],
        ),
    ]
)