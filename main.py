

def main():
    from car_scraping.scraper import scrape_n_pages
    from car_scraping.analizer import get_cars_with_best_price
    # Analyze the repository
    # scrape_n_pages(6)
    get_cars_with_best_price('skoda', 'fabia')


if __name__ == '__main__':
    main()
