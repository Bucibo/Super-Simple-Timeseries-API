from fastapi import APIRouter, Query
import asyncio
from supabase import create_client, Client
import os
import requests
from dotenv import load_dotenv
from typing import List, Optional
from models import TimeseriesData, MetaData 

load_dotenv()

router = APIRouter(prefix="/api/timeseries", tags=["Timeseries"])

# --- Supabase Initialization ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API = os.getenv("SUPABASE_API")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API)

requests.adapters.DEFAULT_RETRIES = 1
TIMEOUT = 5  # seconds

async def metric_exists(metric_name: str) -> bool:
    result = await asyncio.to_thread(
        lambda: supabase.table("metadata")
                       .select("metric_name")
                       .eq("metric_name", metric_name)
                       .limit(1)
                       .execute()
    )
    return bool(result.data)

# --- Data Ingestion ---
@router.post("/ingest_data")
async def ingest_data(data: List[TimeseriesData]):
    
    payload = []
    new_metrics = []
    
    existing_metrics_res = await asyncio.to_thread(lambda: supabase.table("metadata").select("metric_name").execute())
    existing_metrics = {m["metric_name"] for m in existing_metrics_res.data or []}

    for item in data:
        item_dict = item.model_dump()

        # Ensure ISO 8601 timestamp
        ts = item_dict.get("ts")
        if not isinstance(ts, str):
            try:
                item_dict["ts"] = ts.isoformat()
            except Exception:
                item_dict["ts"] = str(ts)
        
        # Convert metric_name to lowercase
        metric_name = item_dict.get("metric_name", "").lower()
        item_dict["metric_name"] = metric_name
        
        payload.append(item_dict)

        # Add new metrics to bulk insert
        if metric_name not in existing_metrics:
            new_metrics.append({
                "metric_name": metric_name,
                "first_seen": item_dict["ts"],
                "first_seen_value": item_dict.get("value")
            })
            existing_metrics.add(metric_name) 

    # Insert new metadata in bulk
    if new_metrics:
        await asyncio.to_thread(lambda: supabase.table("metadata").insert(new_metrics).execute())

    # Insert timeseries
    try:
        result = await asyncio.to_thread(lambda: supabase.table("timeseries").insert(payload).execute())
        return {
            "status": "success",
            "inserted_rows": len(result.data or []),
            "data": result.data
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



# --- Filter Query ---
@router.get("/query_data")
async def query_timeseries(
    metric_name: str = Query(..., description="Metric name to filter by"),
    start_date: str = Query(..., description="Start date (ISO format, e.g. 2024-01-01T00:00:00Z)"),
    end_date: str = Query(..., description="End date (ISO format, e.g. 2024-02-01T00:00:00Z)"),
    agg_func: Optional[str] = Query(" ", description="Aggregation function: AVG, SUM, MIN, MAX"),
    interval: Optional[str] = Query(" ", description="Time interval, e.g. 5min, 1h, 1d")
):
    
    if agg_func and agg_func.strip():
        # agg_func is not None and not empty/whitespace (There is use of an aggregation function)
        try:
            response = await asyncio.to_thread(lambda: supabase.rpc("aggregate_timeseries", {
                "p_metric_name": metric_name.lower(),
                "p_start": start_date,
                "p_end": end_date,
                "p_agg_function": agg_func.upper(),
                "p_interval": interval
            }).execute())
        
            return {"status": "success", "data": response.data}
    
        except Exception as e:
            return {"status": "error", "message": str(e)}

    else:
        # agg_func is empty or None
        """
        Query timeseries data by metric_name and date range.
        """
    
        try:
            response = (await asyncio.to_thread(lambda: 
                supabase.table("timeseries")
                .select("*")
                .eq("metric_name", metric_name.lower())
                .gte("ts", start_date)
                .lte("ts", end_date)
                .order("ts", desc=False)
                .execute()
            ))

            if not response.data:
                return {"status": "no_data", "message": "No records found for this query."}

            points = [
                TimeseriesData(
                    metric_name=row.get("metric_name", ""),
                    ts=row.get("ts"),
                    value=row.get("value", "")
                )
                for row in response.data
            ]

            return {"status": "success", "count": len(points), "data": points}

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Network error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}

# --- List Metrics and Metadata ---
@router.get("/list_metrics")
async def get_metadata():
    try:
        response = await asyncio.to_thread(lambda: supabase.table("metadata").select("*").execute())
        Metadata = [
            MetaData(
                metric_name=row.get("metric_name"),
                first_seen=row.get("first_seen"),
                first_seen_value=row.get("first_seen_value")
            )
            for row in response.data
        ]
        return {"data": Metadata}
    except Exception as e:
        return {"error": str(e)}
    

