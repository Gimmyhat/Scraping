# API проекта Artsy предоставляет информацию о некоторых деятелях искусства, их работах, выставках.
import requests
import json

client_id = 'fc0dd48a3344c8dea776'
client_secret = 'a8de2cd5802ec9c4e2631c627ea36da6'

# Получаем токен с сайта
r = requests.post("https://api.artsy.net/api/tokens/xapp_token",
                  data={
                      "client_id": client_id,
                      "client_secret": client_secret
                  })
j = json.loads(r.text)
token = j["token"]

# отправляем запрос по художнику 4d8b92b34eb68a1b2c0003f4
artist = '4d8b92b34eb68a1b2c0003f4'
headers = {"X-Xapp-Token": token}

r = requests.get(fr"https://api.artsy.net/api/artists/{artist}", headers=headers)

# записываем ответ в файл
with open('art.json', 'w') as file:
    json.dump(r.json(), file)
