import json

from google.cloud import storage
from mongodb import *
from pyspark.sql import Row, SparkSession
import pyspark

from user_definition import *

sc = pyspark.SparkContext()

def retreive_law_enforcement_data(spark, bucket_name, date):
    law_enforcement = (
        spark.read.format("csv")
        .option("header", True)
        .load(f"gs://{bucket_name}/{date}/gnap-fj3t.csv")
    )
    return law_enforcement


def return_json(service_account_key_file,
                bucket_name,
                blob_name):
    storage_client = storage.Client.from_service_account_json(service_account_key_file)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    json_str = blob.download_as_string().decode("utf8")
    json_data = json.loads(json_str)
    return json_data

def add_json_data_to_rdd(rdd, json_data, json_field_name):
    rdd_dict = rdd.asDict()
    rdd_dict[json_field_name] = json_data
    id = rdd_dict['id']
    rdd_dict['_id'] = id
    rdd_dict.pop('id', None)
    
    return rdd_dict

def filter_fields(ip_json):
    keys = list(ip_json.keys())
    final_list = []
    for k in keys:
        job_j = ip_json[k][0]
        filtered_dict = {}
        filtered_dict['job_id'] = job_j['job_id']
        filtered_dict['job_title'] = job_j['job_title']
        filtered_dict['job_description'] = job_j['job_description']
        filtered_dict['employer_name'] = job_j['employer_name']
        filtered_dict['job_required_skills'] = job_j['job_required_skills']
        filtered_dict['job_salary_currency'] = job_j['job_salary_currency']
        filtered_dict['job_highlights'] = job_j['job_highlights']
        final_list.append(filtered_dict)
    return final_list

def filter_fields_seo(ip_json):
    keys = list(ip_json.keys())
    final_list = []
    for k in keys:
        job_j = ip_json[k]
        filtered_dict = {}
        # filtered_dict['job_id'] = job_j['job_id']
        filtered_dict['job_title'] = job_j['position']
        filtered_dict['job_description'] = job_j['description']
        filtered_dict['employer_name'] = job_j['employer']
        # filtered_dict['job_required_skills'] = job_j['job_required_skills']
        # filtered_dict['job_salary_currency'] = job_j['job_salary_currency']
        filtered_dict['job_highlights'] = job_j['highlights']
        final_list.append(filtered_dict)
    return final_list

def insert_aggregates_to_mongo():
    spark = SparkSession.builder.getOrCreate()
    conf = spark.sparkContext._jsc.hadoopConfiguration()
    conf.set("google.cloud.auth.service.account.json.keyfile", service_account_key_file)
    conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    conf.set("fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")

    #First data source
    jobs_data_path = f'{today}/jobs.json'
    jobs_json = return_json(service_account_key_file,
                               bucket_name,
                               jobs_data_path)
    jobs_rdd = sc.parallelize([jobs_json])
    jobs_aggregate = jobs_rdd.map(lambda x:filter_fields(x))
    jobs_filtered_list =jobs_aggregate.collect()[0]
    
    #second data source
    jobs_seo_data_path = f'{today}/jobs_seo.json'
    jobs_seo_json = return_json(service_account_key_file,
                               bucket_name,
                               jobs_seo_data_path)
    jobs_seo_rdd = sc.parallelize([jobs_seo_json])
    jobs_seo_aggregate = jobs_seo_rdd.map(lambda x:filter_fields_seo(x))
    jobs_seo_filtered_list =jobs_seo_aggregate.collect()[0]


    mongodb = MongoDBCollection(mongo_username,
                                mongo_password,
                                mongo_ip_address,
                                database_name,
                                collection_name)

    for aggregate in jobs_filtered_list:
        mongodb.insert_one(aggregate)
    
    for aggregate in jobs_seo_filtered_list:
        mongodb.insert_one(aggregate)

if __name__=="__main__":
    insert_aggregates_to_mongo()
    sc.stop()
