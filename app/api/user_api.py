# 2020.12.27 made by Candykick(우수몽)

from flask import request, current_app, jsonify
from flask_restx import Resource, Api, Namespace, fields
from flask_jwt_extended import *
from sqlalchemy import text

User = Namespace(
    name='User',
    description="유저 정보를 관리하는 API 모음."
)

@User.route('/login')
class Login(Resource):
    def post(self):
        """이메일/패스워드로 로그인을 수행함."""
        # 1. 이메일/패스워드/로그인 방법을 받아옴.
        email = request.form['email']
        login_method = request.form['login_method']

        # 2. 이메일/패스워드에 해당하는 유저 정보가 있는지 찾아봄.
        login_info = current_app.database.execute(text("""
                                                SELECT * FROM User WHERE login_method = :login_method
                                                 AND email = :email;
                                            """), {
            'email': email,
            'login_method': login_method
        }).fetchone()

        # 3. 해당하는 유저 정보가 있다면
        if login_info is not None:
            d_login = dict(login_info)
            if d_login['is_author'] == 0:
                d_login['is_author'] = False
            else:
                d_login['is_author'] = True

            return jsonify(
                result = "success",
                access_token = create_access_token(identity=login_info['id'], expires_delta=False),
                id=login_info['id'],
                email=login_info['email'],
                name=login_info['name'],
                profile=login_info['profile'],
                is_author=d_login['is_author']
            )
        # 3. 해당하는 유저 정보가 없다면
        else:
            return {
                    'result': "fail",
                    'contents': "해당하는 유저 정보가 존재하지 않습니다."
                }, 401

@User.route('/join')
class Join(Resource):
    def post(self):
        """회원가입을 수행함."""
        # 1. 회원가입에 필요한 정보들을 받아옴.
        email = request.form['email']
        name = request.form['nickname']
        profile_url = request.form['profile']
        login_method = request.form['login_method']

        # 2. DB에 정보를 넣음.
        current_app.database.execute(text("""
                                INSERT INTO User (name, profile, login_method, is_author, email)
                                 VALUES (:name, :profile_url, :login_method, 0, :email);
                            """), {
            'name': name,
            'profile_url': profile_url,
            'login_method': login_method,
            'email': email
        })

        # 3. DB에 잘 들어갔는지 확인.
        login_info = current_app.database.execute(text("""
                                                        SELECT * FROM User WHERE login_method = :login_method
                                                         AND email = :email;
                                                    """), {
            'email': email,
            'login_method': login_method
        }).fetchone()

        # 4. 제대로 들어갔다면 :
        if login_info is not None:
            d_login = dict(login_info)
            if d_login['is_author'] == 0:
                d_login['is_author'] = False
            else:
                d_login['is_author'] = True

            return jsonify(
                result="success",
                access_token=create_access_token(identity=login_info['id'], expires_delta=False),
                id=login_info['id'],
                email=login_info['email'],
                name=login_info['name'],
                profile=login_info['profile'],
                is_author=d_login['is_author']
            )
        # 4. 제대로 들어가지 않았다면 :
        else:
            return {
                       'result': "fail",
                       'contents': "해당하는 유저 정보가 존재하지 않습니다."
                   }, 401

