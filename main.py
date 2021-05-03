from libs.uscis.client import USCISStatusFetcher

CASE_TYPE = 'I-129'
SERVICE_CENTER = 'WAC'
FISCAL_YEAR = '21'
WORK_DAYS = list(range(200, 211))
CASE_NUMBERS = list(range(50000, 51200, 1))


def main():
    uscis_fetcher = USCISStatusFetcher(batch_size=1000, save_locally=False)
    uscis_fetcher.query(SERVICE_CENTER, FISCAL_YEAR, WORK_DAYS, CASE_NUMBERS, filter_on_case_type=CASE_TYPE)


main()
