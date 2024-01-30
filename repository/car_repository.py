from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
import car_scraping.car as scrap
from repository.models import Car
from repository.db_connection import Session


def get_all_cars() -> list[Car]:
    session = Session()
    try:
        return session.query(Car).all()
    except Exception as e:
        print(f'An error occurred while getting all cars:\n    {e}')
        return []
    finally:
        session.close()


def get_all_cars_filtered(brand, model, min_year, max_year, min_mileage, max_mileage,
                          fuel_type, gearbox, status, location) -> list[Car]:
    session = Session()
    try:
        model_filters = or_(*[Car.model.like(f'%{m}%') for m in model if m])
        fuel_type_filters = or_(*[Car.fuel_type.like(f'%{f_t}%') for f_t in fuel_type if f_t])
        gearbox_filters = or_(*[Car.gearbox.like(f'%{g}%') for g in gearbox if g])
        location_filters = or_(*[Car.location.like(f'%{loc}%') for loc in location if loc])

        return session.query(Car).filter(
            Car.brand.like(f'%{brand}%'),
            model_filters,
            Car.year >= min_year,
            Car.year <= max_year,
            Car.mileage >= min_mileage,
            Car.mileage <= max_mileage,
            fuel_type_filters,
            gearbox_filters,
            Car.state.like(f'%{status}%'),
            location_filters
        ).all()
    except Exception as e:
        print(f'An error occurred while getting all cars by brand and model:\n    {e}')
        return []
    finally:
        session.close()


def add_car_if_not_exists(new_car: scrap.Car) -> None:
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
            price_pln=new_car.price_pln,
            location=new_car.location
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


def update_car(car: Car) -> None:
    session = Session()
    try:
        session.query(Car).filter(Car.id == car.id).update({
            'link': car.link,
            'brand': car.brand,
            'model': car.model,
            'mileage': car.mileage,
            'engine_capacity': car.engine_capacity,
            'engine_power': car.engine_power,
            'year': car.year,
            'fuel_type': car.fuel_type,
            'gearbox': car.gearbox,
            'body_type': car.body_type,
            'colour': car.colour,
            'type_of_color': car.type_of_color,
            'accident_free': car.accident_free,
            'state': car.state,
            'price_pln': car.price_pln,
            'location': car.location
        })
        session.commit()
    except Exception as e:
        print(f'An error occurred while updating Car in database:\n    {e}')
        session.rollback()
    finally:
        session.close()
