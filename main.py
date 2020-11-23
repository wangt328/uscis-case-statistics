from libs.uscis.client import USCISStatusFetcher


def main():
    uscis_fetcher = USCISStatusFetcher()
    uscis_fetcher.query('I-539', 'LIN', '20', list(range(280, 300)), list(range(50000, 51000, 2)))


main()
