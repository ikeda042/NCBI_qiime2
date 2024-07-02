from pydantic import BaseModel


class Sequence(BaseModel):
    id: str
    sequence: str


class FastaData(BaseModel):
    tag: str
    seq: str
