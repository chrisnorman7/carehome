"""Provides the PropertyTypes class."""

from datetime import datetime, timedelta

NoneType = type(None)


property_types = dict(
    null=NoneType,
    bool=bool,
    str=str,
    float=float,
    int=int,
    list=list,
    dict=dict,
    datetime=datetime,
    duration=timedelta
)
