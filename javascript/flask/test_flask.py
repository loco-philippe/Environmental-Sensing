from flask import Flask, request, render_template, abort

from pymongo import MongoClient
from essearch import ESSearch, empty_request

app = Flask(__name__)

@app.get('/')
def get():
    return render_template('html_initial.html')

@app.post('/')
def post():
    # Gérer l'asynchronicité ? Est-ce nécessaire ?
    # ajouter la gestion de sessions
    # permettre l'annulation prématurée des requêtes
    content = request.get_json()
    print(content)
    try:
        if 'request_type' in content and (content["request_type"] == 'mongo-validation' or content["request_type"] == 'mongo-validation-namelist'):
            try:
                client = MongoClient([content["uri"]])
                collection = client[content["database_name"]][content["collection_name"]]
                if content["request_type"] == 'mongo-validation-namelist':
                    empty = empty_request(collection)
                    print(empty)
                    return empty
                else:
                    return 'mongo_data is valid'
            except:
                return 'mongo_data is invalid'
        elif 'request_type' in content and content["request_type"] == 'execute':
            try:
                client = MongoClient([content["uri"]])
                collection = client[content["database_name"]][content["collection_name"]]
            except:
                return 'mongo_data is invalid'
            srch = ESSearch(input=collection, parameters=content["parameters"])
            print(srch.request)
            result = srch.execute(returnmode = 'single').to_obj(encoded = True, modecodec='dict', geojson=True)
            print(result)
            #for obs in result: print(obs)
            return result
    except:
        abort(499, "An error occured") # ne fonctionne pas, 499 n'est pas un code d'erreur accepté par abort
    return ''