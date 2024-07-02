from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import Sequence
from main import load_qza
import uvicorn

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


@app.get("/qza/{file_path}", response_model=list[Sequence])
async def get_qza(file_path: str) -> list[Sequence]:
    return await load_qza(file_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
