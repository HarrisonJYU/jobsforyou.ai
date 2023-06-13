from datetime import date, datetime, timedelta
import json
import requests
import urllib
from user_definition import *

from google.cloud import storage
# def retreive_api_data(noaa_token, api_url):
#     head = {'token':f'{noaa_token}'}
#     response = requests.get(api_url, headers=head)
#     return response.json()

# def filter_history_data(data, three_days_ago):
#     return [x for x in data['results'] if datetime.strptime(x['date'], '%Y-%m-%dT%H:%M:%S').date() == three_days_ago]

def write_json_to_gcs(bucket_name, blob_name, service_account_key_file, data):
    """Write and read a blob from GCS using file-like IO"""
    storage_client = storage.Client.from_service_account_json(service_account_key_file)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    with blob.open("w") as f:
        json.dump(data, f)

def get_jobs():
    url = "https://jsearch.p.rapidapi.com/search"
    all_jobs = dict()

    querystring = {"query":query,'page':1,"num_pages":1}
    headers = {
    "X-RapidAPI-Key": x_rapidapi_key,
    "X-RapidAPI-Host": x_rapidapi_host}

    response = requests.request("GET", url, headers=headers, params=querystring)
    json_jobs = json.loads(response.text)
    try:
        for job in json_jobs['data']:
            job_id = job['job_id']
            if job_id in all_jobs:
                all_jobs[job_id].append(job)
            else:
                all_jobs[job_id] = [job]
    except:
        pass
    return all_jobs

def get_jobs_seo():
    headers = {
        "X-RapidAPI-Key": x_rapidapi_key_seo,
        "X-RapidAPI-Host": x_rapidapi_host_seo
    }
    seo_jobs = dict()
    resp = requests.get("https://seo-api.p.rapidapi.com/v1/job/search/" + urllib.parse.urlencode(query_seo), headers=headers)
    results = resp.json()
    try:
        for i in results['jobs']:
            seo_jobs[i['link']] = i
    except:
        pass
    return seo_jobs

