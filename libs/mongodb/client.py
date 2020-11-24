import pymongo
from pymongo import database
from config.mongodb import config


class MongoDatabase(object):
    """
    This class returns a database object, not a mongo client. 
    In order to access the client, use the syntax: `database.client`
    """
  
    def __new__(cls, db: str, *arg, **kwargs) -> pymongo.database:
        url = 'mongodb+srv://{}:{}@dev.ba3z7.mongodb.net/test?retryWrites=true&w=majority'  # @dev.ba3z7.mongodb.net should be updated to yours accordingly 
        client = pymongo.MongoClient(
            url.format(config.get('username'), config.get('password'))
        )
        return client[db]
