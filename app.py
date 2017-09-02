from flask import Flask, request
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required

app = Flask(__name__)
app.secret_key = 'raniel'
api = Api(app)

coords = {}

class Routing(Resource):
    
    def get(self):
        return self.coords
        
    def post(self):
        data = request.get_json()
        self.coords = data
        print(self.coords)
        return self.coords
        
    def put(self):
        data = request.get_json()
        coords.append(data)
        return coords
        
        
api.add_resource(Routing, '/route')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
        