import qiime2
from qiime2 import Artifact
import aiofiles
import asyncio
from models import Sequence


async def load_qza(file_path: str) -> list[Sequence]:
    aft: Artifact = Artifact.load(file_path)
    sequences = aft.view(qiime2.Metadata)
    sequences_df = sequences.to_dataframe()
    ret = {i: sequences_df.loc[i, "Sequence"] for i in sequences_df.index}
    async with aiofiles.open(f"{file_path.split('.')[0]}.fasta", "w") as f:
        for i in ret:
            await f.write(f">{i}\n{ret[i]}\n")
    return [Sequence(id=i, sequence=ret[i]) for i in ret]


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(load_qza("rep-seqs.qza"))
    print(res)
