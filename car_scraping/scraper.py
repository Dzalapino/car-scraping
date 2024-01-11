import random
import time
import requests
from enum import Enum
from bs4 import BeautifulSoup
from car_scraping.car import Car
import repository.car_repository as car_repo


class Page(Enum):
    otomoto = 'otomoto'
    otomoto_url = 'https://www.otomoto.pl/osobowe'
    olx = 'olx'
    olx_url = 'https://www.olx.pl/motoryzacja/samochody/'

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

labels_to_find_otomoto = [
    'Marka pojazdu',
    'Model pojazdu',
    'Przebieg',
    'Pojemność skokowa',
    'Moc',
    'Rok produkcji',
    'Rodzaj paliwa',
    'Skrzynia biegów',
    'Typ nadwozia',
    'Kolor',
    'Rodzaj koloru',
    'Bezwypadkowy',
    'Stan'
]

labels_to_find_olx = [
    'Model',
    'Przebieg',
    'Poj. silnika',
    'Moc silnika',
    'Rok produkcji',
    'Paliwo',
    'Skrzynia biegów',
    'Typ nadwozia',
    'Kolor',
    'Stan techniczny',
]


def scrape_n_pages(from_page=Page.otomoto, n_pages=1, start_page=1,
                   min_sleep=4., max_sleep=7., print_steps=True) -> None:
    """
    Main scraping method. It will iterate through pages and scrape cars info and update total number of cars in db
    :param from_page: Page to scrape from
    :param n_pages: Number of pages to scrape
    :param car_brand: Name of the car brand to scrape. If none given all possible brands will be scrapped
    :param start_page: Number of page from which scrapping will start
    :param min_sleep: Minimum time delay after request
    :param max_sleep: Maximum time delay after request
    :param print_steps: If True, method will print the steps it's taking
    :return: None
    """
    if print_steps:
        print(f'Scraping cars...')

    for i in range(start_page, start_page + n_pages):
        if print_steps:
            print(f'  Scraping page {i} of cars from {from_page.value}?page={i}')

        links = scrape_links_from_page(from_page.value + f'?page={i}')

        for car_link in links:
            # Rotate between different User-Agents to mimic different browsers or devices
            headers['User-Agent'] = random.choice(USER_AGENTS)

            scrape_car_info(car_link)

            if print_steps:
                print(f'    Delay after car at link {car_link} from page number {i}...')
            time.sleep(random.uniform(min_sleep, max_sleep))  # Wait some time delay to mimic human behavior


def scrape_links_from_page(page: str) -> list[str]:
    """
    Method sends request to the page to scrape, then creates beautiful soup object to work with
    :param page: Url of page to scrape
    :return: List of links to cars
    """
    try:
        cookie = {'cookie_name': 'cookie_value'}
        session = requests.Session()
        session.cookies.update(cookie)

        response = session.get(page, headers=headers).text
        soup = BeautifulSoup(response, 'html.parser')
        # Check if page is otomoto or olx
        if str(Page.otomoto_url.value) in page:
            return get_links_otomoto(soup)
        elif str(Page.olx_url.value) in page:
            return get_links_olx(soup)
        return []
    except Exception as e:
        print(f'Encountered problem on the page {page}, error message: {e}')
        return []


def get_links_otomoto(soup) -> list[str]:
    """
    Method that returns links to cars with BeautifulSoup object from response
    :param soup: BeautifulSoup object from response
    :return: List of links to cars
    """
    links = []
    try:
        # Get the div element storing all car offers on the page
        search_results = soup.find('div', class_='ooa-r53y0q ezh3mkl11')
        # Get all car offers elements
        car_articles = search_results.find_all('article', class_='ooa-yca59n e1oqyyyi0')
        for car_article in car_articles:  # Iterate through car offers elements
            # Get the particular html elements representing needed car properties
            url_element = car_article.find('a', href=True)
            links.append(url_element['href'] if url_element is not None else None)
        return links
    except Exception as e:
        print(f'Encountered problem while extracting car links from page, error message: {e}')
        return []


