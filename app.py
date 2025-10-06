from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

from routes import timeseries
from routes.timeseries import router as timeseries_router


app = FastAPI(title="Super Simple Timeseries API")

# Include router
app.include_router(timeseries_router)
