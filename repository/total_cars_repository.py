from repository.db_connection import Session
from repository.models import TotalCars


def update_or_create_total_cars(brand: str, total_used: int, total_new: int):
    session = Session()

    try:
        # Check if record with the given name already exists
        existing_record = session.query(TotalCars).filter(TotalCars.brand == brand).first()

        if existing_record:
            # Update existing record
            existing_record.total_used = total_used
            existing_record.total_new = total_new
        else:
            # Create new record
            new_record = TotalCars(
                brand=brand,
                total_used=total_used,
                total_new=total_new
            )
            session.add(new_record)

        # Commit the transaction to db
        session.commit()
    except Exception as e:
        # Rollback changes if error occurs
        print(f'An error occurred: {e}')
        session.rollback()
    finally:
        session.close()


def get_all_brands():
    session = Session()

    try:
        return [record.brand for record in session.query(TotalCars.brand).all()]
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        session.close()
