import qiime2
from qiime2 import Artifact
import aiofiles
import asyncio
from pydantic import BaseModel

aft = Artifact.load("rep-seqs.qza")

sequences = aft.view(qiime2.Metadata)

sequences_df = sequences.to_dataframe()

ret = {i: sequences_df.loc[i, "Sequence"] for i in sequences_df.index}


print(ret)
