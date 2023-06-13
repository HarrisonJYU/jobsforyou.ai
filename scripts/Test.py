import requests

api_url = "http://127.0.0.1:5000"
query_url = f"{api_url}/find_closest_match"
test_pdf = './data/p18swathi_CV2.pdf'
response = requests.post(query_url, json={"path": test_pdf})