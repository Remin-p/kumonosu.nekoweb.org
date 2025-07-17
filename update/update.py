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

print(repo.head.reference.log()[-1][1]) # Grabs the latest commit hash

sendFiles = [item for item in sendFiles if not any(str(item).startswith(target) for target in noSend)]
print(sendFiles)

# Make a request to upload these files

NEKOWEB_API_KEY = os.getenv('NEKOWEB_API_KEY')

url = 'https://nekoweb.org/api/files/upload'
headers = { 'Authorization': NEKOWEB_API_KEY }

for file in sendFiles:
    files = { 'files': (file, open(file, 'rb'), 'application/octet-stream') }
    data = { 'pathname': '.' if file.find('/') == -1 else file[:file.rfind('/')+1] }
    
    try:
        response = requests.request('POST', url, headers=headers, data=data, files=files)
        response.raise_for_status()
    
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    print(file, response.text)
