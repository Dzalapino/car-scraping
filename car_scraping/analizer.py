"""
file that contains all the logic needed to analise the data in the car repository to get the cars with the best price
(cheaper than the average price of the same car in the repository)
"""

import car_scraping.utils as utils
from repository import car_repository as car_repo


def analise_cars_with_best_price(cars_with_best_price: list):
    """
    Method that analises the cars with the best price and prints the results
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





def get_cars_with_best_price(brand: str, model: str) -> list:
    """
    Method that returns the brand and model of cars with the best price
    in the repository
    :return: list of cars with the best price
    """
    cars = car_repo.get_all_cars_by_brand_and_model(brand, model)
    if not cars:
        print(f'No cars found for brand {brand} and model {model}')
        return []

    average_price = utils.get_average_price(cars)
    print(f'Average price for {brand} {model} is {average_price}')

    cars_with_best_price = [car for car in cars if car.price_pln < average_price]
    analise_cars_with_best_price(cars_with_best_price)
