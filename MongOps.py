from pymongo import MongoClient


def connect(db, collection, host='localhost', port=27017):

    client = MongoClient(host, port)
    db = client.get_database(db)
    collection = db.get_collection(collection)

    return collection


def clear_db(db='advisor', collection='companies'):

    collection = connect(db, collection)
    collection.delete_many({})

