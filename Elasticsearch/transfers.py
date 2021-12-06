from fastapi import FastAPI, Depends, Header, HTTPException, status, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import numpy as np
import json
from random import choices
from sklearn import metrics
from sklearn.model_selection import train_test_split
import joblib
from joblib import dump, load

users = {
  "alice": "wonderland",
  "bob": "builder",
  "clementine": "mandarine"
}

class Transfer(BaseModel):
    name: str
    position: str
    age: int
    team_from: str
    league_from: str
    team_to: str
    league_to: str
    season: str
    market_value: int
    transfer_fee: int

api = FastAPI(
    title="Football transfers API",
    description="API de données sur les 250 premiers transfers de football entre 2000 et 2018",
    version="1.0.1",
    openapi_tags=[
    {
        'name': 'Home',
        'description': 'Default functions'
    },
    {
        'name': 'Transfers',
        'description': 'Functions that are used to deal with transfers'
    }
    ]
)

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

    
@api.get('/status', name='Get API status', tags=['Home'])
def get_status(username: str = Depends(get_current_username)):
    """Cette fonction renvoie 1 si l'API fonctionne.
    """
    return 1

@api.get('/transfers', name='Get transfers', tags=['Transfers'])
async def get_transfers(username: str = Depends(get_current_username)):
    """
    Cette fonction recherche les transfers en fonction de paramètres donnés
    """

    try:

        transfers = []
        """ TO DO
        """

        return transfers 

    except IndexError:
        raise HTTPException(
            status_code=404,
            detail='Unknown Index')
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail='Bad Type'
        )
        
@api.post('/transfer', name='Post new transfer', tags=['Transfers'])
def post_transfer(transfer: Transfer, username: str = Depends(get_admin_username)):
    """Cette fonction permet a un utilisateur admin de créer un nouveau transfer
    """

    try:
        new_transfer = {
            'name': transfer.name,
            'position': transfer.position,
            'age': transfer.age,
            'team_from': transfer.team_from,
            'league_from': transfer.league_from,
            'team_to': transfer.team_to,
            'league_to': transfer.league_to,
            'season': transfer.season,
            'market_value': transfer.market_value,
            'transfer_fee': transfer.transfer_fee
        }
        """ TO DO
        """
        return new_transfer

    except IndexError:
        return {}
