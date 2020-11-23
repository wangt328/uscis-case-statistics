from libs.uscis.client import USCISStatusFetcher


def main():
    uscis_fetcher = USCISStatusFetcher(batch_size=1000)  # batch_size should be smaller than 1000
    uscis_fetcher.query('I-539', 'LIN', '20', list(range(220, 300)), list(range(50000, 51010, 2)))


main()
