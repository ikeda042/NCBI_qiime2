from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import Sequence
from main import load_qza


app = FastAPI()

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
