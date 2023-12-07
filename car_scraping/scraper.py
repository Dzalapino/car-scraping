import math
import random
import time
import requests
from bs4 import BeautifulSoup
from math import ceil
from car_scraping.car import Car

URL = 'https://www.otomoto.pl/osobowe'
NEW = 'nowe'
USED = 'uzywane'

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'pl-PL,pl;q=0.8',
    'User-Agent': USER_AGENTS[0]
}


def get_page_url(base_url, status, car_brand=None, page=None) -> str:
    """
    Combine the base url with cars status, its brand and the pagination number
    :param base_url: base url of the scrapped page
    :param status: used or new
    :param car_brand: car brand. If none then omitted in url completely
    :param page: page number
    :return: combined url
    """
    if car_brand:
        if page:
            return f'{base_url}/{status}/{car_brand}?page={page}'
        else:
            return f'{base_url}/{status}/{car_brand}'
    else:
        if page:
            return f'{base_url}/{status}?page={page}'
        else:
            return f'{base_url}/{status}'


def extract_numbers(string) -> int:  # Remove all characters except digits
    numbers = ''.join(filter(str.isdigit, string))
    return int(numbers) if numbers else None


def total_used_new(car_brand=None) -> tuple[int, int]:  # Get the total number of used and new cars
    used_url = get_page_url(URL, USED, car_brand)
    try:
        response = requests.get(used_url, headers).text
        soup = BeautifulSoup(response, 'html.parser')
        n_used = soup.find('a', {'data-testid': 'select-used'}).get_text(strip=True)
        n_new = soup.find('a', {'data-testid': 'select-new'}).get_text(strip=True)
        return extract_numbers(n_used), extract_numbers(n_new)
    except Exception as e:
        print(f'Encountered problem while getting number of used and new cars on page{used_url}\nerror message: {e}')
        return 0, 0


def scrape_n_pages(n_pages: int, car_brand=None, from_page=1,
                   min_sleep=4., max_sleep=7., print_steps=True) -> list[Car]:
    """
    Main scraping method. It will iterate through pages and scrape cars info
    :param n_pages: Number of pages to scrape
    :param car_brand: Name of the car brand to scrape. If none given all possible brands will be scrapped
    :param from_page: Number of page from which scrapping will start
    :param min_sleep: Minimum time delay after request
    :param max_sleep: Maximum time delay after request
    :param print_steps: Should method print the steps it's taking
    :return: list of cars
    """
    cars = []

    n_used, n_new = total_used_new(car_brand)  # Get the total number of used and new cars
    used_ratio = n_used/(n_used+n_new)  # Calculate the ratio of used cars
    n_pages_used = ceil(used_ratio * n_pages)  # Get the number of pages for the used cars based on the ratio
    n_pages_new = n_pages - n_pages_used  # Get the number of pages for new cars
    
    # Iterate through n pages
    for i in range(from_page, from_page + n_pages_used):
        if print_steps:
            print(f'Scraping page {i}')

        # Rotate between different User-Agents to mimic different browsers or devices
        headers['User-Agent'] = random.choice(USER_AGENTS)

        # Used cars
        page_used = get_page_url(URL, USED, car_brand, i)
        cars_to_add = scrape_cars_from_page(page_used, USED)
        if cars_to_add:
            cars.extend(cars_to_add)  # Append cars from the page

        if print_steps:
            print('Delay after used cars...')
        time.sleep(random.uniform(min_sleep, max_sleep))  # Wait some time delay to mimic human behavior

    for i in range(from_page, from_page + n_pages_new):
        # Rotate between different User-Agents to mimic different browsers or devices
        headers['User-Agent'] = random.choice(USER_AGENTS)

        # New cars
        page_new = get_page_url(URL, NEW, car_brand, i)
        cars_to_add = scrape_cars_from_page(page_new, NEW)
        if cars_to_add:
            cars.extend(cars_to_add)  # Append

        if print_steps:
            print('Delay after new cars...')
        time.sleep(random.uniform(min_sleep, max_sleep))  # Wait

    return cars


def scrape_cars_from_page(page: str, status=None) -> list[Car]:
    """
    Method sends request to the page to scrape, then creates beautiful soup object to work with
    :param page: url of page to scrape
    :param status: used or new
    :return: list of cars
    """
    try:
        response = requests.get(page, headers).text
        soup = BeautifulSoup(response, 'html.parser')
        return extract_cars(soup, status)
    except Exception as e:
        print(f'Encountered problem on the page {page}, error message: {e}')
        return []


def extract_cars(soup: BeautifulSoup, status=None) -> list[Car]:
    """
    Actual cars scrapping with BeautifulSoup object.
    :param soup: BeautifulSoup object from response
    :param status: used or new
    :return: list of scraped cars
    """
    # Get the html elements representing single car offers
    search_results = soup.find('div', class_='ooa-1hab6wx er8sc6m9')
    car_articles = search_results.find_all('article', class_='ooa-1t80gpj ev7e6t818')
    cars = []
    try:
        # Iterate through car offers elements
        for car_article in car_articles:
            # Get the particular html elements representing needed car properties
            url_element = car_article.find('a', href=True)
            full_name_element = car_article.find('h1')
            list_element = car_article.find('div', class_='ooa-d3dp2q ev7e6t816')
            mileage_element = list_element.find('dd', {'data-parameter': 'mileage'})
            fuel_type_element = list_element.find('dd', {'data-parameter': 'fuel_type'})
            gearbox_element = list_element.find('dd', {'data-parameter': 'gearbox'})
            year_element = list_element.find('dd', {'data-parameter': 'year'})
            price_element = car_article.find('h3', class_='ev7e6t82 ooa-bz4efo er34gjf0')

            cars.append(
                Car(
                    link=url_element['href'] if url_element is not None else None,
                    full_name=full_name_element.get_text(strip=True) if full_name_element else None,
                    mileage=int(mileage_element.get_text(strip=True).replace(" ", "")
                                .removesuffix('km')) if mileage_element else None,
                    fuel_type=fuel_type_element.get_text(strip=True) if fuel_type_element else None,
                    gearbox=gearbox_element.get_text(strip=True) if gearbox_element else None,
                    year=int(year_element.get_text(strip=True)) if year_element else None,
                    status=status,
                    price_pln=int(price_element.get_text(strip=True).replace(" ", "")) if price_element else None
                )
            )
    except Exception as e:
        print(f'Encountered problem while extracting cars data, error message: {e}')
        return []

    return cars
