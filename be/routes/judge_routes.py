from flask import Blueprint, request, jsonify
from controllers.judge_controller import judge_code
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required

judge_bp = Blueprint("judge", __name__)

@judge_bp.route("/run-python", methods=["POST", "OPTIONS"])
@cross_origin(origins="http://127.0.0.1:5500")
@jwt_required()
def run_python():
    data = request.get_json()
    source_code = data.get("code")
    test_input = data.get("input", "")
    expected_output = data.get("expected_output", "")

    result = judge_code(source_code, test_input, expected_output)
    return jsonify(result)
