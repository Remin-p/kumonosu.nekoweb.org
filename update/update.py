from git import Repo
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

NEKOWEB_API_KEY = os.getenv('NEKOWEB_API_KEY')

url = "https://nekoweb.org/api/files/upload"
headers = { "Authorization": NEKOWEB_API_KEY }

for file_path in sendFiles:
    with open(file_path,'rb') as f:
        files = { "files": (file_path, open(f), "application/octet-stream") }
        data = { "pathname": '.' if file_path.find('/') == -1 else file_path[:file_path.rfind('/')+1] }

        response = requests.request("POST", url, headers=headers, data=data, files=files)
    print(file, response.raise_for_status)
