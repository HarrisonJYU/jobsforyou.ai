from MongoClient import MongoDBCollection
import requests
from tqdm import tqdm


# api_url = "http://127.0.0.1:5000"


# mongo_username = "mongoadmin"
# mongo_password = "pDru4hbGjnIGRCmm"
# mongo_ip_address = "cluster0.inorscz.mongodb.net"
# database_name = "msds697"
# collection_name = "job_postings"
from user_definition import *


mon = MongoDBCollection(mongo_username, 
                                mongo_password,
                                mongo_ip_address,
                                database_name,
                                collection_name)

curs = mon.collection.find()
data = list(curs)

keys = ['job_title','job_description', 'employer_name',
        'job_required_skills']

cleaned = []
max_token_len = 512
lesser, ids = [], []

for idx, doc in enumerate(data):
    id = doc['_id']
    total_doc = ''
    for key in keys:
        if key in doc:
            if isinstance(doc[key], dict):
                for k in doc[key]:
                    total_doc += doc[key][k] + " "
            if isinstance(doc[key], str):
                total_doc += str(doc[key]) + ' '

    if len(total_doc.split()) < 20:
        lesser.append(idx)
        continue
    ids.append(str(id))
    cleaned.append(total_doc)

for i in tqdm(range(len(cleaned))):
    text = cleaned[i]
    ID = ids[i]
    URL = ''

    # Call /embed_and_store API
    embed_and_store_url = f"{api_url}/embed_and_store"
    response = requests.post(embed_and_store_url, json={"text": text, "ID": ID, "URL": URL})

