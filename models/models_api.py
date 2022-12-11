from models.survival import Model, MODEL_TYPES, MODELS_LIST
from flask import jsonify, make_response
from flask_restx import Namespace, Resource, fields

api = Namespace("Models", description="Expiration models")

model_type = api.model(
    "Model",
    {
        "name": fields.String(required=True, description="Model name"),
        "type": fields.String(required=True, description="Model type"),
    },
)

model = Model()


@api.route("/types")
class AvaluableModelTypes(Resource):
    @api.doc("model_types")
    # @api.marshal_with(model_type)
    def get(self):
        """List of all avaluable model types"""
        return jsonify(MODEL_TYPES)


@api.route("/types/<name>")
@api.param("name", "Model identifier")
class ModelType(Resource):
    @api.doc("get_model_type")
    # @api.marshal_with(model_type, mask="name")
    def get(self, name):
        """Get model type by its identifier"""
        for model in MODEL_TYPES:
            if model["name"] == name:
                return jsonify(model)
        return f"Model '{name}' not found in avaluable models", 404


@api.route("/model/set", methods=["POST"])
class SetModel(Resource):
    # @api.expect(model_type)
    def post(self):
        name = api.payload
        if name not in model.models_list:
            return f"Model '{name}' not found in avaluable models", 404
        else:
            if model.model_type == name:
                message = f"Model {name} already set"
            elif model.model_type is not None:
                message = f"Clear existing model before setting the new one"
            else:
                model.set_model_type(name)
                message = f"Set model to {name}"
            return message, 201
