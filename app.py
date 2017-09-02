from flask import Flask, request
from flask_restful import Resource, Api
from drone import Drone

app = Flask(__name__)
api = Api(app)

api.add_resource(Drone, '/drone/<string:command>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
        