def get_links_olx(soup) -> list[str]:
    """
    Method that returns links to cars with BeautifulSoup object from response
    :param soup: BeautifulSoup object from response
    :return: List of links to cars
    """
    links = []
    try:
        # Get the div element storing all car offers on the page
        search_results = soup.find('div', class_='css-oukcj3')
        # Get all car offers elements
        car_articles = search_results.find_all('div', class_='css-1sw7q4x')
        for car_article in car_articles:  # Iterate through car offers elements
            # Get the particular html elements representing needed car properties
            url_element = car_article.find('a', href=True)
            if Page.otomoto_url.value in url_element['href']:  # Some auctions on olx are from otomoto
                links.append(url_element['href'])
            else:
                links.append('https://www.olx.pl' + url_element['href'] if url_element is not None else None)
        return links
    except Exception as e:
        print(f'Encountered problem while extracting urls of cars, error message: {e}')
        return []


def scrape_car_info(page) -> None:
    """
    Method sends request to the page to scrape, then creates beautiful soup object to work with
    :param page: Url of page to scrape
    :return: None
    """
    try:
        response = requests.get(page, headers).text
        soup = BeautifulSoup(response, 'html.parser')
        # Check if page is otomoto or olx
        if str(Page.otomoto_url.value) in page:
            save_cars_otomoto(soup, page)
        elif str(Page.olx.value) in page:
            save_cars_olx(soup, page)
    except Exception as e:
        print(f'Encountered problem on the page {page}, error message: {e}')


def save_cars_otomoto(soup: BeautifulSoup, link: str) -> None:
    """
    Method that saves cars to database with BeautifulSoup object from response for otomoto
    :param link: Link to car offer
    :param soup: BeautifulSoup object from response
    """
    try:
        # Dictionary to store label-value pairs
        car_details = {}

        # Get price element
        price_element = (soup.find('h3', class_='offer-price__number eqdspoq4 ooa-o7wv9s er34gjf0')
                         .text.replace(' ', ''))

        # Find all div elements with specific class
        details = soup.find_all("div", class_="ooa-162vy3d e18eslyg3")
        # Filter the details list to keep only the elements that have labels we want to keep
        details = [detail for detail in details if detail.find("p", class_="e18eslyg4 ooa-12b2ph5").text.strip() in labels_to_find_otomoto]

        # Loop through each div to extract label-value pairs
        for detail in details:
            label = detail.find('p', class_="e18eslyg4 ooa-12b2ph5").text.strip()
            if label in [labels_to_find_otomoto[0], labels_to_find_otomoto[1], labels_to_find_otomoto[6],
                         labels_to_find_otomoto[7], labels_to_find_otomoto[8], labels_to_find_otomoto[9],
                         labels_to_find_otomoto[11], labels_to_find_otomoto[12]]:
                value = detail.find('a', class_="e16lfxpc1 ooa-1ftbcn2").text.strip()
            else:
                value = detail.find('p', class_="e16lfxpc0 ooa-1pe3502 er34gjf0").text.strip()

            # Check if the label matches the ones we're interested in
            if label in labels_to_find_otomoto:
                car_details[label] = value

        # Create car object
        car = Car(
            link=link,
            brand=car_details[labels_to_find_otomoto[0]] if labels_to_find_otomoto[0] in car_details else None,
            model=car_details[labels_to_find_otomoto[1]] if labels_to_find_otomoto[1] in car_details else None,
            mileage=int(car_details[labels_to_find_otomoto[2]].replace('km', '').replace(' ', '')) if labels_to_find_otomoto[2] in car_details else None,
            engine_capacity=int(car_details[labels_to_find_otomoto[3]].replace('cm3', '').replace(' ', '')) if labels_to_find_otomoto[3] in car_details else None,
            engine_power=int(car_details[labels_to_find_otomoto[4]].replace('KM', '').replace(' ', '')) if labels_to_find_otomoto[4] in car_details else None,
            year=int(car_details[labels_to_find_otomoto[5]]) if labels_to_find_otomoto[5] in car_details else None,
            fuel_type=car_details[labels_to_find_otomoto[6]] if labels_to_find_otomoto[6] in car_details else None,
            gearbox=car_details[labels_to_find_otomoto[7]] if labels_to_find_otomoto[7] in car_details else None,
            body_type=car_details[labels_to_find_otomoto[8]] if labels_to_find_otomoto[8] in car_details else None,
            colour=car_details[labels_to_find_otomoto[9]] if labels_to_find_otomoto[9] in car_details else None,
            type_of_color=car_details[labels_to_find_otomoto[10]] if labels_to_find_otomoto[10] in car_details else None,
            accident_free=car_details[labels_to_find_otomoto[11]] if labels_to_find_otomoto[11] in car_details else None,
            state=car_details[labels_to_find_otomoto[12]] if labels_to_find_otomoto[12] in car_details else None,
            price_pln=int(price_element.replace(' ', '')) if price_element else None
        )

        car_repo.add_car_if_not_exists(car)  # Add car to database

    except Exception as e:
        print(f'Encountered problem while extracting car data from page {link}, error message: {e}')


