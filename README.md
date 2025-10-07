# Super Simple Timeseries API


This project provides a simple and scalable **Timeseries Data API** built with **FastAPI** and **Supabase**.  

It supports:

- Ingesting metric data points,

- Querying time-bound records,

- Running aggregate queries, and

- Managing metadata for all tracked metrics.

---

## Features


- **FastAPI Backend** — Modern Python web framework optimized for speed and clarity.

- **Supabase Integration** — PostgreSQL-based cloud backend with REST and RPC access.

- **Timeseries Storage** — Store metric data with timestamps and values.

- **Aggregation Support** — Query aggregated metrics via PostgreSQL RPC.

- **Metadata Management** — Automatically track first-seen timestamps and values.

---

## Project Structure


service/

│

├── app.py # Main FastAPI entry point

├── models.py # Pydantic models for data validation

├── routes/

│ └── timeseries.py # Timeseries routes and Supabase logic

│

├── .env # Environment variables (not committed)

├── .gitignore # Ignored files and directories

├── requirements.txt # Python dependencies

└── README.md # Project documentation


## Prerequisites


Before setting up, make sure you have installed:


- **Python 3.10+**

- **pip** (Python package manager)

- **Virtual environment** (optional but recommended)

## Installation

1. **Clone the repository**

```bash

   git clone https://github.com/Bucibo/Super-Simple-Timeseries-API.git

   cd Super-Simple-Timeseries-API
```

2. **Create and activate a virtual environment**
```bash
  python -m venv venv
```

## On Windows ##

```bash
  venv\Scripts\activate
```

## On Mac/Linux

```bash
  source venv/bin/activate
```

3. **Install dependencies**

```bash
  pip install -r requirements.txt
``` 

4. **Create a .env file in the project root with the following variables:**

For the purpose of this Assessment, the SUPABASE_URL AND SUPABASE API keys are provided in the report sent via email(page 2)

```bash

SUPABASE_URL=https://your-project-ref.supabase.co 

SUPABASE_API=your-supabase-anon-key
```
## Running the service with uvicorn: ##

```bash
uvicorn app:app --reload
```

## Testing the API with Swagger UI

FastAPI automatically generates Swagger UI for interactive testing.

1. **Open your browser and navigate to:**

```bash
http://127.0.0.1:8000/docs
```

- You will see all the available endpoints grouped by tags (e.g., Timeseries).

2. **Test endpoints by:**

- Clicking on an endpoint (e.g., POST /timeseries/ingest_data)

- Expanding the input form

- Filling in example JSON payloads

- Clicking “Execute”

- Viewing the response directly in the browser
