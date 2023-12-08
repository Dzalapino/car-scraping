from dataclasses import dataclass


@dataclass
class Car:
    link: str
    full_name: str
    url_brand: str
    mileage: int
    fuel_type: str
    gearbox: str
    year: int
    status: str
    price_pln: int
