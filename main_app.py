import streamlit as st
import PyPDF2 
from PIL import Image
from user_definition import *
from MongoClient import *
from MongoClient import *
import requests
import os

def main():
    mon = MongoDBCollection(mongo_username, 
                                mongo_password,
                                mongo_ip_address,
                                database_name,
                                collection_name)
    st.set_page_config(page_title='My Streamlit Page', page_icon=':sunglasses:', layout='wide', initial_sidebar_state='auto')
    logo = Image.open('assets/logo.png')
    width, height = logo.size
    logo = logo.resize((width//2, height//2))
    st.image(logo) #,use_column_width='always')
    # st.title("_:blue[JobsForYou]_")
    st.header("Job Listings")

    # Add search functionality and upload button
    query = st.text_input("Search for jobs:")
    uploaded_file = st.file_uploader("Upload your resume in PDF format:", type=["pdf"])
    # If file is uploaded, print absolute file path
    if not os.path.exists('uploaded_resumes'):
        os.makedirs('uploaded_resumes')
    if uploaded_file:
        file_path = os.path.abspath('uploaded_resumes/'+uploaded_file.name)
        with open(file_path,'wb') as f:
            f.write(uploaded_file.read())
        st.success(f"File uploaded: {uploaded_file.name}")
        #call api
        with st.spinner(text="In progress..."):
            find_closest_match_url=f"{api_url}/find_closest_match"
            recom_job_ids = requests.post(find_closest_match_url, json={'path':file_path}).json()
            recom_job_objids = [ObjectId(job_id['id']) for job_id in recom_job_ids]
            st.header("Recommended Job Listings")
            recom_jobs=list(mon.find({'_id':{'$in':recom_job_objids}},{'_id':False}))
        show_jobs(recom_jobs)
        
        # for job_description in jds:
        #     st.write(f"## Job Description")
        #     st.write(f"{job_description}")
        #     st.write("---")
            
    elif query:
        with st.spinner(text="In progress..."):
            find_query_url=f"{api_url}/search" 
            recom_job_ids = requests.post(find_query_url, data=query).json()
            recom_job_objids = [ObjectId(job_id) for job_id in recom_job_ids['job_ids']]
            st.header("Search Results")
            recom_jobs=[next(mon.find({'_id':oid},{'_id':False})) for oid in recom_job_objids]
        show_jobs(recom_jobs)

        
    # Get 100 job listings
    else:
        n=100
        jobs = mon.find_n(n)

        # Show job listings
        show_jobs(list(jobs))
    

def show_jobs(jobs):
    # Show 100 jobs per page
    num_jobs = len(jobs)
    num_pages = int(num_jobs / 100) + 1

    # Create container for job listings
    container = st.container()

    start_index = 0
    end_index = min(start_index + 100, num_jobs)
    col1, col2 = st.columns(2)
    # Show job listings in vertical slider
    with container:
        job_blocks = []
        # st.write('<style>div.row-widget.stHorizontal{flex-wrap: nowrap !important;}</style>', unsafe_allow_html=True)
        # st.write('<style>.main .block-container {flex: 1 1 0px}</style>', unsafe_allow_html=True)
        # st.write('<style>.block-container {max-height:500px;overflow:auto;} </style>',unsafe_allow_html=True)
        for i in range(start_index, end_index):
            if i%2==0:
                with col1:
                    job_title = jobs[i]["job_title"]
                    employer = jobs[i]["employer_name"]
                    job_description = jobs[i]["job_description"]
                    job_block = st.expander(f":blue[{job_title}] - {employer}")
                    job_block.write(job_description)
                    job_blocks.append(job_block)
            else:
                with col2:
                    job_title = jobs[i]["job_title"]
                    employer = jobs[i]["employer_name"]
                    job_description = jobs[i]["job_description"]
                    job_block = st.expander(f":blue[{job_title}] - {employer}")
                    job_block.write(job_description)
                    job_blocks.append(job_block)
        if end_index < num_jobs:
            if st.button("Load more"):
                start_index = end_index
                end_index = min(start_index + 100, num_jobs)
                for i in range(start_index, end_index):
                    job_title = jobs[i]["job_title"]
                    employer = jobs[i]["employer_name"]
                    job_description = jobs[i]["job_description"][:100]+'...'
                    job_block = st.expander(f":blue[{job_title}] - {employer}")
                    job_block.write(job_description)
                    job_blocks.append(job_block)

    # Add slider for selecting page
    # page_number = st.slider("Page", 1, num_pages, 1)

if __name__ == "__main__":
    main()