def save_cars_olx(soup: BeautifulSoup, link: str) -> None:
    """
    Method that saves cars to database with BeautifulSoup object from response for olx
    :param soup: BeautifulSoup object from response
    :param link: Link to car offer
    :return: None
    """
    try:
        # Dictionary to store label-value pairs
        car_details = {}

        # Find the first 'a' element that stores the value of brand name
        brand_element = soup.find(
            lambda tag: tag.name == 'a' and tag.get('href', '').startswith('/motoryzacja/samochody/') and tag.get(
                'href').count('/') == 4)

        # Get the price element
        price_element = soup.find('h3', class_='css-93ez2t')

        # Find all list items with class "css-1r0si1e"
        list_items = soup.find_all('li', class_='css-1r0si1e')

        # Loop through each list item to extract label-value pairs
        for item in list_items:
            p_element = item.find('p', class_='css-b5m1rv')

            # Check if the p element exists and does not contain a span (it is different and not contain ':')
            if p_element and not p_element.find('span'):
                label = p_element.text.split(': ')[0]
                value = p_element.text.split(': ')[1]
                car_details[label] = value

        # Create car object
        car = Car(
            link=link,
            brand=brand_element.get_text(strip=True) if brand_element else None,
            model=car_details[labels_to_find_olx[0]] if labels_to_find_olx[0] in car_details else None,
            mileage=int(car_details[labels_to_find_olx[1]].replace('km', '').replace(' ', '')) if labels_to_find_olx[1] in car_details else None,
            engine_capacity=int(car_details[labels_to_find_olx[2]].replace('cm³', '').replace(' ', '')) if labels_to_find_olx[2] in car_details else None,
            engine_power=int(car_details[labels_to_find_olx[3]].replace('KM', '').replace(' ', '')) if labels_to_find_olx[3] in car_details else None,
            year=int(car_details[labels_to_find_olx[4]]) if labels_to_find_olx[4] in car_details else None,
            fuel_type=car_details[labels_to_find_olx[5]] if labels_to_find_olx[5] in car_details else None,
            gearbox=car_details[labels_to_find_olx[6]] if labels_to_find_olx[6] in car_details else None,
            body_type=car_details[labels_to_find_olx[7]] if labels_to_find_olx[7] in car_details else None,
            colour=car_details[labels_to_find_olx[8]] if labels_to_find_olx[8] in car_details else None,
            type_of_color=None,
            accident_free=car_details[labels_to_find_olx[9]] if labels_to_find_olx[9] in car_details else None,
            state=None,
            price_pln=int(price_element.text.strip().replace(' ', '').replace('zł', '')) if price_element else None
        )

        # Set the state of the car based on mileage
        if car.mileage < 500:
            car.state = 'Nowy'
        else:
            car.state = 'Używany'

        car_repo.add_car_if_not_exists(car)  # Add car to database

    except Exception as e:
        print(f'Encountered problem while extracting car data from page {link}, error message: {e}')
