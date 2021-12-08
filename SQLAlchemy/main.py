from typing import List
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, text, inspect
from sqlalchemy import Column, Integer, String, ForeignKey
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

users = {
  "alice": "wonderland",
  "bob": "builder",
  "clementine": "mandarine"
}

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    position = Column(String)
    age = Column(Integer)

class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    
class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    team_from_id = Column(Integer, ForeignKey("teams.id"))
    league_from_id = Column(Integer, ForeignKey("leagues.id"))
    team_to_id = Column(Integer, ForeignKey("teams.id"))
    league_to_id = Column(Integer, ForeignKey("leagues.id"))
    season = Column(String)
    market_value = Column(Integer)
    transfer_fee = Column(Integer)
    player_id = Column(Integer, ForeignKey("players.id"))

#Create the database
engine = create_engine('sqlite:///transfers.db', echo=True)
conn = engine.connect()

# Test
# stmt = text ( "SELECT * from transfers inner join players on players.id=transfers.player_id limit 5;" )
# result = conn.execute(stmt)
# print(result.fetchall())

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    return db.query(Player).filter(Player.id == player_id).first()

def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Player).offset(skip).limit(limit).all()

def get_teams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Team).offset(skip).limit(limit).all()

def get_leagues(db: Session, skip: int = 0, limit: int = 100):
    return db.query(League).offset(skip).limit(limit).all()

def get_transfers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transfer).offset(skip).limit(limit).all()

def get_transfers_for_player(db: Session, player_id: int):
    return db.query(Transfer).filter(Transfer.player_id == player_id).all()


@api.get("/teams/")
def read_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    teams = get_teams(db, skip=skip, limit=limit)
    return teams

@api.get("/leagues/")
def read_leagues(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    leagues = get_leagues(db, skip=skip, limit=limit)
    return leagues

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

@api.get("/players/{player_id}/transfers/")
def read_transfers_for_player(player_id: int, db: Session = Depends(get_db), username: str = Depends(get_current_username)):
    transfers  = get_transfers_for_player(db, player_id=player_id)
    if transfers  is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfers 
