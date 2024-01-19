
def get_average_price(cars):
    """
    Calculate average price of cars in given list of cars
    :param cars: List of Car objects
    :return: Average price of cars in given list
    """
    prices = [car.price_pln for car in cars]
    return sum(prices) / len(prices) if prices else None
