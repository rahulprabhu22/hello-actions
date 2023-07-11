import requests
import re
from time import sleep
import json

pat=''



def run(org_name,project_name,repo_name,files,run=False):
    new_branch_name ='refs/heads/relic-pr'

    repo_url =f'https://dev.azure.com/{org_name}/{project_name}/_apis/git/repositories/{repo_name}'

    # get the branch name
    repo = requests.get( repo_url + '?api-version=7',auth=('',pat))
    if repo.status_code != 200:
        print("Error Getting the Repo:",f'{org_name}/{project_name}/{repo_name} \n',repo.text)
        exit()

    default_branch = repo.json()['defaultBranch'].split('/')[-1]
    print('Default Branch:',default_branch)
    if default_branch != 'main' and default_branch != 'master':
        print('Warning!: Default Branch does not match',default_branch)
        exit()

    # Get the default branch latest commit ID
    default_branch_commit = requests.get(repo_url + f'/commits?searchCriteria.itemVersion.version={default_branch}&&searchCriteria.$top=1&api-version=6.1-preview.1',auth=('',pat))
    if default_branch_commit.status_code != 200:
        print("Error Getting the Commit ID:",f'{org_name}/{project_name}/{repo_name} \n',default_branch_commit.text)
        exit()

    default_branch_commit_id = default_branch_commit.json()['value'][0]['commitId']
    print('Latest Commit:',default_branch_commit_id)

    # Get the file 
    def get_file(file_name):
        file_contents_resp = requests.get( repo_url + f'/items?Path={file_name}&download=true',auth=('',pat))
        if file_contents_resp.status_code != 200:
            print("Error Getting the file:",f'{org_name}/{project_name}/{repo_name} \n',file_contents_resp.text)
            exit()
        return file_contents_resp.text


    def find_occurences(content,environment,run_replace):
        patterns = [f' - {environment}',f'- {environment}', f' -{environment}',f'-{environment}']
        count=0
        original_content = content
        for pattern in patterns:
            for occurence in re.finditer(pattern,content):
                print(original_content[occurence.start()-15:occurence.start()+20])
                count+=1
                content = content.replace(pattern,'')
        if count:
            print(f'===============\n',f'{environment}',count, '\n=================\n')
        return content,count

    environments = ['Local','Staging','Stage','Production']

    pushes = []
    print("\n**************  Files  ****************\n")
    for file in files:
        print(f"====== {file} ====")
        file_contents = get_file(file)
        # print(file,file_contents)
        flag = 0
        for env in environments:
            file_contents,count = find_occurences(file_contents, env,run)
            flag+=count
        if flag:
            pushes.append({
                    "changeType": "edit",
                    "item": {
                        "path": file
                    },
                    "newContent": {
                        "content": file_contents
                    }
                })
        else:
            print("---------No Pattern Matched---------\n========================")

    # Push the changes to remote
    if run:
        push_changes = requests.post(repo_url + '/pushes?api-version=6.1-preview.2',auth=('',pat),json={
        "refUpdates": [
            {
            "name": new_branch_name,
            "oldObjectId": default_branch_commit_id
            }
        ],
        "commits": [
            {
            "comment": "Added New Relic Fix",
            "changes": pushes
            }
        ]})
        print(push_changes.status_code,push_changes.text)

        pr_description = ''' 
Description
[] Hello World
[] Change Hola!

## 🏀 Changes
- Rename `appName` to `appName` without environment

## 💁🏻‍♀️ What are the Other Changes?
There are other changes too!
'''
        
        if push_changes.status_code < 301:
            sleep(2)
            create_pr = requests.post(repo_url + '/pullrequests?api-version=7',auth=('',pat),json={
                "sourceRefName": new_branch_name,
                "targetRefName": f'refs/heads/{default_branch}',
                "title": "ENV PR relic name",
                "description": pr_description,
                "reviewers": [
                    {
                    "id": "4cc4da87-86f2-6715-8c51-7a223b785fe9",
                    "isRequired": False
                    }
                ]})
            
            if create_pr.status_code != 200:
                print("Error Creating PR:",f'{org_name}/{project_name}/{repo_name} \n',create_pr.text)
                exit()

# for repos in 'project':

orgs = json.load(open('repos.json'))

for org in orgs.keys():
    for repo in orgs[org]:
        print('Project:',org,'\nRepo:',repo)
        run('RahulCloud',org,repo,orgs[org][repo],run=False)
        print('#######################################################################\n')
# org_name = 'RahulCloud'
# project_name = 'M1'
# repo_name = 'M1'
