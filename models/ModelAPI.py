
from models.BaseModel import Model, MODEL_TYPES
from flask import jsonify, make_response
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
        return make_response(jsonify({'message': MODEL_TYPES}))


@api.route('/model/<id>')
@api.param('id', 'Model type identifier')
@api.response(404, 'Model type not found')
class ModelType(Resource):
    @api.doc('get_model_name')
    @api.marshal_with(model_type, mask='id')
    def get(self, id):
        '''Get model name by its identifier'''
        for model in MODEL_TYPES:
            if model['id'] == id:
                return make_response(jsonify({'message': model}))
        # return {'Result': f'Model {model.model} not found in avaluable models'}, 404
        api.abort(404)


@api.route('/model/set_model', methods=['POST'])
class SetModel(Resource):
    @api.expect(model_type)
    def post(self):
        model_name = api.payload
        if model_name not in model.models_list:
            message = f'Model {model.model} not found in avaluable models'
            return make_response(jsonify({'message': message}), 404)
        else:
            if model.model_type == model_name:
                message = f'Model {model.model} already set'
            elif model.model is not None:
                message = f'Clear existing model before setting the new one'
            else:
                model.model_type = model_name
                message = f'Set model to {model.model}'
            return make_response(jsonify({'message': message}, 201))

