from libs.uscis.client import USCISStatusFetcher
from libs.utils.decorators import timer

CASE_TYPE = 'I-539'
SERVICE_CENTER = 'LIN'
FISCAL_YEAR = '20'
WORK_DAYS = list(range(260, 290))
CASE_NUMBERS = list(range(50000, 51200, 1))


@timer
def main():
    uscis_fetcher = USCISStatusFetcher(batch_size=1000, save_locally=False)
    uscis_fetcher.query(CASE_TYPE, SERVICE_CENTER, FISCAL_YEAR, WORK_DAYS, CASE_NUMBERS)


main()

