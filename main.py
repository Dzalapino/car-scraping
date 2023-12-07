

def main():
    from car_scraping.scraper import scrape_n_pages
    for car in scrape_n_pages(1):
        print(car)


if __name__ == '__main__':
    main()
