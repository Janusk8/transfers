from typing import List
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.orm import Session

Base = declarative_base()

#Create the database
engine = create_engine('sqlite:///transfers.db', echo=True)
Base.metadata.create_all(engine)

#Create the session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

users = {
  "alice": "wonderland",
  "bob": "builder",
  "clementine": "mandarine"
}

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    position = Column(String)
    age = Column(Integer)

    items = relationship("Transfer", back_populates="owner")


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    market_value = Column(Integer)
    transfer_fee = Column(Integer)

    owner = relationship("Player", back_populates="transfers")

class Transfer(BaseModel):
    id: int
    player_id: int
    team_from_id: int
    league_from_id: int
    team_to_id: int
    league_to_id: int
    season: str
    market_value: int
    transfer_fee: int


class Player(BaseModel):
    id: int
    name: str
    age: int
    position: str
    transfers: List[Transfer] = []



api = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    for key, value in users.items():
        if credentials.username==key and credentials.password==value:
            return credentials.username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )

def get_admin_username(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username=='admin' and credentials.password=='4dm1N':
        return credentials.username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


def get_player(db: Session, player_id: int):
    return db.query(Player).filter(models.Player.id == player_id).first()


def get_player_by_name(db: Session, name: str):
    return db.query(Player).filter(models.Player.name == name).first()


def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Player).offset(skip).limit(limit).all()


def get_transfers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transfer).offset(skip).limit(limit).all()


@api.get("/players/")
def read_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    players = get_players(db, skip=skip, limit=limit)
    return players


@api.get("/players/{player_id}")
def read_player(player_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    db_player = get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player


@api.get("/transfers/")
def read_transfers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    transfers = get_transfers(db, skip=skip, limit=limit)
    return transfers