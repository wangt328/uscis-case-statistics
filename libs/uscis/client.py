import re
from datetime import datetime
from typing import Dict, Union, Any, Optional, List
import time
import requests
from bs4 import BeautifulSoup
from pandas import Timestamp
from pymongo import UpdateOne

from libs.mongodb.client import MongoDatabase

CASE_DATE_PATTERN = r'[(A-Za-z)]*\s[\d]*,\s[\d]*'
CASE_STATUS_PATTERN = r'\: (.*?) \+'


class USCISStatusFetcher(object):
    def __init__(self):
        self._collection = MongoDatabase('uscis')['case_history']
        self._approved_case_nums = self.__get_approved_case_numbers()

    def __get_approved_case_numbers(self):
        query = {'status': {'$eq': 'Case Was Approved'}}
        curse = self._collection.find(query, {'_id': False})
        return set(x['case_number'] for x in curse)

    def __write_to_mongo(self, data: List):
        db_writes = []
        for item in data:
            update_filter = {'case_number': item['case_number']}
            update = {'$set': {k: v for k, v in item.items() if v is not None}}
            update_one = UpdateOne(update_filter, update, upsert=True)
            db_writes.append(update_one)
        if db_writes:
            self._collection.bulk_write(db_writes)

    def query(self,
              service_center: str,
              case_type: str,
              sampling_dates: List[int],
              sampling_range: int) -> None:

        for i in sampling_dates:
            result = []
            for j in range(sampling_range):
                case_number = service_center + str(i) + str(50000 + j)
                if case_number in self._approved_case_nums:
                    continue

                print('Query ' + case_number)
                case_status = self.get_case_status(case_number, case_type)
                if case_status:
                    result.append(case_status)
            self.__write_to_mongo(result)
            time.sleep(60)

    @staticmethod
    def get_case_status(case_num: str, case_type: str) -> Optional[Dict[str, Union[str, Any]]]:
        data = {
            'appReceiptNum': case_num,
            'caseStatusSearchBtn': 'CHECK STATUS'
        }

        response = requests.post('https://egov.uscis.gov/casestatus/mycasestatus.do', data=data)

        soup = BeautifulSoup(response.text, 'lxml')
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
