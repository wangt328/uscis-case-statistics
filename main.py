from libs.uscis.client import USCISStatusFetcher


def main():
    uscis_fetcher = USCISStatusFetcher(batch_size=1000, save_locally=True)  # batch_size should be smaller than 1000
    uscis_fetcher.query('I-539', 'LIN', '20', list(range(268, 269)), list(range(50000, 50500, 1)))


main()
