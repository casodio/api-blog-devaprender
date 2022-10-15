from requests.auth import HTTPBasicAuth
import requests
a = input('usuario: ')
s = input('pass: ')

resultado = requests.get('http://localhost:5000/login', auth=(a, s))

print(resultado.json())

resultado_token = requests.get('http://localhost:5000/autores', headers={'x-access-token':resultado.json()['token']})
print(resultado_token.json())
