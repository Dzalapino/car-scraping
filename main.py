

def main():
    from car_scraping.scraper import scrape_n_pages, Page
    from car_scraping.analizer import get_brands_with_best_price

    # Scrape the cars
    scrape_n_pages(Page.olx_url, 25, 1, 3.0, 5., True)
    scrape_n_pages(Page.otomoto_url, 1000, 1, 3.0, 5., True)
    # Analyze the repository
    # get_brands_with_best_price('bmw', [''], 2006, 2006,
    #                            0, 300000, ['benzyna', 'petrol'], ['manual'], '')


if __name__ == '__main__':
    main()
