from libs.uscis.client import USCISStatusFetcher


def main():
    uscis_fetcher = USCISStatusFetcher()
    uscis_fetcher.query('LIN', 'I-539', list(range(20240, 20241)), 10)


main()

