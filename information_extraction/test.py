import requests
import time
import ast


if __name__ == '__main__':
    uri = "http://api.conceptnet.io/query?start=/c/en/parsley&rel=/r/IsA"
    obj = requests.get(uri).json()
    obj.keys()
    time.sleep(0.5)
    edges = obj['edges']
    for elem in edges:
        print(str(elem['surfaceText']).split("[["))
