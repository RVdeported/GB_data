# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 15:46:15 2021

@author: Roman
"""
from pymongo import MongoClient
from pprint import pprint
import json

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "posts"
MONGO_COLLECTION = "jobs_posts"

def print_mongo_docs(cursor):
    for doc in cursor:
        pprint(doc)

def load_jobs_data(fp):
    with open(fp, 'r') as f:
        job_data = json.load(f)
    with MongoClient(MONGO_HOST, MONGO_PORT) as client:
        db = client[MONGO_DB]
        jobs =db[MONGO_COLLECTION]
        for n in job_data:
            jobs.update_many(n,
                             {'$set':n}, True)
        
    
def load_print_mongo(params):
    with MongoClient(MONGO_HOST, MONGO_PORT) as client:
        db = client[MONGO_DB]
        jobs =db[MONGO_COLLECTION]
        
        cursor = jobs.find(params)
        print_mongo_docs(cursor)
        
def load_high_jobs(salary):
    load_print_mongo({
            'min_sal': {"$gt" : salary}
            })    

def load_nosalary_jobs():
    load_print_mongo({
            'min_sal': "Not stated",
            'max_sal': "Not stated"
            })

if __name__ == "__main__":
    load_jobs_data("./jobs.json")
    load_nosalary_jobs()