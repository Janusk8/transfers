from numpy import genfromtxt
from sqlalchemy import Column, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def Load_Data(file_name):
    data = genfromtxt(file_name, delimiter=';', skip_header=1, converters={0: lambda s: str(s)})
    return data.tolist()

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    position = Column(String)
    age = Column(Integer)

    transfer = relationship("Transfer", back_populates="player")


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
    team_from_id = Column(Integer)
    league_from_id = Column(Integer)
    team_to_id = Column(Integer)
    league_to_id = Column(Integer)
    season = Column(String)
    market_value = Column(Integer)
    transfer_fee = Column(Integer)
    player_id = Column(Integer, ForeignKey("players.id"))

    player = relationship("Player", back_populates="transfers")


if __name__ == "__main__":
    t = time()

    #Create the database
    engine = create_engine('sqlite:///transfers.db')
    Base.metadata.create_all(engine)

    #Create the session
    session = sessionmaker()
    session.configure(bind=engine)
    s = session()

    try:
        file_name = "/files/league.csv"
        data = Load_Data(file_name) 

        for i in data:
            record = League(**{
                'id' : i[0],
                'name' : i[1]
            })
            s.add(record) #Add all the records
            
        file_name = "/files/team.csv"
        data = Load_Data(file_name) 

        for i in data:
            record = Team(**{
                'id' : i[0],
                'name' : i[1]
            })
            s.add(record) #Add all the records
            
        file_name = "/files/player.csv"
        data = Load_Data(file_name) 

        for i in data:
            record = Player(**{
                'id' : i[0],
                'name' : i[1],
                'position' : i[2],
                'age' : i[3]
            })
            s.add(record) #Add all the records

        file_name = "/files/transfer.csv"
        data = Load_Data(file_name) 

        for i in data:
            record = Transfer(**{
                'id' : i[0],
                'player_id' : i[1],
                'team_from_id' : i[2],
                'league_from_id' : i[3],
                'team_to_id' : i[4],
                'league_to_id' : i[5],
                'season' : i[6],
                'market_value' : i[7],
                'transfer_fee' : i[8]
            })
            s.add(record) #Add all the records

        s.commit() #Attempt to commit all the records
    except:
        s.rollback() #Rollback the changes on error
    finally:
        s.close() #Close the connection
    print "Time elapsed: " + str(time() - t) + " s." 