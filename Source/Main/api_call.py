import requests
import sys
import json
import openai

# Authenticate with Github API
auth_token = '<github_key>'
headers = {'Authorization':'Token ' + auth_token}

owner = "Raghav-Bajaj"
repo = "Pr-Review"
base = 'main'
head = 'my-branch'
pull_number=3
url1 = f'https://api.github.com/repos/{owner}/{repo}/compare/{base}...{head}'
# url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all"
# pull_number = "1"
url2 = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"

response = requests.get(url1, headers=headers)



if response.status_code == 200:
    diffs = response.json()["files"]
    for i, diff in enumerate(diffs):
        patch = diff["patch"]
        with open(f'diff_{i}.patch', 'w') as f:
            f.write(patch)

    add_changes = []
    delete_changes = []

    for i, diff in enumerate(diffs):
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
else:
    print(f"Failed to get diff, status code: {response.status_code}")

url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pull_number}/comments"
response = requests.get(url)

# parse the response and extract the body and URL of each comment

if response.status_code == 200:
    comments = []
    # comment = response.json()
    # print(comment)
    for comment in response.json():
      body = comment["body"]
      comments.append(body)

# write the comments to a file
with open("comments.txt", "w") as f:
    for comment in comments:
        f.write(comment + "\n")

openai.api_key ="<gpt_key>"
model="text-davinci-003"

def chat_with_chatgpt(prompt):
    review = openai.Completion.create(engine=model, prompt=prompt, max_tokens=2800)
    return review.choices[0].text

with open("comments.txt", "r") as f:
    comment = f.read()

with open("add_changes.txt", "r") as f:
    snipt_1 = f.read()

with open("delete_changes.txt", "r") as f:
    snipt_2 = f.read()
# print(f"snipt1: {snipt_1}")
# print(f"snipt2: {snipt_2}")
comment_p = f"Evalute the changes on the basis of the provided information and tell if the code is meeting the coding standards and quality and is it satisfactory to merge the pr or not. Given: {comment}. Two Snippets will be provided namely, Snipt1 and Snipt2. Snipt1 will contain the changes added to the files and Snipt2 will contain the changes removed from the files. If Snipt1 is empty means nothing is added or if Snipt2 is empty means nothing is removed."
# print(f"comment: {comment_p}")
prompt = f"{comment_p} \n Snipt1: {snipt_1} \n Snipt2: {snipt_2}"
print(f"prompt: {prompt}")
response = chat_with_chatgpt(prompt)
print("Chatgpt:::>",end='\n')
for i in response:
    sys.stdout.write(i)
    sys.stdout.flush()

pull_response = requests.get(url2, headers=headers)
pr_info = pull_response.json()

# Post review as a comment on the Github PR
comment_url = pr_info['comments_url']
comment_body = "Automated review using OpenAI: {}\n".format(response)
git_response = requests.post(comment_url, headers=headers, json={'body': comment_body})
if git_response.status_code == 201:
    print('\nReview posted successfully')
else:
    print('\nError posting review: {}'.format(git_response.text))