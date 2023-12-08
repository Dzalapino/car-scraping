from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String, unique=True)
    full_name = Column(String)
    url_brand = Column(String)
    mileage = Column(Integer)
    fuel_type = Column(String)
    gearbox = Column(String)
    year = Column(Integer)
    status = Column(String)
    price_pln = Column(Integer)

    # Define unique constraints
    __table_args__ = (
        (UniqueConstraint('full_name', 'mileage', 'fuel_type', 'gearbox', 'year', 'status', 'price_pln'),)
    )


class TotalCars(Base):
    __tablename__ = 'total_cars'

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand = Column(String, unique=True)
    total_used = Column(Integer)
    total_new = Column(Integer)
