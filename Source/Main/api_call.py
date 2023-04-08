import requests
import sys
import json


headers = {
    "Authorization": <github_key>
}

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

api_key =<gpt_key>
model="text-davinci-003"

def chat_with_chatgpt(prompt):
  res = requests.post(f"https://api.openai.com/v1/completions",
          headers = {
              "Content-Type": "application/json",
              "Authorization": f"Bearer {api_key}"
          },
          json={
              "model": model,
              "prompt": prompt,
              "max_tokens": 2800,
          }).json()
  return res['choices'][0]['text'][1:]
# comment=""
# snipt_1=""
# snipt_2=""
with open("comments.txt", "r") as f:
    comment = f.read()

with open("add_changes.txt", "r") as f:
    snipt_1 = f.read()

with open("delete_changes.txt", "r") as f:
    snipt_2 = f.read()
# print(f"snipt1: {snipt_1}")
# print(f"snipt2: {snipt_2}")
comment_p = f"Snipt1 contains what is added to files and snipt2 contains what is removed evalute the changes on the basis of this comment if snipt1 is empty means nothing is added or if snipt2 is empty means nothing is removed {comment} and tell if it is satisfactory to merge the pr"
# print(f"comment: {comment_p}")
prompt = f"{comment_p} \n snipt1 {snipt_1} \n snipt2 {snipt_2}"
response = chat_with_chatgpt(prompt)
print("Chatgpt:::>",end='\n')
for i in response:
    sys.stdout.write(i)
    sys.stdout.flush()













