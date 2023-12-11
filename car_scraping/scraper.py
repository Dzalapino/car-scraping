import random
import time
import requests
from bs4 import BeautifulSoup
from math import ceil
from car_scraping.car import Car
import car_scraping.utils as utils
import repository.car_repository as car_repo
import repository.total_cars_repository as total_cars_repo


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


def scrape_total_used_new(car_brand=None) -> tuple[int, int]:  # Get the total number of used and new cars
    used_url = utils.get_page_url(URL, USED, car_brand)
    try:
        response = requests.get(used_url, headers).text
        soup = BeautifulSoup(response, 'html.parser')
        n_used = soup.find('a', {'data-testid': 'select-used'}).get_text(strip=True)
        n_new = soup.find('a', {'data-testid': 'select-new'}).get_text(strip=True)
        return utils.extract_numbers_from_string(n_used), utils.extract_numbers_from_string(n_new)
    except Exception as e:
        print(f'Encountered problem while getting number of used and new cars on page{used_url}\nerror message: {e}')
        return 0, 0


def scrape_n_pages(n_pages: int, car_brand=None, from_page=1, min_sleep=4., max_sleep=7., print_steps=True) -> None:
    """
    Main scraping method. It will iterate through pages and scrape cars info
    :param n_pages: Number of pages to scrape
    :param car_brand: Name of the car brand to scrape. If none given all possible brands will be scrapped
    :param from_page: Number of page from which scrapping will start
    :param min_sleep: Minimum time delay after request
    :param max_sleep: Maximum time delay after request
    :param print_steps: Should method print the steps it's taking
    """
    n_used, n_new = scrape_total_used_new(car_brand)  # Get the total number of used and new cars

    used_ratio = n_used/(n_used+n_new)  # Calculate the ratio of used cars
    n_pages_used = ceil(used_ratio * n_pages)  # Get the number of pages for the used cars based on the ratio
    n_pages_new = n_pages - n_pages_used  # Get the number of pages for new cars

    brands = set()
    if print_steps:
        print(f'Scraping used cars...')
    for i in range(from_page, from_page + n_pages_used):  # Iterate through n used pages
        if print_steps:
            print(f'  Scraping page {i}')

        # Rotate between different User-Agents to mimic different browsers or devices
        headers['User-Agent'] = random.choice(USER_AGENTS)

        page_used = utils.get_page_url(URL, USED, car_brand, i)  # Get url for used cars on page i
        brands.update(scrape_cars_from_page(page_used, USED))  # Scrape used cars with given url & add brands to update

        if print_steps:
            print(f'  Delay after page {i} of used cars...')
        time.sleep(random.uniform(min_sleep, max_sleep))  # Wait some time delay to mimic human behavior

    if print_steps:
        print(f'Scraping new cars...')
    for i in range(from_page, from_page + n_pages_new):  # Iterate through n new pages
        if print_steps:
            print(f'  Scraping page {i}')

        headers['User-Agent'] = random.choice(USER_AGENTS)  # Change user agents

        page_new = utils.get_page_url(URL, NEW, car_brand, i)  # Get url for new cars
        brands.update(scrape_cars_from_page(page_new, NEW))  # Scrape new cars and add brands

        if print_steps:
            print(f'  Delay after page {i} of new cars...')
        time.sleep(random.uniform(min_sleep, max_sleep))  # Wait

    if print_steps:
        print('Updating total number of used and new cars for scraped brands...')
    total_cars_repo.update_or_create_total_cars('*', n_used, n_new)  # Update total number of used and new cars in db
    for brand in brands:
        if print_steps:
            print(f'  Updating for {brand}')
        total_used, total_new = scrape_total_used_new(brand)
        total_cars_repo.update_or_create_total_cars(brand, total_used, total_new)


def scrape_cars_from_page(page: str, status=None) -> set[str]:
    """
    Method sends request to the page to scrape, then creates beautiful soup object to work with
    :param page: url of page to scrape
    :param status: used or new
    """
    try:
        response = requests.get(page, headers).text
        soup = BeautifulSoup(response, 'html.parser')
        return save_cars(soup, status)
    except Exception as e:
        print(f'Encountered problem on the page {page}, error message: {e}')
        return set()


def save_cars(soup: BeautifulSoup, status=None) -> set[str]:
    """
    Actual cars scrapping and saving in database with BeautifulSoup object.
    :param soup: BeautifulSoup object from response
    :param status: used or new
    """
    # Get the html elements representing single car offers
    search_results = soup.find('div', class_='ooa-1hab6wx er8sc6m9')
    car_articles = search_results.find_all('article', class_='ooa-1t80gpj ev7e6t818')
    brands = set()
    try:
        for car_article in car_articles:  # Iterate through car offers elements
            # Get the particular html elements representing needed car properties
            url_element = car_article.find('a', href=True)
            full_name_element = car_article.find('h1')
            list_element = car_article.find('div', class_='ooa-d3dp2q ev7e6t816')
            mileage_element = list_element.find('dd', {'data-parameter': 'mileage'})
            fuel_type_element = list_element.find('dd', {'data-parameter': 'fuel_type'})
            gearbox_element = list_element.find('dd', {'data-parameter': 'gearbox'})
            year_element = list_element.find('dd', {'data-parameter': 'year'})
            price_element = car_article.find('h3', class_='ev7e6t82 ooa-bz4efo er34gjf0')
            car_to_add = Car(
                    link=url_element['href'] if url_element is not None else None,
                    full_name=full_name_element.get_text(strip=True) if full_name_element else None,
                    url_brand='',
                    mileage=int(mileage_element.get_text(strip=True).replace(" ", "")
                                .removesuffix('km')) if mileage_element else None,
                    fuel_type=fuel_type_element.get_text(strip=True) if fuel_type_element else None,
                    gearbox=gearbox_element.get_text(strip=True) if gearbox_element else None,
                    year=int(year_element.get_text(strip=True)) if year_element else None,
                    status=status,
                    price_pln=int(price_element.get_text(strip=True).replace(" ", "")) if price_element else None
                )
            car_to_add.url_brand = utils.get_brand_from_full_name(car_to_add.full_name)
            brands.add(car_to_add.url_brand)
            car_repo.add_car_if_not_exists(car_to_add)
    except Exception as e:
        print(f'Encountered problem while extracting cars data, error message: {e}')
        return set()

    return brands
