from typing import List
from typing import List, Optional
from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from sqlalchemy.orm import Session

from .database import SessionLocal, engine

users = {
  "alice": "wonderland",
  "bob": "builder",
  "clementine": "mandarine"
}

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



app = FastAPI()

security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    for key, value in users.items():
        if credentials.username==key and credentials.password==value:
            return credentials.username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Basic"},
    )

def get_admin_username(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username=='admin' and credentials.password=='4dm1N':
        return credentials.username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Basic"},
    )


def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.id == player_id).first()


def get_player_by_name(db: Session, name: str):
    return db.query(models.Player).filter(models.Player.name == name).first()


def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Player).offset(skip).limit(limit).all()


def create_player(db: Session, player: schemas.PlayerCreate):
    db_player = models.Player(name=player.name, position=player.position, age=player.age)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


def get_transfers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transfer).offset(skip).limit(limit).all()


def create_player_transfer(db: Session, transfer: schemas.TransferCreate, player_id: int):
    db_transfer = models.Transfer(**transfer.dict(), player_id=player_id)
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    return db_transfer

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/players/", response_model=schemas.Player)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db), username: str = Depends(get_admin_username)):
    db_player = crud.get_player_by_name(db, name=player.name)
    if db_player:
        raise HTTPException(status_code=400, detail="Name already registered")
    return crud.create_player(db=db, player=player)


@app.get("/players/", response_model=List[schemas.Player])
def read_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), username: str = Depends(get_admin_username)):
    players = crud.get_players(db, skip=skip, limit=limit)
    return players


@app.get("/players/{player_id}", response_model=schemas.Player)
def read_player(player_id: int, db: Session = Depends(get_db), username: str = Depends(get_admin_username)):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player


@app.post("/players/{player_id}/transfers/", response_model=schemas.Transfer)
def create_transfer_for_player(player_id: int, transfer: schemas.TransferCreate, db: Session = Depends(get_db), username: str = Depends(get_admin_username)):
    return crud.create_player_transfer(db=db, transfer=transfer, player_id=player_id)


@app.get("/transfers/", response_model=List[schemas.Transfer])
def read_transfers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), username: str = Depends(get_admin_username)):
    transfers = crud.get_transfers(db, skip=skip, limit=limit)
    return transfers