"""
Dummy server for testing telemetry reporting.
In order to run this module you need `flask` and `flask-restful` installed.
"""

from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class Telemetry(Resource):

    def put(self):
        print(request.json)
        return {}


api.add_resource(Telemetry, '/telemetry')


if __name__ == '__main__':
    app.run(debug=True)
