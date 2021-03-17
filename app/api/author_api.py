# 2020.12.24 made by Candykick(우수몽)

from flask import request, current_app, jsonify
from flask_restx import Resource, Api, Namespace, fields
from flask_jwt_extended import *
from sqlalchemy import text

Author = Namespace(
    name='Author',
    description="작가 정보를 불러오는 API 모음."
)

@Author.route('/all', methods=['POST'])
class AuthorAll(Resource):
    def post(self):
        """모든 작가의 정보를 최근 등록한 작가 순서대로 불러옴."""
        # 작가 목록을 DB에서 불러온다.
        author_list = current_app.database.execute(text("""
                                    SELECT * FROM User WHERE is_author=1;
                                """)).fetchall()

        # 작가 정보가 있다면 : 모든 작가 정보를 리턴한다.
        if len(author_list) > 0:
            return jsonify(
                [{
                    'id': author['id'],
                    'name': author['name'],
                    'profile': author['profile'],
                    'series_num': author['series_num'],
                    'recent_update': author['recent_update'],
                    'zzimkkong': author['zzimkkong'],
                    'introduce': author['introduce']
                } for author in author_list]
            )
        # 작가 정보가 없다면 : 204(No content)를 리턴한다.
        else:
            return jsonify([])

@Author.route('/search/<terms>')
@Author.doc(params={'terms': '작가 이름의 일부분'})
class AuthorSearch(Resource):
    def get(self, terms):
        """작가의 이름을 가지고 검색."""
        #args = request.get_json()
        #search = "%{}%".format(args['terms'])
        #args = request.form['terms']
        #search = "%{}%".format(args)
        #terms = request.args.get('terms')
        #search = "%{}%".format(terms)
        search = "%{}%".format(terms)

        author_list = current_app.database.execute(text("""
                                    SELECT * FROM User
                                    WHERE name LIKE :search AND is_author=1;
                                """), {
            'search': search
        }).fetchall()

        if len(author_list) > 0:
            return jsonify(
                [{
                    'id': author['id'],
                    'name': author['name'],
                    'profile': author['profile'],
                    'series_num': author['series_num'],
                    'recent_update': author['recent_update'],
                    'zzimkkong': author['zzimkkong'],
                    'introduce': author['introduce']
                } for author in author_list]
            )
        else:
            return jsonify([])

@Author.route('/info')
class AuthorAll(Resource):
    def post(self):
        """특정 작가의 정보를 가져옴."""
        # 작가 id를 가져온다.
        author_id = request.form['id']
        user_id = int(request.form['user_id'])

        # 작가 id를 가지고 작가 정보를 검색함.
        author_info = current_app.database.execute(text("""
                                                        SELECT * FROM User WHERE id= :author_id AND is_author=1;
                                                    """), {
            'author_id': author_id
        }).fetchone()

        if author_info is None:
            return [], 204

        else:
            # 작가를 구독하는지 여부를 파악.
            if user_id != 0:
                subscribe_info = current_app.database.execute(text("""
                                                            SELECT * FROM Subscribe_Author WHERE user_id = :user_id AND author_id = :author_id ;
                                                        """), {
                    'author_id': author_id,
                    'user_id': user_id
                }).fetchone()

                if subscribe_info is None:
                    subscribe_result = False
                else:
                    subscribe_result = True
            else:
                subscribe_result = False

            # 작가 id를 가지고 작가가 쓴 작품 정보들을 검색함.
            author_series = current_app.database.execute(text("""
                                                            SELECT * FROM Series WHERE author_id= :author_id ;
                                                        """), {
                'author_id': author_id
            }).fetchall()

            if len(author_series) > 0:
                d_series_list = []
                for series in author_series:
                    d_series = dict(series)
                    if d_series['is_end'] == 0:
                        d_series['is_end'] = False
                    else:
                        d_series['is_end'] = True
                    d_series_list.append(d_series)

                return jsonify({
                    'name': author_info['name'],
                    'introduce': author_info['introduction'],
                    'is_subscribe': subscribe_result,
                    'zzimkkong': author_info['zzimkkong'],
                    'data': [{
                        'id': series['id'],
                        'title': series['title'],
                        'image': series['image'],
                        'date': series['date'],
                        'introduction': series['introduction'],
                        'hash_tag': series['hash_tag'],
                        'recent_update': series['recent_update'],
                        'comment_num': series['comment_num'],
                        'hits': series['hits'],
                        'zzimkkong': series['zzimkkong'],
                        'is_end': series['is_end'],
                        'writing_num': series['writing_num']
                    } for series in d_series_list]
                })

            else:
                return jsonify({
                    'name': author_info['name'],
                    'introduce': author_info['introduction'],
                    'is_subscribe': subscribe_result,
                    'data': []
                })

