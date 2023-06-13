## JobsForYou - Matching resumes with relevant jobs powered by AI

Build a resume matching platform (i.e. when user uploads a resume, the system parses the resume and finds the most relevant job posting from the available job postings on the internet)

Steps Involved

- Periodically (using Airflow) use job listing APIs to retrieve the open job listings, and save the content to GCS
  Eg APIs: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
- Aggregate the saved data and create a collection on MongoDB
- Retrieve the relevant information from the aggregate (i.e. description/location/skills etc) and pass them through a Deep Learning pre-trained network (using PyTorch/HuggingFace) to obtain sentence embeddings and store them in a vector Database (eg. Meta’s FAISS)
- Build a parser to read user’s resume and use the same Deep Learning Model to obtain a sentence embedding
- Find a vector (from the vector database) which closely matches the user’s vector
- Build a Web Interface (Streamlit) for users to upload the resume, and return the cloest match jobs and job details.
