
from model import Model
from flask_restx import Namespace, Resource, fields

api = Namespace('Models', description='Expiration models')

model = api.model('Model', {
    'id': fields.String(required=True, description='Model identifier'),
    'name': fields.String(required=True, description='Model name'),
})

MODELS = [
    {'id': 1, 'name': 'Logit'},
    {'id': 2, 'name': 'Kaplan-Meier'},
    {'id': 3, 'name': 'Cox'},
]


@api.route('/models/list')
class AvaluableModels(Resource):
    @api.doc('models_list')
    @api.marshal_list_with(model)
    def get(self):
        '''List of all avaluable models'''
        return MODELS


@api.route('/models/<id>')
@api.param('id', 'Model identifier')
@api.response(404, 'Model not found')
class ModelName(Resource):
    @api.doc('get_model')
    @api.marshal_with(model)
    def get(self, id):
        '''Get model by its identifier'''
        for model in MODELS:
            if model['id'] == id:
                return model
        api.abort(404)


# @api.route('/model/set_model', methods=['POST'])
# class set_model(Resource):
#     @api.expect(model)
#     def post(self):
#         model_name = api.payload
#         if model_name in model.models_list:
#             model.model = model_name
#             return {'Result': f'Set model to {model.model}'}, 201
#         else:
#             return {'Result': f'Model {model.model} not found in avaluable models'}, 404


