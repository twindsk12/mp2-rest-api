import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, setup_logging

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    filename = file.filename or ""

    if Path(filename).suffix.lower() != ".csv":
        logger.warning("Unsupported file format: %s", filename)
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )

    contents = await file.read()

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            UnicodeDecodeError
    ) as error:
        logger.warning("Cannot read CSV: %s", error)
        raise HTTPException(
            status_code=400,
            detail="Cannot read the uploaded CSV."
        ) from error

    dataset_id = storage.save(df, filename)
    metadata = storage.get_metadata(dataset_id)

    logger.info(
        "Uploaded dataset: id=%s, filename=%s, rows=%s",
        dataset_id,
        filename,
        len(df)
    )

    return metadata


@app.get("/datasets/{dataset_id}")
def get_dataset( dataset_id: int, limit: int = Query(default=100, ge=1),
):
    """Return up to limit rows from a stored dataset."""
    df = storage.get(dataset_id)

    if df is None:
        logger.warning("Dataset not found: %s", dataset_id)
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    records = json.loads(df.head(limit).to_json(orient="records"))

    logger.info(
        "Retrieved dataset: id=%s, returned_rows=%s",
        dataset_id,
        len(records)
    )

    return {
        "id": dataset_id,
        "data": records,
        "total_rows": len(df)
    }