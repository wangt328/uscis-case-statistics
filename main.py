from libs.uscis.client import USCISStatusFetcher

CASE_TYPE = 'I-539'
SERVICE_CENTER = 'LIN'
FISCAL_YEAR = '20'
WORK_DAYS = list(range(280, 300))
CASE_NUMBERS = list(range(50000, 51000, 2))


def main():
    uscis_fetcher = USCISStatusFetcher(batch_size=500, save_locally=True)
    uscis_fetcher.query(CASE_TYPE, SERVICE_CENTER, FISCAL_YEAR, WORK_DAYS, CASE_NUMBERS)


main()
