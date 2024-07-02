import qiime2
from qiime2 import Artifact
import pandas as pd

aft = Artifact.load("rep-seqs.qza")
table_df = aft.view(pd.DataFrame)

print(table_df)
