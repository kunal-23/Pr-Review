import requests
import sys
import json
import openai

def chat_with_chatgpt(prompt):
    conversation = []
    conversation.append({'role':'user','content':str({prompt})})
    review = openai.ChatCompletion.create(model=model_id, messages=conversation)
    return review.choices[0].message.content

def post_review(headers, url2, chatgpt_response, fileName):
    pull_response = requests.get(url2, headers=headers)
    pr_info = pull_response.json()

    # Post review as a comment on the Github PR
    comment_url = pr_info['comments_url']
    comment_body = "Automated review using OpenAI for file {}:\n {}\n".format(fileName,chatgpt_response)
    git_response = requests.post(comment_url, headers=headers, json={'body': comment_body})
    if git_response.status_code == 201:
        print('\nReview posted successfully')
    else:
        print('\nError posting review: {}'.format(git_response.text))

openai.api_key ="<gpt_key>"
model_id="gpt-3.5-turbo"

# Authenticate with Github API
auth_token = '<github_key>'
headers = {'Authorization':'Token ' + auth_token}

#PR details
owner = "Raghav-Bajaj"
repo = "Pr-Review"
base = 'main'
head = 'my-branch'
pull_number=4

#Endpoints
url1 = f'https://api.github.com/repos/{owner}/{repo}/compare/{base}...{head}'

url2 = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"

url3 = f"https://api.github.com/repos/{owner}/{repo}/issues/{pull_number}/comments"

#PR details
pr_response = requests.get(url1, headers=headers)

if pr_response.status_code == 200:
    diffs = pr_response.json()["files"]
    for i, diff in enumerate(diffs):
        chatgpt_response = ''
        add_changes = []
        delete_changes = []
        original_file = ''
        patch = diff["patch"]
        fileName = diff["filename"]
        if(diff["status"] == 'modified' or diff["status"] == 'deleted'):
            print(f'\nModified file :{fileName}');
            url4 = f"https://raw.githubusercontent.com/{owner}/{repo}/{base}/{fileName}"
            response = requests.get(url4, headers=headers)
            original_file= response.text
        else:
            print("\nNew file is being added.")  
          
        with open(f'diff_{i}.patch', 'w') as f:
            f.write(patch)
        with open(f'diff_{i}.patch', 'r') as f:
            for line in f:
                if line.startswith('+'):
                    add_changes.append(line[1:])
                elif line.startswith('-'):
                    delete_changes.append(line[1:])
        
        with open('add_changes.txt', 'w') as f:
            f.write(''.join(add_changes))

        with open('delete_changes.txt', 'w') as f:
            f.write(''.join(delete_changes)) 

        #Call to comments endpoint
        comments_response = requests.get(url3)

        # parse the response and extract the body and URL of each comment

        if comments_response.status_code == 200:
            comments = []
            for comment in comments_response.json():
                body = comment["body"]
                if(not str(body).startswith('Automated review using OpenAI')):
                    comments.append(body)

        # write the comments to a file
        with open("comments.txt", "w") as f:
            for comment in comments:
                f.write(comment + "\n")

        with open("comments.txt", "r") as f:
            comment = f.read()

        with open("add_changes.txt", "r") as f:
            snipt_1 = f.read()

        with open("delete_changes.txt", "r") as f:
            snipt_2 = f.read()
        #print(f"snipt1: {snipt_1}")
        #print(f"snipt2: {snipt_2}")
        comment_p = f"Evalute the changes on the basis of the provided information and tell if the code is meeting the coding standards and quality and is it satisfactory to merge the pr or not. Given: {comment} 3 variables will be provided namely orgFile,Snipt1 and Snipt2. orgFile will contain the current contents of the file present in the branch for which PR is being raised. Snipt1 will contain the changes being added to the orgFile as part of PR and Snipt2 will contain the changes removed from this file. If Snipt1 is empty means nothing is added or if Snipt2 is empty means nothing is removed from the file. Simillarly if orgFile is empty it means the entire file is new. Below provided information is related to only {fileName} file."
        # print(f"comment: {comment_p}")
        prompt = f"{comment_p} \n orgFile: {original_file} \n Snipt1: {snipt_1} \n Snipt2: {snipt_2}"
        print(f"prompt: {prompt}")
        chatgpt_response = chat_with_chatgpt(prompt)
        print("Chatgpt:::>",end='\n')
        for i in chatgpt_response:
            sys.stdout.write(i)
            sys.stdout.flush()
        
        post_review(headers, url2, chatgpt_response, fileName)
        
else:
    print(f"Failed to get diff, status code: {pr_response.status_code}")
