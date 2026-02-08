import requests

# Enviar mensagem de teste
url = "http://localhost:8080/message/sendText/cliente_1"
headers = {
    "apikey": "sua_chave_aqui",
    "Content-Type": "application/json"
}
payload = {
    "number": "556294757240",  # Seu número pessoal
    "text": "Teste do bot! 🤖"
}

response = requests.post(url, json=payload, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
