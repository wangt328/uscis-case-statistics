from libs.uscis.client import USCISStatusFetcher


def main():
    uscis_fetcher = USCISStatusFetcher(save_to_mongodb=True)
    uscis_fetcher.query('LIN', 'I-539', list(range(20240, 20285)), 1000)


main()

