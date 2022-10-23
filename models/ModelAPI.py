
from models.BaseModel import Model, MODEL_TYPES
from flask_restx import Namespace, Resource, fields

api = Namespace('Models', description='Expiration models')

model_type = api.model('Model', {
    'id': fields.String(required=True, description='Model type identifier'),
    'name': fields.String(required=True, description='Model name'),
})

model = Model()

@api.route('/model/types')
class AvaluableModelTypes(Resource):
    @api.doc('model_types')
    @api.marshal_list_with(model_type)
    def get(self):
        '''List of all avaluable model types'''
        return MODEL_TYPES


@api.route('/model/<id>')
@api.param('id', 'Model type identifier')
@api.response(404, 'Model type not found')
class ModelType(Resource):
    @api.doc('get_model_name')
    @api.marshal_with(model_type)
    def get(self, id):
        '''Get model name by its identifier'''
        for model in MODEL_TYPES:
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

