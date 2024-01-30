"""
file that contains all the logic needed to analise the data in the car repository to get the cars with the best prices
(cheaper than the average price for the similar cars in the repository or with the best price per km)
"""
from repository import car_repository as car_repo
import pandas as pd


def get_brands_with_best_price(brand: str, model=list[''], min_year=1885, max_year=2050,
                               min_mileage=0, max_mileage=1000000,
                               fuel_type=list[''], gearbox=list[''], status='', location=list['']) -> list:
    """
    Method that returns the brand and model of cars with the best price
    in the repository
    :param brand: brand of the car
    :param model: model (or models) of the car
    :param min_year: minimum year of the car
    :param max_year: maximum year of the car
    :param min_mileage: minimum mileage of the car (in km)
    :param max_mileage: maximum mileage of the car (in km)
    :param fuel_type: fuel type (or types) of the car if empty string then all fuel types
    :param gearbox: gearbox (or gearboxes) of the car if empty string then all gearboxes
    :param status: used or new
    :param location: location (or locations) of the car to seek
    :return: list of car offers with the best prices
    """
    if model is None:
        model = ['']
    if fuel_type is None:
        fuel_type = ['']
    if gearbox is None:
        gearbox = ['']
    if location is None:
        location = ['']
    cars = car_repo.get_all_cars_filtered(brand, model, min_year, max_year, min_mileage, max_mileage,
                                          fuel_type, gearbox, status, [''])
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)

    if not cars:
        print(f'No cars found for brand {brand} and model {model}')
        return []

    # Create a list of dictionaries by extracting attributes from each Car object
    cars_dict = [{'id': car.id,
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
                  'location': car.location} for car in cars]

    # Convert the list of dictionaries to a DataFrame
    cars_df = pd.DataFrame(cars_dict)

    local_cars_df = pd.DataFrame({})
    if location[0] != '':
        # Create a pattern that matches the location
        location_pattern = '|'.join(location)

        # Find rows where the 'location' column contains the pattern
        local_cars_df = cars_df.copy()[cars_df['location'].str.contains(location_pattern, na=False)]

    occasions_compared_locally = []
    occasions_compared_globally = []

    if local_cars_df.size > 0:
        print(f'Found {len(local_cars_df)} cars in {location}')
        local_cars_df['price_per_km'] = local_cars_df['price_pln'] / local_cars_df['mileage']

        for local_car in local_cars_df.itertuples():
            # Get the similar cars locally
            similar_cars_locally = local_cars_df.copy()[
                (local_cars_df['brand'] == local_car.brand) &
                (local_cars_df['model'] == local_car.model) &
                (local_cars_df['gearbox'] == local_car.gearbox) &
                (abs(local_cars_df['year'] - local_car.year) <= 2) &
                (abs(local_cars_df['mileage'] - local_car.mileage) <= 20000)
            ]
            # Get the similar cars globally
            similar_cars_globally = cars_df.copy()[
                (cars_df['brand'] == local_car.brand) &
                (cars_df['model'] == local_car.model) &
                (cars_df['gearbox'] == local_car.gearbox) &
                (abs(cars_df['year'] - local_car.year) <= 2) &
                (abs(cars_df['mileage'] - local_car.mileage) <= 20000)
            ]

            # Calculate the average price for similar local cars
            similar_cars_average_price_locally = similar_cars_locally['price_pln'].mean()
            # Calculate the average price for similar global cars
            similar_cars_average_price_globally = similar_cars_globally['price_pln'].mean()

            # Add the car to the dictionary of cars with the best price if it has better price than average
            if local_car.price_pln < similar_cars_average_price_locally:
                occasions_compared_locally.append({'car': local_car,
                                                   'avg_price_for_similar_car': similar_cars_average_price_locally})
            if local_car.price_pln < similar_cars_average_price_globally:
                occasions_compared_globally.append({'car': local_car,
                                                    'avg_price_for_similar_car': similar_cars_average_price_globally})
        occasions_compared_locally.sort(key=lambda x: x['avg_price_for_similar_car'] - x['car'].price_pln)
        occasions_compared_globally.sort(key=lambda x: x['avg_price_for_similar_car'] - x['car'].price_pln)
    else:
        print(f'Found {len(cars_df)} cars in whole Poland')
        cars_df['price_per_km'] = cars_df['price_pln'] / cars_df['mileage']

        for car in cars_df.itertuples():
            # Get the similar cars
            similar_cars = cars_df.copy()[
                (cars_df['brand'] == car.brand) &
                (cars_df['model'] == car.model) &
                (cars_df['gearbox'] == car.gearbox) &
                (abs(cars_df['year'] - car.year) <= 2) &
                (abs(cars_df['mileage'] - car.mileage) <= 20000)
            ]

            # Calculate the average price for similar cars
            similar_cars_average_price = similar_cars['price_pln'].mean()

            # Add the car to the dictionary of cars with the best price if it has better price than average
            if car.price_pln < similar_cars_average_price:
                occasions_compared_globally.append({'car': car,
                                                    'avg_price_for_similar_car': similar_cars_average_price})
        occasions_compared_globally.sort(key=lambda x: x['avg_price_for_similar_car'] - x['car'].price_pln)

    print(f'Found {len(occasions_compared_globally)} cars with better price than average for similar cars in Poland\n'
          f'(same brand, model, year, fuel type, gearbox, state, mileage +/- 10000 km)\n'
          f'printing the global occasions:')
    for car_occasion in occasions_compared_globally:
        print(f'    {car_occasion["car"].brand} {car_occasion["car"].model}, {car_occasion["car"].year},'
              f' {car_occasion["car"].fuel_type}, {car_occasion["car"].gearbox}, {car_occasion["car"].mileage} km:'
              f' {car_occasion["car"].link}\n        Price: {car_occasion["car"].price_pln} PLN\n'
              f'        Average price for similar cars: {car_occasion["avg_price_for_similar_car"]} PLN')

    if len(occasions_compared_globally) > 0:
        n_otomoto_occasions = len([car_occasion for car_occasion in occasions_compared_globally if 'otomoto' in car_occasion['car'].link])
        n_olx_occasions = len([car_occasion for car_occasion in occasions_compared_globally if 'olx' in car_occasion['car'].link])
        print('Number of car occasions from otomoto:')
        print(f'{n_otomoto_occasions} ({n_otomoto_occasions / len(occasions_compared_globally) * 100}%)')

        print('Number of car occasions from olx:')
        print(f'{n_olx_occasions} ({n_olx_occasions / len(occasions_compared_globally) * 100}%)')

    percent = 20
    if not local_cars_df.empty:
        print(f'Found {len(occasions_compared_locally)} cars with better price than average for simillar cars in {location}')
        if len(occasions_compared_locally) > 0:
            print('printing the local occasions:')
            for car_occasion in occasions_compared_locally:
                print(f'    {car_occasion["car"].brand} {car_occasion["car"].model}, {car_occasion["car"].year},'
                      f' {car_occasion["car"].fuel_type}, {car_occasion["car"].gearbox}, {car_occasion["car"].mileage} km:'
                      f' {car_occasion["car"].link}\n        Price: {car_occasion["car"].price_pln} PLN\n'
                      f'        Average price for similar cars: {car_occasion["avg_price_for_similar_car"]} PLN')
            n_otomoto_occasions = len(
                [car_occasion for car_occasion in occasions_compared_locally if 'otomoto' in car_occasion['car'].link])
            n_olx_occasions = len(
                [car_occasion for car_occasion in occasions_compared_locally if 'olx' in car_occasion['car'].link])

            print('Number of car occasions from otomoto:')
            print(f'{n_otomoto_occasions} ({n_otomoto_occasions / len(occasions_compared_locally) * 100}%)')

            print('Number of car occasions from olx:')
            print(f'{n_olx_occasions} ({n_olx_occasions / len(occasions_compared_locally) * 100}%)')

        print(f'Top local cars with best price per km:')
        local_cars_df.sort_values(by=['price_per_km'], inplace=True, ignore_index=True)
        best_local_cars = local_cars_df.head(int(len(local_cars_df) * percent / 100))
        print(best_local_cars[['brand', 'model', 'price_per_km', 'link']])

        print(f'Percentage of top cars with best price per km from otomoto:')
        print(len(best_local_cars[best_local_cars['link'].str.contains('otomoto')])
              / len(best_local_cars) * 100)

        print(f'Percentage of top local cars with best price per km from olx:')
        print(len(best_local_cars[best_local_cars['link'].str.contains('olx')])
              / len(best_local_cars) * 100)
    else:
        print(f'Top {percent}% cars with best price per km:')
        cars_df.sort_values(by=['price_per_km'], inplace=True, ignore_index=True)
        top_cars = cars_df.head(int(len(cars_df) / percent * 100))
        print(top_cars[['brand', 'model', 'price_per_km', 'link']])

        print(f'Percentage of top {percent}% cars with best price per km from otomoto:')
        print(len(top_cars[top_cars['link'].str.contains('otomoto')]) / len(top_cars) * 100)

        print(f'Percentage of top {percent}% cars with best price per km from olx:')
        print(len(top_cars[top_cars['link'].str.contains('olx')]) / len(top_cars) * 100)
