import asyncio
import re
import time
from datetime import datetime
from typing import Dict, Union, Any, Optional, List

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from pandas import Timestamp
from pymongo import UpdateOne

from libs.mongodb.client import MongoDatabase
from libs.utils import batch

CASE_DATE_PATTERN = r'[(A-Za-z)]*\s[\d]*,\s[\d]*'
CASE_STATUS_PATTERN = r'\: (.*?) \+'
HEADERS = {
    'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/45.0.2454.101 Safari/537.36'),
}


class USCISStatusFetcher(object):
    def __init__(self):
        self._collection = MongoDatabase('uscis')['case_history']
        self._approved_case_nums = self.__get_approved_case_numbers()

    def __get_approved_case_numbers(self):
        """
        Cache the case numbers that have been approved already
        """
        query = {'status': {'$eq': 'Case Was Approved'}}
        curse = self._collection.find(query, {'_id': False})
        return set(x['case_number'] for x in curse)

    def __write_to_mongo(self, data: List):
        """
        Write the query result into MongoDB collection
        """
        db_writes = []
        for item in data:
            update_filter = {'case_number': item['case_number']}
            update = {'$set': {k: v for k, v in item.items() if v is not None}}
            update_one = UpdateOne(update_filter, update, upsert=True)
            db_writes.append(update_one)
        if db_writes:
            self._collection.bulk_write(db_writes)

    def __get_case_numbers(self,
                           service_center: str,
                           fiscal_year: str,
                           sampling_work_days: List[int],
                           sampling_case_nums: List[int]
                           ) -> List[str]:
        case_numbers = [
            service_center + fiscal_year + str(x) + str(y) for x in sampling_work_days for y in sampling_case_nums]

        return list(filter(lambda x: x not in self._approved_case_nums, case_numbers))

    def query(self,
              case_type: str,
              service_center: str,
              fiscal_year: str,
              sampling_work_days: List[int],
              sampling_case_nums: List[int]) -> None:
        """
        Query the case status within the range and dates and save the result to the MongoDB

        Args:
            service_center: three characters that stands for the USCIS processing center. For example, LIN, EAC, etc
            fiscal_year: fiscal year as string, '20' for 2020
            case_type: form type like 'I-539', 'I-765', etc
            sampling_work_days: list of receive dates that we want to query
            sampling_case_nums: list of case processing numbers to query
        """
        case_numbers = self.__get_case_numbers(service_center, fiscal_year, sampling_work_days, sampling_case_nums)

        batch_id = 1

        for shard in batch(case_numbers, 10):
            print('-' * 10 + ' Processing Batch {} '.format(batch_id) + '-' * 10)
            loop = asyncio.get_event_loop()

            result = loop.run_until_complete(
                asyncio.gather(
                    *(self.get_case_status(x, case_type) for x in shard)
                )
            )

            filtered_result = [x for x in result if x is not None]

            print('Successfully query {} results...'.format(len(filtered_result)))

            self.__write_to_mongo(filtered_result)
            time.sleep(5)
            batch_id += 1

        cursor = self._collection.find()
        df = pd.DataFrame(list(cursor))
        df.to_csv('df_{}.csv'.format(datetime.now().strftime("%Y_%m_%d")))

    @staticmethod
    async def get_case_status(case_num: str, case_type: str) -> Optional[Dict[str, Union[str, Any]]]:
        """
        Query the status of a single case

        Args:
            case_num: case number to be queried.
            case_type: case type to be checked. If the case is not the type specified by input case_type, return None
        """

        data = {
            'appReceiptNum': case_num,
            'caseStatusSearchBtn': 'CHECK STATUS'
        }

        url = 'https://egov.uscis.gov/casestatus/mycasestatus.do'

        print('Query case: ' + case_num)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, params=data) as resp:
                data = await resp.text()

        soup = BeautifulSoup(data, 'lxml')
        status_message = soup.find('div', 'rows text-center').text

        if case_type not in status_message:
            return None

        p = re.search(CASE_DATE_PATTERN, status_message)
        if p is not None:
            match = p.group(0)
            last_update_date = datetime.strptime(str(match), '%B %d, %Y')
            last_update_date = last_update_date.strftime('%m/%d/%Y')
        else:
            last_update_date = datetime.min

        status_title = soup.find('div', {'class': 'current-status-sec'})
        status_message = ' '.join(status_title.text.split())

        p = re.search(CASE_STATUS_PATTERN, status_message)
        if p is None:
            status = 'No result is available'
        else:
            status = p.group(1)

        return {'case_number': case_num,
                'case_type': case_type,
                'status': status,
                'as_of_date': last_update_date,
                'last_updated_time': Timestamp.now(tz='UTC')}
