import requests

# response = requests.post('http://127.0.0.1:5000/ads',
#                          json={
#                              "heading": "Python",
#                              "description": "Iterable programming language",
#                              "owner": "WWW"
#                          })
# print(response.status_code)
# print(response.text)

# response = requests.get('http://127.0.0.1:5000/ads/2')
# print(response.status_code)
# print(response.text)

response = requests.delete("http://127.0.0.1:5000/ads/2")
print(response.status_code)
print(response.text)
