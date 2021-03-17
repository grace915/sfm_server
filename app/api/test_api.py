from flask import request, current_app, jsonify
from flask_restx import Resource, Api, Namespace, fields
from flask_jwt_extended import *
from sqlalchemy import text
from . import image_upload_api

Test = Namespace(
    name='Test',
    description="Test."
)

@Test.route('')
class Tester(Resource):
    @jwt_required
    def post(self):
            """현재 유저의 정보를 가져옴."""
            # 0. 토큰값을 가져옴.
            current_user = get_jwt_identity()
            # 1. 필요한 값들을 parameter로 받아옴.
            user_id = request.form['id']

            # 2. 토큰값이 잘못된 경우
            if current_user is None:
                # 3. 401(Unauthorized)를 리턴한다.
                return make_response(jsonify({
                    "result": "fail",
                    "contents": "잘못된 토큰값입니다."
                }), 401)
            # 2. 토큰값이 정상인 경우
            else:
                return jsonify({"result":"success", "contents":"성공!"})

