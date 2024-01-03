

def main():
    from car_scraping.scraper import scrape_n_pages
    from car_scraping.analizer import get_brands_with_best_price
    # scrape_n_pages(750, None, 278)
    # Analyze the repository
    get_brands_with_best_price('skoda', 'fabia', 2010, 2020,
                               0, 200000, 'benzyna', 'manualna')


if __name__ == '__main__':
    main()
