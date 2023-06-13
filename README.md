## JobsForYou - Matching resumes with relevant jobs powered by AI

A resume matching platform built with Airflow(fetched jobs), GCP (stored jobs), MongoDB (processed jobs), Pinecone (stored job&resume embeddings), Sentence Transformers (generating embeddings).

Key Features:

- user uploads a resume, the system parses and embeded the resume
- returns the most relevant job posting from the available job postings on the internet

### Architecture

<img src="/assets/architecture.png" alt="Alt Text" width="1500"/>

### Getting Started

Clone this repo

Run `streamlit run main_app.py`
