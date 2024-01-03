"""
file that contains all the logic needed to analise the data in the car repository to get the cars with the best price
(cheaper than the average price of the same car in the repository)
"""

import car_scraping.utils as utils
from repository import car_repository as car_repo


def analise_brands_with_best_price(cars_with_best_price: list):
    """
    Method that analyses the cars with the best price and prints the results
    :param cars_with_best_price: List of cars with the best price
    """
    if not cars_with_best_price:
        print('No cars with best price found')
        return

    print(f'Found {len(cars_with_best_price)} cars with best price:')
    for car in cars_with_best_price:
        print(f'    {car.full_name} - {car.price_pln} PLN')
        print(f'        {car.link}')

    print(f'\nTop 5 cars with best price with best mileage:')
    cars_with_best_price.sort(key=lambda x: x.mileage)
    for car in cars_with_best_price[:5]:
        print(f'    {car.full_name} - {car.mileage} km, {car.price_pln} PLN')
        print(f'        {car.link}')

    print(f'\nTop 5 cars with best price with best year:')
    cars_with_best_price.sort(key=lambda x: x.year, reverse=True)
    for car in cars_with_best_price[:5]:
        print(f'    {car.full_name} - {car.year}, {car.price_pln} PLN')
        print(f'        {car.link}')


def get_brands_with_best_price(brand: str, model: str, min_year=1885, max_year=2050,
                               min_mileage=0, max_mileage=1000000, fuel_type='', gearbox='') -> list:
    """
    Method that returns the brand and model of cars with the best price
    in the repository
    :param brand: brand of the car
    :param model: model of the car
    :param min_year: minimum year of the car
    :param max_year: maximum year of the car
    :param min_mileage: minimum mileage of the car (in km)
    :param max_mileage: maximum mileage of the car (in km)
    :param fuel_type: fuel type of the car if empty string then all fuel types
    :param gearbox: gearbox of the car if empty string then all gearboxes
    :return: list of cars with the best price
    """
    cars = car_repo.get_all_cars_filtered(brand, model, min_year, max_year, min_mileage, max_mileage, fuel_type, gearbox)
    if not cars:
        print(f'No cars found for brand {brand} and model {model}')
        return []

    average_price = utils.get_average_price(cars)
    print(f'Average price for {brand} {model} is {average_price}')

    brands_with_best_price = [car for car in cars if car.price_pln < average_price]
    analise_brands_with_best_price(brands_with_best_price)
