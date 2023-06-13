import json
from flask import Flask, request, jsonify
from LLM import Embedding
import pinecone
from resumeParser import ResumeParser
from user_definition import *
from MongoClient import *

app = Flask(__name__)

#Resume Parser
rs = ResumeParser()

# Initialize the sentence transformer model
model = Embedding()

# Initialize Pinecone
pinecone.init(api_key = "fb0405aa-3107-4845-bc12-eb768ddf345c",
              environment = "us-west1-gcp")

pinecone_index = pinecone.Index("msds697")
pinecone_namespace = "sentence_embeddings"
mon=MongoDBCollection(mongo_username, 
                                mongo_password,
                                mongo_ip_address,
                                database_name,
                                collection_name)
job_data=[]
for rec in mon.find({},{'job_title':True,'employer_name':True}):
    job_data.append((set((rec['job_title'].lower().strip()+' '+rec['employer_name'].lower().strip()).split()),rec['_id']))    


@app.route('/embed_and_store', methods=['POST'])
def embed_and_store():
    print('Received API call')
    text = request.json['text']
    ID = request.json['ID']
    URL = request.json['URL']
    embedding = model.get_embedding(text)
    metadata = {'url': URL}
    pinecone_index.upsert(vectors=[{'id':ID, 
                                    'values':embedding, 
                                    'metadata':metadata}],
                           namespace = pinecone_namespace)
    return jsonify({"success": True})

@app.route('/find_closest_match', methods=['POST'])
def find_closest_match():
    print('received API call')
    pdf_path = request.json['path']
    embed_string = rs.construct_embed_string(pdf_path)
    query_embedding = model.get_embedding(embed_string)
    results = pinecone_index.query(vector=query_embedding, 
                                   top_k=15,
                                   include_values=False,
                                   include_metadata=True,
                                   namespace=pinecone_namespace)
    
    
    results = results.to_dict()['matches']
    results = [{i: d[i] for i in d if i!='values'} for d in results]
    print(results)
    return jsonify(results)

@app.route('/search', methods=['POST'])
def search():
    print('received API call')
    request_text = request.data.decode('ascii')
    request_text=request_text.lower().strip().split()
    output=[]
    for job in job_data:
        score=len(job[0].intersection(request_text))
        output.append((score,str(job[1])))
    output.sort(key=lambda x:x[0],reverse=True)
    output=[job[1] for job in output[:15]]
#     embed_string = rs.construct_embed_string(pdf_path)
#     query_embedding = model.get_embedding(embed_string)
#     results = pinecone_index.query(vector=query_embedding, 
#                                    top_k=15,
#                                    include_values=False,
#                                    include_metadata=True,
#                                    namespace=pinecone_namespace)
    
    
#     results = results.to_dict()['matches']
#     results = [{i: d[i] for i in d if i!='values'} for d in results]
    return jsonify({"job_ids": output})

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True)