

def main():
    from car_scraping.scraper import scrape_n_pages
    from car_scraping.analizer import get_brands_with_best_price
    # scrape_n_pages(750, None, 278)
    # Analyze the repository
    get_brands_with_best_price('skoda', ['octavia'], 2018, 2025,
                               0, 250000, ['benzyna'], ['automat'], '')


if __name__ == '__main__':
    main()
