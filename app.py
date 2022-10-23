from flask import Flask
from flask_restx import Api

from models_api import api as models


api = Api(
    title='Expiration models',
    version='1.0',
    description='Choose, fit and predict expiration models',
)

api.add_namespace(models, path='/models')

app = Flask(__name__)
api.init_app(app)

if __name__=='__main__':
    app.run(debug=True)
