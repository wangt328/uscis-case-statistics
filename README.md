This chunk of code can query a range of case numbers and save results to MongoDB or locally. Before running the code, it is good to have:

- MongoDB Atlas account. You can resigter a MongoDB Atlas account which will give you a free 512MB storage. After you create the MongoDB Atlas, please update the `mongodb.py` under the `config` folder so that the daily results can be saved into your MongoDB. 
- (Optional) AWS account. Furthermore, you can create an AWS account and deploy the code to a lambda function, set up a cron job and run the scrawler job overnight. 


## How to Use
You can folk the repo and run the `main.py` in any PyCharm. You need to update `CASE_TYPE`, `SERVICE_CENTER`, `FISCAL_YEAR` and other variables as needed.

```python
CASE_TYPE = 'I-539'
SERVICE_CENTER = 'LIN'
FISCAL_YEAR = '20'
WORK_DAYS = list(range(280, 300))
CASE_NUMBERS = list(range(50000, 51000, 2))


def main():
    uscis_fetcher = USCISStatusFetcher(batch_size=500, save_locally=False)
    uscis_fetcher.query(CASE_TYPE, SERVICE_CENTER, FISCAL_YEAR, WORK_DAYS, CASE_NUMBERS)


main()
```
If `save_locally` is set to `True`, the query result will be saved as a `.csv` file locally. Otherwise, the results will be upserted into the MongoDB Atlas ans save all the data in the collection into a `.csv` file locally.
