from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from models import Sequence
from main import load_qza
import uvicorn
import os
import tempfile

app = FastAPI(
    docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"status": "running"}


@app.post("/qza/")
async def get_qza(file: UploadFile = File(...)) -> list[Sequence]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".qza") as tmp_file:
        contents = await file.read()
        tmp_file.write(contents)
        tmp_file_path = tmp_file.name
    result = await load_qza(tmp_file_path)
    os.unlink(tmp_file_path)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
