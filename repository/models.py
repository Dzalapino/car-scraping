from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String, unique=True)
    brand = Column(String)
    model = Column(String)
    mileage = Column(Integer)
    engine_capacity = Column(Integer)
    engine_power = Column(Integer)
    year = Column(Integer)
    fuel_type = Column(String)
    gearbox = Column(String)
    body_type = Column(String)
    colour = Column(String)
    type_of_color = Column(String)
    accident_free = Column(String)
    state = Column(String)
    price_pln = Column(Integer)
