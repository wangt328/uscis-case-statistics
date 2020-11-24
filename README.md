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


## Explaination: USCIS Receipt Number (LIN, SRC, EAC, WAC, IOE)
The USCIS receipt or case number is one of the most commonly used numbers, by immigrants and lawyers alike, to track the progress or identify a particular immigration case or filing.

These receipt numbers start with three letters followed by a series of numbers, for example `EAC-15-123-45678`.  Here is how to understand what the numbers mean.

### Processing Service Center

The first three letters indicate the USCIS service center which is processing the petition, as follows:

```
- EAC: Vermont Service Center
- VSC: Vermont Service Center
- WAC: California Service Center
- CSC: California Service Center
- LIN: Nebraska Service Center
- NSC: Nebraska Service Center
- SRC: Texas Service Center
- TSC: Texas Service Center
- MSC: National Benefits Center
- NBC: National Benefits Center
- IOE: ELIS (e-Filing)
- YSC: Potomac Service Center
```

### Fiscal Year
The next two digits represent the fiscal year in which USCIS received the petition.  In the example above, “15″ means that the petition was received by USCIS during Fiscal Year 2015.   Note that the government fiscal year runs from October 1st until September 30th.

### Computer Workday
The next three digits represent the computer workday on which the receipt was processed and the fee was taken. This represents the sequential workday on which USCIS is accepting cases for intake. In the example above, 123 would indicate that this was the 123th processing date of the fiscal year. If necessary, a date of filing can be calculated starting from October 1st.

### Case Processing Number
Finally, the last five digits are used to identify uniquely the petition filed. Our observation has been that these are sequential numbers which are issued as cases are being processed at the intake facility. Cases filed together are often given sequential (or close to sequential) numbers for the last five digits (and overall).
