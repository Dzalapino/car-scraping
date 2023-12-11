from unidecode import unidecode


def extract_numbers_from_string(string: str) -> int:  # Remove all characters except digits
    numbers = ''.join(filter(str.isdigit, string))
    return int(numbers) if numbers else None


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


def format_brand(brand: str) -> str:
    """

    :param brand:
    :return:
    """
    mapping = {
        'alfa': 'alfa-romeo',
        'aston': 'aston-martin',
        'land': 'land-rover',
        'warszawa': 'marka_warszawa',
        'rolls': 'rolls-royce'
    }
    return mapping.get(brand, brand)


def get_brand_from_full_name(full_name: str) -> str:
    """

    :param full_name:
    :return:
    """
    brand = unidecode(full_name.split(' ')[0].lower())
    return format_brand(brand)
