import os
import requests
import json
from dotenv import load_dotenv

load_dotenv("../.env")
USERNAME = os.environ.get("GIT_NAME")
WEATHER_KEY = os.environ.get("OPEN_WEATHER_KEY")

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


response = get_repos(USERNAME)
save_repo_list(response)
print(print_repo_list(response))

#------------------Task 2---------------------

def get_cur_temp(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}'
    
    respond = requests.get(url=url)
    
    if respond.status_code != 200:
        print("Request not succsessful. Check the city entered.")
        print(respond.content)
        return None
    return respond.json()

def translate_temp_from_response(response, temp_type='Celsium'):
    """ Returns cur temperature in Celsium, Kelvin or Fahrenheit"""
    temp = response["main"]["temp"]
    
    if temp_type == 'Celsium':
        return temp - 273.15
    if temp_type == 'Fahrenheit':
        return (temp - 273.15) * 9 / 5 + 32
    if temp_type == 'Kelvin':
        return temp
    
    print("Incorrect temp_type entered. Returning Celsium")
    return temp - 273.15 

def get_cur_temp_pipe(temp_type = 'Celsium'):
    
    print("Please, enter the city\n")
    city = input()
    
    respond = get_cur_temp(city)
    if respond is None:
        return False
    
    return translate_temp_from_response(respond, temp_type)
    
if __name__ == "__main__":
    print(round(get_cur_temp_pipe(),2))
    
