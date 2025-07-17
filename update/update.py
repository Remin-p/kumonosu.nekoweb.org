from git import Repo
import requests
import os
import sys

# Define files to be updated with diff

repo = Repo('.')
sendFiles = []
deleteFiles = []
noSend = ['.github/','update/']

with open('update/last_commit.txt','r') as file: 
    last_commit = file.read().strip()

diffs = repo.commit(last_commit).diff(repo.head.commit) # Compare the _oldest_ commit to HEAD otherwise it's not going to detect which files have been deleted.

print('Last commit being compared:', last_commit)
print(f"Number of diffs found: {len(diffs)}")

for d in diffs:
    if d.deleted_file:
        deleteFiles.append(d.a_path)
    elif d.a_path and d.b_path: # Check if both paths exist
        sendFiles.append(d.a_path)

sendFiles = [item for item in sendFiles if not any(str(item).startswith(target) for target in noSend)]
deleteFiles = [item for item in deleteFiles if not any(str(item).startswith(target) for target in noSend)]

print('=> Files to send:', sendFiles)
print('=> Files to delete:', deleteFiles)

# Make requests to upload files

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

    print(f"-> File '{file}' upload, response: {response.status_code,response.text} <-")

# Make requests to delete files

if len(deleteFiles) <= 0:
    print("No files to delete from last commit. Exiting...")
    sys.exit()

url = 'https://nekoweb.org/api/files/delete'
headers = { 'Authorization': NEKOWEB_API_KEY, 'content-type':'application/x-www-form-urlencoded' }

for file in deleteFiles:
    payload = f"pathname={file}"

    try:
        response = requests.request('POST', url, headers=headers, data=payload)
        response.raise_for_status()
 
    except requests.exceptions.HTTPError as err:
        if response.status_code == 400:
            print(f"=X 400, Failed to upload file {file} (payload '{payload}'): {response.text}!")
            break
        raise SystemExit(err)

    print(f"-> File '{file}' delete (Payload '{payload}'), response: {response.status_code,response.text} <-")

# TODO: Update the last_commit.txt with the latest commit hash

print(repo.head.reference.log()[-1][1]) # Grabs the latest commit hash
