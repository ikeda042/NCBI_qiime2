from models import Sequence
import aiofiles
import asyncio
from concurrent.futures import ThreadPoolExecutor
import qiime2
import pandas as pd
from qiime2 import Artifact
from database import load_fasta_to_sqlite, get_all_fasta_data


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


if __name__ == "__main__":
    # sequences = asyncio.run(load_qza("rep-seqs.qza"))
    seq = [i.seq for i in asyncio.run(get_all_fasta_data())]
