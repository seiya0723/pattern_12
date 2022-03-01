import requests,time

URL = ""

while True:
    try:
        requests.get(URL)
    except Exception as e:
        print(e)

    time.sleep(60*30)



