# uscis-case-statistics

This project can query a range of case numbers and save results to MongoDB. 

You can resigter a MongoDB Atlas account which will give you a free 512MB storage. After you create the MongoDB Atlas, please update the `mongo.py` under the `config` folder so that the daily results can be saved into your MongoDB. 

Furthermore, you can create an AWS account and deploy the code to a lambda function, set up a cron job and run the scrawler job overnight. 
