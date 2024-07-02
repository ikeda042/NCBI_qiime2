import qiime2
from qiime2 import Artifact
import pandas as pd

aft = Artifact.load("rep-seqs.qza")

sequences = aft.view(qiime2.Metadata)

sequences_df = sequences.to_dataframe()

print(sequences_df)

sequences_df.to_csv("sequences.csv", index=False)
