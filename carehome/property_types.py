"""Provides the PropertyTypes class."""

from datetime import datetime, timedelta
from enum import Enum
from .objects import Object

NoneType = type(None)


class PropertyTypes(Enum):
    """The available property types."""

    null = NoneType
    bool = bool
    str = str
    float = float
    int = int
    list = list
    dict = dict
    datetime = datetime
    duration = timedelta
    obj = Object
