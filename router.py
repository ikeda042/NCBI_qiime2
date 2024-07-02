from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from models import Sequence
import uvicorn
import aiofiles
import asyncio
from concurrent.futures import ThreadPoolExecutor
import qiime2
import pandas as pd
from qiime2 import Artifact
from database import load_fasta_to_sqlite

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

executor = ThreadPoolExecutor()


def load_qza_sync(file_path: str) -> list[Sequence]:
    aft: Artifact = Artifact.load(file_path)
    sequences: qiime2.Metadata = aft.view(qiime2.Metadata)
    sequences_df: pd.DataFrame = sequences.to_dataframe()
    ret: dict[str, str] = {
        i: sequences_df.loc[i, "Sequence"] for i in sequences_df.index
    }
    fasta_content = "\n".join(f">{i}\n{ret[i]}" for i in ret)
    return ret, fasta_content


async def load_qza(file_path: str) -> list[Sequence]:
    loop = asyncio.get_event_loop()
    ret, fasta_content = await loop.run_in_executor(executor, load_qza_sync, file_path)

    async with aiofiles.open(f"{file_path.split('.')[0]}.fasta", "w") as f:
        await f.write(fasta_content)

    return [Sequence(id=i, sequence=ret[i]) for i in ret]


@app.on_event("startup")
async def startup_event():
    # await load_fasta_to_sqlite("./NCBI_database.fasta")
    pass


@app.get("/")
async def read_root():
    return {"status": "running"}


@app.post("/qza/")
async def get_qza(file: UploadFile = File(...)) -> list[Sequence]:
    async with aiofiles.tempfile.NamedTemporaryFile(
        delete=False, suffix=".qza"
    ) as tmp_file:
        contents = await file.read()
        await tmp_file.write(contents)
        tmp_file_path = tmp_file.name
    return await load_qza(tmp_file_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
