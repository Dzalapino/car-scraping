from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
import car_scraping.car as scrap
from repository.models import Car
from repository.db_connection import Session


def add_car_if_not_exists(new_car: scrap.Car):
    session = Session()
    try:
        new_car = Car(
            link=new_car.link,
            brand=new_car.brand,
            model=new_car.model,
            mileage=new_car.mileage,
            engine_capacity=new_car.engine_capacity,
            engine_power=new_car.engine_power,
            year=new_car.year,
            fuel_type=new_car.fuel_type,
            gearbox=new_car.gearbox,
            body_type=new_car.body_type,
            colour=new_car.colour,
            type_of_color=new_car.type_of_color,
            accident_free=new_car.accident_free,
            state=new_car.state,
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


def get_all_cars_filtered(brand, model, min_year, max_year, min_mileage, max_mileage, fuel_type, gearbox, status):
    session = Session()
    try:
        model_filters = or_(*[Car.model.like(f'%{m}%') for m in model if m])
        fuel_type_filters = or_(*[Car.fuel_type.like(f'%{fuel_type}%') for fuel_type in fuel_type if fuel_type])
        gearbox_filters = or_(*[Car.gearbox.like(f'%{gearbox}%') for gearbox in gearbox if gearbox])

        return session.query(Car).filter(
            Car.brand == brand,
            model_filters,
            Car.year >= min_year,
            Car.year <= max_year,
            Car.mileage >= min_mileage,
            Car.mileage <= max_mileage,
            fuel_type_filters,
            gearbox_filters,
            Car.state.like(f'%{status}%')
        ).all()
    except Exception as e:
        print(f'An error occurred while getting all cars by brand and model:\n    {e}')
    finally:
        session.close()
