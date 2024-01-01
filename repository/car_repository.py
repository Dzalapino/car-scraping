from sqlalchemy.exc import IntegrityError
import car_scraping.car as scrap
from repository.models import Car
from repository.db_connection import Session


def add_car_if_not_exists(new_car: scrap.Car):
    session = Session()
    try:
        new_car = Car(
            link=new_car.link,
            full_name=new_car.full_name,
            url_brand=new_car.url_brand,
            mileage=new_car.mileage,
            fuel_type=new_car.fuel_type,
            gearbox=new_car.gearbox,
            year=new_car.year,
            status=new_car.status,
            price_pln=new_car.price_pln
        )
        session.add(new_car)
        session.commit()
    except IntegrityError:
        session.rollback()  # Rollback the transaction in case of IntegrityError (duplicate entry)
        print(f'Duplicate entry: {new_car} already exists in the database.')
    except Exception as e:
        # Rollback changes if error occurs
        print(f'An error occurred while adding Car to database:\n    {e}')
        session.rollback()
    finally:
        session.close()


def get_all_cars_by_brand_and_model(brand, model):
    session = Session()
    try:
        return session.query(Car).filter(Car.url_brand == brand, Car.full_name.like(f'%{model}%')).all()
    except Exception as e:
        print(f'An error occurred while getting all cars by brand and model:\n    {e}')
    finally:
        session.close()
