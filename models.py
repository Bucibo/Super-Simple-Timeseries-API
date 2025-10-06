from pydantic import BaseModel
from datetime import datetime

class TimeseriesData(BaseModel):
    metric_name: str
    ts: datetime
    value: str

class MetaData(BaseModel):
    metric_name: str
    first_seen: datetime
    first_seen_value: str
