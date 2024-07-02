from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select

Base = declarative_base()


class FastaData(Base):
    __tablename__ = "fasta_data"
    tag = Column(String, primary_key=True)
    seq = Column(String, nullable=False)


DATABASE_URL = "sqlite+aiosqlite:///./NCBI.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


def parse_fasta(fasta_data):
    from itertools import groupby

    lines = fasta_data.strip().split("\n")
    grouped = groupby(lines, lambda x: x.startswith(">"))

    sequences = []
    tag = ""
    for is_header, group in grouped:
        if is_header:
            tag = next(group).strip()
        else:
            seq = "".join(line.strip() for line in group)
            sequences.append((tag, seq))

    return sequences


def FASTA_loader(fasta_file: str) -> list[tuple[str, str]]:
    with open(fasta_file, "r") as f:
        data = f.read()
    sequences = parse_fasta(data)
    return sequences


async def get_fasta_data(tag: str) -> FastaData:
    async with async_session() as session:
        async with session.begin():
            query = select(FastaData).filter(FastaData.tag == tag)
            result = await session.execute(query)
            fasta_data = result.scalars().first()
            return fasta_data


async def add_fasta_data(tag: str, seq: str) -> FastaData:
    async with async_session() as session:
        async with session.begin():
            fasta_data = FastaData(tag=tag, seq=seq)
            session.add(fasta_data)
            await session.commit()
            return fasta_data


async def get_all_fasta_data() -> list[FastaData]:
    async with async_session() as session:
        async with session.begin():
            query = select(FastaData)
            result = await session.execute(query)
            fasta_data = result.scalars().all()
            return fasta_data


async def get_fasta_data_by_seq(seq: str) -> FastaData:
    async with async_session() as session:
        async with session.begin():
            query = select(FastaData).filter(FastaData.seq == seq)
            result = await session.execute(query)
            fasta_data = result.scalars().first()
            return fasta_data


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def load_fasta_to_sqlite(fasta_file: str):
    await init_db()
    sequences = FASTA_loader(fasta_file)
    for tag, seq in sequences:
        await add_fasta_data(tag, seq)

    tag_to_search = sequences[0][0]
    fasta_data = await get_fasta_data(tag_to_search)
    print(f"Retrieved: Tag: {fasta_data.tag}, Sequence: {fasta_data.seq}")
