import pandas as pd
import matplotlib.pyplot as plt
import time
from repository import db_connection
from repository.models import Car


def analise_data(visualize_data=True) -> None:
    # Fetch data from the database and create a DataFrame
    query = db_connection.Session().query(Car)
    cars_data = pd.read_sql(query.statement, query.session.bind)

    pd.set_option('display.float_format', '{:.2f}'.format)

    # Check basic statistics and information about the data collectively
    print('Basic statistics about the data:')
    print(cars_data.describe())

    print('\nInformation about the data:')
    print(cars_data.info())

    # Check basic statistics and information about the data for olx and otomoto separately
    print('\nBasic statistics about the data from olx:')
    print(cars_data[cars_data['link'].str.contains('olx')].describe())

    print('\nInformation about the data from olx:')
    print(cars_data[cars_data['link'].str.contains('olx')].info())

    print('\nBasic statistics about the data from otomoto:')
    print(cars_data[cars_data['link'].str.contains('otomoto')].describe())

    print('\nInformation about the data from otomoto:')
    print(cars_data[cars_data['link'].str.contains('otomoto')].info())

    # Check for missing data collectively
    missing_data_percentage = cars_data.isnull().sum() / len(cars_data) * 100
    print('\nPercentage of missing data:')
    print(missing_data_percentage)

    # Check for missing data for olx and otomoto separately
    missing_data_percentage_olx = cars_data[cars_data['link'].str.contains('olx')].isnull().sum() / \
                                  len(cars_data[cars_data['link'].str.contains('olx')]) * 100

    missing_data_percentage_otomoto = cars_data[cars_data['link'].str.contains('otomoto')].isnull().sum() / \
                                        len(cars_data[cars_data['link'].str.contains('otomoto')]) * 100

    print('\nPercentage of missing data from olx:')
    print(missing_data_percentage_olx)

    print('\nPercentage of missing data from otomoto:')
    print(missing_data_percentage_otomoto)

    if visualize_data:
        # Collective visualization
        # ------------------------

        # Check and visualize the missing data in each column
        plt.figure(figsize=(15, 10))
        missing_data_percentage.plot(kind='bar')
        plt.title('Percentage of missing data in each column for all data')
        plt.xlabel('Column name')
        plt.ylabel('Percentage')
        plt.xticks(rotation=60)
        plt.show()
        time.sleep(1)

        # Check the distribution of the data for numeric columns
        numeric_columns = ['mileage', 'engine_capacity', 'engine_power', 'year', 'price_pln']
        cars_data[numeric_columns].hist(bins=20, figsize=(15, 10))
        plt.suptitle('Distribution of the data for numeric columns for all data')
        plt.show()
        time.sleep(1)

        # Check the distribution of the data for categorical columns
        categorical_columns = ['brand', 'fuel_type', 'gearbox', 'body_type', 'colour',
                               'type_of_color', 'accident_free', 'state',]
        for column in categorical_columns:
            plt.figure(figsize=(15, 10))
            cars_data[column].value_counts().plot(kind='bar')
            plt.title(f'Distribution of the data for {column} for all data')
            plt.xlabel(column)
            plt.ylabel('Number of cars')
            plt.xticks(rotation=80)
            plt.show()
            time.sleep(1)

        # Show the distribution of the model categorical column and limit the visibility to most popular models
        # (too much models to be visible on one plot)
        top_models_counts = cars_data['model'].value_counts().head(50)
        plt.figure(figsize=(15, 10))
        top_models_counts.plot(kind='bar')
        plt.title('Distribution of the data for model for all data')
        plt.xlabel('Model')
        plt.ylabel('Number of cars')
        plt.xticks(rotation=60)
        plt.show()
        time.sleep(1)

        # Show the distribution of the location categorical column and limit the visibility to most popular models
        top_locations_counts = cars_data['location'].value_counts().head(50)
        # Discard first element because it is a missing value
        top_locations_counts = top_locations_counts[1:]
        plt.figure(figsize=(25, 20))
        top_locations_counts.plot(kind='bar')
        plt.title('Distribution of the data for location for all data')
        plt.xlabel('Location')
        plt.ylabel('Number of cars')
        plt.show()
        time.sleep(1)

        # Visualization for olx and otomoto separately
        # --------------------------------------------

        # Check the distribution of the data for numeric columns from otomoto
        cars_data[cars_data['link'].str.contains('otomoto')][numeric_columns].hist(bins=20, figsize=(15, 10))
        plt.suptitle('Distribution of the data for numeric columns from otomoto')
        plt.show()
        time.sleep(1)

        # Check the distribution of the data for categorical columns from otomoto
        for column in categorical_columns:
            plt.figure(figsize=(15, 10))
            cars_data[cars_data['link'].str.contains('otomoto')][column].value_counts().plot(kind='bar')
            plt.title(f'Distribution of the data for {column} from otomoto')
            plt.xlabel(column)
            plt.ylabel('Number of cars')
            plt.xticks(rotation=80)
            plt.show()
            time.sleep(1)

        # Show the distribution of the model categorical column and limit the visibility to most popular models
        # (too much models to be visible on one plot)
        top_models_counts_otomoto = cars_data[cars_data['link'].str.contains('otomoto')]['model'].value_counts().head(50)
        plt.figure(figsize=(15, 10))
        top_models_counts_otomoto.plot(kind='bar')
        plt.title('Distribution of the data for model from otomoto')
        plt.xlabel('Model')
        plt.ylabel('Number of cars')
        plt.xticks(rotation=60)
        plt.show()
        time.sleep(1)

        # Show the distribution of the location categorical column and limit the visibility to most popular models
        top_locations_counts_otomoto = cars_data[cars_data['link'].str.contains('otomoto')]['location'].value_counts().head(50)
        # Discard first element because it is a missing value
        top_locations_counts_otomoto = top_locations_counts_otomoto[1:]
        plt.figure(figsize=(25, 20))
        top_locations_counts_otomoto.plot(kind='bar')
        plt.title('Distribution of the data for location from otomoto')
        plt.xlabel('Location')
        plt.ylabel('Number of cars')
        plt.show()
        time.sleep(1)

        # Check the distribution of the data for numeric columns from olx
        cars_data[cars_data['link'].str.contains('olx')][numeric_columns].hist(bins=20, figsize=(15, 10))
        plt.suptitle('Distribution of the data for numeric columns from olx')
        plt.show()
        time.sleep(1)

        # Check the distribution of the data for categorical columns from olx
        categorical_columns.remove('type_of_color')
        for column in categorical_columns:
            plt.figure(figsize=(15, 10))
            cars_data[cars_data['link'].str.contains('olx')][column].value_counts().plot(kind='bar')
            plt.title(f'Distribution of the data for {column} from olx')
            plt.xlabel(column)
            plt.ylabel('Number of cars')
            plt.xticks(rotation=80)
            plt.show()
            time.sleep(1)

        # Show the distribution of the model categorical column and limit the visibility to most popular models
        # (too much models to be visible on one plot)
        top_models_counts_olx = cars_data[cars_data['link'].str.contains('olx')]['model'].value_counts().head(50)
        plt.figure(figsize=(15, 10))
        top_models_counts_olx.plot(kind='bar')
        plt.title('Distribution of the data for model from olx')
        plt.xlabel('Model')
        plt.ylabel('Number of cars')
        plt.xticks(rotation=60)
        plt.show()
        time.sleep(1)

        # Show the distribution of the location categorical column and limit the visibility to most popular models
        top_locations_counts_olx = cars_data[cars_data['link'].str.contains('olx')]['location'].value_counts().head(50)
        # Discard first element because it is a missing value
        top_locations_counts_olx = top_locations_counts_otomoto[1:]
        plt.figure(figsize=(25, 20))
        top_locations_counts_olx.plot(kind='bar')
        plt.title('Distribution of the data for locations from olx')
        plt.xlabel('Location')
        plt.ylabel('Number of locations')
        plt.show()
        time.sleep(1)

    # Check how the prices differ between olx and otomoto
    print('\nPrices from olx:')
    print(cars_data[cars_data['link'].str.contains('olx')]['price_pln'].describe())

    print('\nPrices from otomoto:')
    print(cars_data[cars_data['link'].str.contains('otomoto')]['price_pln'].describe())

    # Check how the mileage differ between olx and otomoto
    print('\nMileage from olx:')
    print(cars_data[cars_data['link'].str.contains('olx')]['mileage'].describe())

    print('\nMileage from otomoto:')
    print(cars_data[cars_data['link'].str.contains('otomoto')]['mileage'].describe())

    # Check how the year differ between olx and otomoto
    print('\nYear from olx:')
    print(cars_data[cars_data['link'].str.contains('olx')]['year'].describe())

    print('\nYear from otomoto:')
    print(cars_data[cars_data['link'].str.contains('otomoto')]['year'].describe())

    pd.set_option('display.float_format', '{:.2f}'.format)

    # Check the correlation between the price and the engine capacity
    print('\nCorrelation between the price and the engine capacity:')
    print(cars_data[['price_pln', 'engine_capacity']].corr())

    # Check the correlation between the price and the engine power
    print('\nCorrelation between the price and the engine power:')
    print(cars_data[['price_pln', 'engine_power']].corr())

    # Check the correlation between the price and the year
    print('\nCorrelation between the price and the year:')
    print(cars_data[['price_pln', 'year']].corr())

    # Check the correlation between the price and the mileage
    print('\nCorrelation between the price and the mileage:')
    print(cars_data[['price_pln', 'mileage']].corr())

    # Check for the correlations for olx and otomoto separately
    print('\nCorrelation between the price and the engine capacity from olx:')
    print(cars_data[cars_data['link'].str.contains('olx')][['price_pln', 'engine_capacity']].corr())

    print('\nCorrelation between the price and the engine capacity from otomoto:')
    print(cars_data[cars_data['link'].str.contains('otomoto')][['price_pln', 'engine_capacity']].corr())

    print('\nCorrelation between the price and the engine power from olx:')
    print(cars_data[cars_data['link'].str.contains('olx')][['price_pln', 'engine_power']].corr())

    print('\nCorrelation between the price and the engine power from otomoto:')
    print(cars_data[cars_data['link'].str.contains('otomoto')][['price_pln', 'engine_power']].corr())

    print('\nCorrelation between the price and the year from olx:')
    print(cars_data[cars_data['link'].str.contains('olx')][['price_pln', 'year']].corr())

    print('\nCorrelation between the price and the year from otomoto:')
    print(cars_data[cars_data['link'].str.contains('otomoto')][['price_pln', 'year']].corr())

    print('\nCorrelation between the price and the mileage from olx:')
    print(cars_data[cars_data['link'].str.contains('olx')][['price_pln', 'mileage']].corr())

    print('\nCorrelation between the price and the mileage from otomoto:')
    print(cars_data[cars_data['link'].str.contains('otomoto')][['price_pln', 'mileage']].corr())

    # Create a new column with the price per 1 km
    cars_data['price_per_km'] = cars_data['price_pln'] / cars_data['mileage']
