import requests
import json


username = "gimmyhat"
url = f"https://api.github.com/users/{username}/repos"

user_data = requests.get(url).json()
user_data_dir = {rep.get('name'): rep.get('url') for rep in user_data}
with open('user_data.json', 'w') as file:
    json.dump(user_data_dir, file)

