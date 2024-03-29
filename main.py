def main():
    from car_scraping.scraper import scrape_n_pages, Page
    from car_scraping.brand_analizer import get_brands_with_best_price
    from car_scraping.data_analizer import analise_data
    from car_scraping.scraper import set_missing_locations

    # Scrape the cars
    # scrape_n_pages(Page.olx_url, 10, 1, 1.0, 2.0, True)
    # scrape_n_pages(Page.otomoto_url, 20, 1, 1.0, 2.0, True)

    # Analyze the repository
    # analise_data(True)

    # Analyze given brand with best prices
    get_brands_with_best_price('bmw', [''], 2006, 2024,
                               0, 300000, [], [], '', ['Łódzkie'])

    # set_missing_locations()


if __name__ == '__main__':
    main()
