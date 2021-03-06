import asyncio
import re
import time
from datetime import datetime
from typing import Dict, Union, Any, Optional, List

import aiohttp
import lxml.html
import pandas as pd
from pandas import Timestamp
from pymongo import UpdateOne

from libs.mongodb.client import MongoDatabase
from libs.utils import batch

CASE_DATE_PATTERN = r'[(A-Za-z)]*\s[\d]*,\s[\d]*'
CASE_TYPE_PATTERN = r'I-\d{3}'
HEADERS = {
    'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/45.0.2454.101 Safari/537.36'),
}


class USCISStatusFetcher(object):
    def __init__(self, batch_size: int = 500, save_locally: bool = False):
        """
        Args:
            batch_size: size of batch in the async query
            save_locally: save final results into a local csv file
        """
        self._save_locally = save_locally

        if not save_locally:
            # make sure you have a mongo collection called "uscis". Update the collection name if needed.
            self._collection = MongoDatabase('uscis')['case_history']
            self._approved_case_nums = self.__get_approved_case_numbers()
        else:
            self._collection = None
            self._approved_case_nums = set()

        self._batch_size = batch_size

    def __get_approved_case_numbers(self):
        """
        Cache the case numbers that have been approved already
        """
        query = {'status': {'$eq': 'Case Was Approved'}}
        curse = self._collection.find(query, {'_id': False})
        return set(x['caseNumber'] for x in curse)

    def __write_to_mongo(self, data: List):
        """
        Write the query result into MongoDB collection
        """
        db_writes = []
        for item in data:
            update_filter = {'caseNumber': item['caseNumber']}
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
              service_center: str,
              fiscal_year: str,
              sampling_work_days: List[int],
              sampling_case_nums: List[int],
              filter_on_case_type: Optional[str]) -> None:
        """
        Query the case status within the range and dates and save the result to the MongoDB

        Args:
            service_center: three characters that stands for the USCIS processing center. For example, LIN, EAC, etc
            fiscal_year: fiscal year as string, '20' for 2020
            filter_on_case_type: form type like 'I-539', 'I-765', etc
            sampling_work_days: list of receive dates that we want to query
            sampling_case_nums: list of case processing numbers to query
        """
        case_numbers = self.__get_case_numbers(service_center, fiscal_year, sampling_work_days, sampling_case_nums)

        batch_id = 1
        cumulative_result = []

        loop = asyncio.get_event_loop()
        for shard in batch(case_numbers, self._batch_size):
            print(f'[INFO] Processing Batch {batch_id}')

            filtered_result = loop.run_until_complete(self.__fetch_all(shard))

            if self._save_locally:
                cumulative_result.extend(filtered_result)
            else:
                self.__write_to_mongo(filtered_result)

            time.sleep(2)
            batch_id += 1

        if self._save_locally:
            df = pd.DataFrame(cumulative_result)
        else:
            cursor = self._collection.find()
            df = pd.DataFrame(list(cursor))

        if filter_on_case_type is not None:
            df = df[df['caseType'] == filter_on_case_type]
            print(f'[INFO] Filtered the result to {filter_on_case_type} only')

        df.to_csv('{}.csv'.format(datetime.now().strftime("%Y_%m_%d")))
        loop.close()

    @classmethod
    async def __fetch_all(cls, case_batch: List[str]):
        """
        Query the status of a batch

        Args:
            case_batch: a batch of case numbers
        """
        # conn = aiohttp.TCPConnector(
        #     ttl_dns_cache=300,
        #     verify_ssl=False,
        #     limit=0)

        async with aiohttp.ClientSession() as session:
            result = await asyncio.gather(
                *[cls.fetch(session, x) for x in case_batch]
            )

            filtered_result = [x for x in result if x is not None]

            print(f'[INFO] Successfully query {len(filtered_result)} results')

            return filtered_result

    @staticmethod
    async def fetch(session: aiohttp.ClientSession, case_num: str) -> Optional[Dict[str, Union[str, Any]]]:
        """
        Query the status of a single case

        Args:
            session: aio http client session
            case_num: case number to be queried.
        """

        data = {
            'appReceiptNum': case_num,
            'caseStatusSearchBtn': 'CHECK STATUS'
        }

        url = 'https://egov.uscis.gov/casestatus/mycasestatus.do'

        # print('Query case: ' + case_num)

        async with session.get(url, headers=HEADERS, params=data, verify_ssl=False) as resp:
            data = await resp.text()

        selector = lxml.html.fromstring(data)

        # if the status title is empty, the receipt number is not valid
        try:
            status_title = selector.xpath('//div[@class="rows text-center"]/h1/text()')[0]
        except IndexError:
            return None

        status_message = selector.xpath('//div[@class="rows text-center"]/p/text()')[0]

        p = re.search(CASE_TYPE_PATTERN, status_message)

        if p is None:
            return None
        else:
            case_type = p.group(0)

        p = re.search(CASE_DATE_PATTERN, status_message)
        if p is not None:
            match = p.group(0)
            last_update_date = datetime.strptime(str(match), '%B %d, %Y')
        else:
            last_update_date = datetime.min

        return {'caseNumber': case_num,
                'workDay': int(case_num[5:8]),
                'caseType': case_type,
                'status': status_title,
                'effectiveDate': last_update_date,
                'lastUpdateTime': Timestamp.now(tz='UTC')}
