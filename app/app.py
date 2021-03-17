# mysql 연동 : https://velog.io/@inyong_pang/Flask-API-MySQL-%EC%97%B0%EB%8F%99-SQLAlchemy
# Layered-Architecture 및 flask-restx 응용 : https://justkode.kr/python/flask-restapi-1
# flask_restx parameter passing : https://github.com/noirbizarre/flask-restplus/issues/772
# jwt token 발급 및 응용 : https://blog.naver.com/shino1025/221954027152
# flask_jwt_extended : https://flask-jwt-extended.readthedocs.io/en/stable/
# flask에서 파일 업로드 : https://velog.io/@kho5420/Flask-%ED%8C%8C%EC%9D%BC-%EC%97%85%EB%A1%9C%EB%93%9C-File-Upload%ED%95%98%EA%B8%B0
# flask에서 AWS S3에 업로드 : https://velog.io/@kho5420/Flask-AWS-S3%EC%97%90-%ED%8C%8C%EC%9D%BC-%EC%97%85%EB%A1%9C%EB%93%9C%ED%95%98%EA%B8%B0
# AWS S3 Public Upload 허용 방법 : https://stackoverflow.com/questions/52711199/how-to-upload-files-to-aws-s3-with-public-access-granted

from flask import Flask, request, jsonify, current_app
from flask_restx import Api, resource
from flask.json import JSONEncoder
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine, text
from flask_jwt_extended import *

from api import author_api, notice_api, series_api, user_api, writing_api, mypage_api, test_api, image_upload_api, \
    admin_api, comment_api


# Default JSON Encoder는 set->JSON 변환이 불가능하다.
# 따라서 Custom Endocer를 작성해서 set->list로 변환 후 JSON 변환을 진행한다.
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)

app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title="You are Heroine API Server",
    description="개발중입니다."
)

CORS(app, resources={r'*': {'origins': '*'}})

app.json_encoder = CustomJSONEncoder
app.config.from_pyfile("config.py")
# JWT 확장 모듈을 flask 어플리케이션에 등록함.
jwt = JWTManager(app)

database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow = 0)
app.database = database

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

api.add_namespace(author_api.Author, '/author')
api.add_namespace(series_api.Series, '/series')
api.add_namespace(writing_api.Writing, '/writing')
api.add_namespace(notice_api.Notice, '/notice')
api.add_namespace(user_api.User, '/user')
api.add_namespace(mypage_api.MyPage, '/mypage')
api.add_namespace(test_api.Test, '/test')
api.add_namespace(image_upload_api.Images, '/images')
api.add_namespace(admin_api.Admin, '/admin')
api.add_namespace(comment_api.Comment, '/comment')

