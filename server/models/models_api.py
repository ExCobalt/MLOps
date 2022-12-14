from models.survival import Model, MODEL_TYPES, MODELS_LIST
import json
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
@api.param("name", "Model name")
class ModelType(Resource):
    @api.doc("get_model_type")
    # @api.marshal_with(model_type, mask="name")
    def get(self, name):
        """Get model type by its name"""
        for model in MODEL_TYPES:
            if model["name"] == name:
                return jsonify(model)
        return f"Model '{name}' not found in avaluable models", 501


@api.route("/model/set", methods=["POST"])
class SetModel(Resource):
    # @api.expect(model_type)
    def post(self):
        name = api.payload
        if name not in model.models_list:
            return f"Model '{name}' not found in avaluable models", 501
        if model.model_type == name:
            return f"Model {name} already set", 200
        
        model.clear_model()
        model.set_model_type(name)
        return f"Set model to {name}", 201


@api.route("/fitted")
class ListAllFitted(Resource):
    @api.doc("list all fitted models")
    def get(self):
        """List of all avaluable fitted models"""
        model.update_storage()
        return model.fitted, 200
    
    # def post(self):
    #     name = api.payload
    #     if name not in model.fitted.keys():
    #         return f"Model '{name}' not found in avaluable models", 501
    #     return jsonify(model.fitted[name]), 200


@api.route("/fitted/<name>")
@api.param("name", "Model type")
class ListAllFittedType(Resource):
    @api.doc("Get all fitted models of chosen type")
    def get(self, name):
        if name in model.models_list:
            return jsonify(model.fitted[name])
        return f"Model '{name}' not found in avaluable models", 501

