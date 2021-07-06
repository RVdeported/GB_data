#import os
import requests
import json
#from dotenv import load_dotenv

#------------------Task 1---------------------

def get_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url=url)

    if response.status_code != 200:
        print("Response is not 200")
        return None
    return response

def save_repo_list(response, filename = "Repos.json"):
    with open(filename, 'w') as f:
        f.write(json.dumps(response.json()))
        f.close()

def print_repo_list(response):
    return [n["name"] for n in response.json()]


response = get_repos("RVdeported")
save_repo_list(response)
print(print_repo_list(response))

#------------------Task 2---------------------

