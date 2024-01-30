import random
import time
import requests
from enum import Enum
from bs4 import BeautifulSoup
from car_scraping.car import Car
import repository.car_repository as car_repo
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(page)
        # Check if page is otomoto or olx
        if str(Page.otomoto_url.value) in page:
            save_cars_otomoto(driver)
        elif str(Page.olx.value) in page:
            save_cars_olx(driver)
    except Exception as e:
        print(f'Encountered problem on the page {page}, error message: {e}')
    finally:
        driver.quit()


def save_cars_otomoto(driver) -> None:
    """
    Method that saves cars to the database with Selenium driver for Otomoto
    :param driver: Selenium WebDriver
    """
    try:
        # Dictionary to store label-value pairs
        car_details = {}

        # Wait for price element to be present
        price_element = driver.find_element(By.XPATH, '//h3[@class="offer-price__number eqdspoq4 ooa-o7wv9s er34gjf0"]')

        # Find all div elements with specific class
        details = driver.find_elements(By.CSS_SELECTOR, 'div.ooa-162vy3d.e18eslyg3')

        location_element = driver.find_elements(By.XPATH, '//a[@class="edhv9y51 ooa-oxkwx3"]')
        location_element = [element for element in location_element
                            if 'Przejdź do' not in element.text and 'Zobacz więcej' not in element.text]

        # Filter the details list to keep only the elements that have labels we want to keep
        details = [detail for detail in details if detail.find_element(By.CSS_SELECTOR, 'p.e18eslyg4.ooa-12b2ph5').text.strip() in labels_to_find_otomoto]

        # Loop through each div to extract label-value pairs
        for detail in details:
            label = detail.find_element(By.CSS_SELECTOR, 'p.e18eslyg4.ooa-12b2ph5').text.strip()
            if label in [labels_to_find_otomoto[0], labels_to_find_otomoto[1], labels_to_find_otomoto[6],
                         labels_to_find_otomoto[7], labels_to_find_otomoto[8], labels_to_find_otomoto[9],
                         labels_to_find_otomoto[11], labels_to_find_otomoto[12]]:
                value = detail.find_element(By.CSS_SELECTOR, 'a.e16lfxpc1.ooa-1ftbcn2').text.strip()
            else:
                value = detail.find_element(By.CSS_SELECTOR, 'p.e16lfxpc0.ooa-1pe3502.er34gjf0').text.strip()

            # Check if the label matches the ones we're interested in
            if label in labels_to_find_otomoto:
                car_details[label] = value

        # Create car object
        car = Car(
            link=driver.current_url,
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
            price_pln=int(price_element.text.replace(' ', '')) if price_element else None,
            location=location_element[0].text.strip() if len(location_element) > 0 else ''
        )

        car_repo.add_car_if_not_exists(car)  # Add car to the database

    except Exception as e:
        print(f'Encountered a problem while extracting car data from page {driver.current_url}, error message: {e}')


def save_cars_olx(driver) -> None:
    """
    Method that saves cars to the database with Selenium.
    :param driver: Selenium WebDriver
    :return: None
    """
    try:

        # Dictionary to store label-value pairs
        car_details = {}

        # Find the first 'a' element that stores the value of brand name (using a more general approach)
        brand_element = driver.find_elements(
            By.XPATH,
            '//a[@class="css-tyi2d1" and starts-with(@href, "/motoryzacja/samochody/")]'
        )

        # Get the price element
        price_element = driver.find_element(By.CSS_SELECTOR, 'h3.css-93ez2t')

        # Wait for location element to be present
        location_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//p[@class="css-1cju8pu er34gjf0"]'))
        )

        # Wait for region elements to be present
        region_element = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//p[@class="css-b5m1rv er34gjf0"]'))
        )
        location = ''
        if location_element:
            location += location_element.text.strip()
            if location.endswith(','):
                location = location[:-1]
        if region_element:
            if region_element[-1] != 'Więcej od tego ogłoszeniodawcy':
                location += ' - ' + region_element[-1].text.strip()

        # Find all list items with class "css-1r0si1e"
        list_items = driver.find_elements(By.CSS_SELECTOR, 'li.css-1r0si1e')

        # Loop through each list item to extract label-value pairs
        for item in list_items:
            p_element = item.find_element(By.CSS_SELECTOR, 'p.css-b5m1rv')

            # Check if the p element exists and does not contain a span (it is different and does not contain ':')
            if p_element and not p_element.find_elements(By.TAG_NAME, 'span'):
                label = p_element.text.split(': ')[0]
                value = p_element.text.split(': ')[1]
                car_details[label] = value

        # Create car object
        car = Car(
            link=driver.current_url,
            brand=brand_element[1].text.strip() if len(brand_element) > 0 else None,
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
            price_pln=int(price_element.text.strip().replace(' ', '').replace('zł', '')) if price_element else None,
            location=location
        )

        # Set the state of the car based on mileage
        if car.mileage < 500:
            car.state = 'Nowy'
        else:
            car.state = 'Używany'

        car_repo.add_car_if_not_exists(car)  # Add car to the database

    except Exception as e:
        print(f'Encountered a problem while extracting car data from the page {driver.current_url}, error message: {e}')


def set_missing_locations() -> None:
    """
    Method needed after db update (Added location row to Car table)
    :return: None
    """
    cars = car_repo.get_all_cars()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    for car in cars[15531:]:
        try:
            driver.get(car.link)

            print(f'Updating the location for car with id {car.id}...')
            # Check if page is otomoto or olx
            if str(Page.otomoto_url.value) in car.link:
                location_element = driver.find_elements(By.XPATH, '//a[@class="edhv9y51 ooa-oxkwx3"]')
                location_element = [element for element in location_element
                                    if 'Przejdź do' not in element.text and 'Zobacz więcej' not in element.text]
                car.location = (location_element[0].text.strip() if len(location_element) > 0 else '')
            elif str(Page.olx.value) in car.link:
                # Wait for location element to be present
                location_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//p[@class="css-1cju8pu er34gjf0"]'))
                )
                # Wait for region elements to be present
                region_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//p[@class="css-b5m1rv er34gjf0"]'))
                )
                car.location = ''
                if location_element:
                    car.location += location_element.text.strip()
                    if car.location.endswith(','):
                        car.location = car.location[:-1]
                if region_element:
                    if region_element[-1] != 'Więcej od tego ogłoszeniodawcy':
                        car.location += ' - ' + region_element[-1].text.strip()
            else:
                continue
            print(car.location)
            car_repo.update_car(car)
        except Exception as e:
            print(f'Encountered problem on the page {car.link}, error message: {e}\n')
            driver.quit()  # Close the browser
            driver = webdriver.Chrome(options=chrome_options)
            continue

        print(f'    Delay after car at link {car.link}...\n')
        time.sleep(random.uniform(1.0, 1.5))  # Wait some time delay to mimic human behavior
