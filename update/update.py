from git import Repo
from dotenv import load_dotenv
import requests
import os

# Define files to be updated with diff

repo = Repo('.')
sendFiles = []
noSend = ['.github/','update/']

with open('update/last_commit.txt','r') as file: 
    last_commit = file.read().strip()

diffs = repo.head.commit.diff(last_commit)

for d in diffs:
    sendFiles.append(d.a_path)

print(repo.head.reference.log()[-1])

sendFiles = [item for item in sendFiles if not any(str(item).startswith(target) for target in noSend)]
sendFiles.reverse()
print(sendFiles)

# Make a request to upload these files

load_dotenv()

API_KEY = os.getenv('API_KEY')

url = "https://nekoweb.org/api/files/upload"
headers = { "Authorization": API_KEY }

for file in sendFiles:
    files = { "files": (file, open(file), "application/octet-stream") }
    data = { "pathname": '.' if file.find('/') == -1 else file[:file.rfind('/')+1] }

    response = requests.request("POST", url, headers=headers, data=data, files=files)
    print(file, response.raise_for_status)
