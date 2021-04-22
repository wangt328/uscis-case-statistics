This chunk of code can query a range of case numbers and save results to MongoDB or locally. Before running the code, it is good to have:

- MongoDB Atlas account (optional). You can [resigter](https://www.mongodb.com/cloud/atlas) a MongoDB Atlas account which will give you a free 512MB storage. After you create the MongoDB Atlas, please update the `mongodb.py` under the `config` folder so that the daily results can be saved into your MongoDB. 

You can also run the code and save result locally without the MongoDB Atlas account by setting `save_locally=True`.

## How to Use
You can clone the repo to your local.

First change directory to the folder where the code is downloaded. Run `pip install -r requirements.txt` to install all the required packages and run the `main.py` file. You need to update `CASE_TYPE`, `SERVICE_CENTER`, `FISCAL_YEAR` and other variables as needed.

```python
# Assume your receipt number is LIN2028551101, then
# your fiscal_year is 20, work day is 285 and case number is 51101.

CASE_TYPE = 'I-539'
SERVICE_CENTER = 'LIN'
FISCAL_YEAR = '20'
WORK_DAYS = list(range(280, 301))           # change it to the work day range you want to query
CASE_NUMBERS = list(range(50000, 51001, 1)) # change it to the case number range you want to query. 

# above setting will do the query for all the case numbers between 50000 and 51000 for work days from 280 to 299.

def main():
    uscis_fetcher = USCISStatusFetcher(batch_size=500, save_locally=True)
    uscis_fetcher.query(CASE_TYPE, SERVICE_CENTER, FISCAL_YEAR, WORK_DAYS, CASE_NUMBERS)


main()
```
If `save_locally` is set to `True`, the query result will be saved as a `.csv` file locally. Otherwise, the results will be upserted into the MongoDB Atlas ans save all the data in the collection into a `.csv` file locally.
