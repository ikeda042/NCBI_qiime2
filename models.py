from pydantic import BaseModel


class Sequence(BaseModel):
    id: str
    sequence: str
