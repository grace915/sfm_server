from flask import request, current_app, jsonify
from flask_restx import Resource, Api, Namespace, fields
from flask_jwt_extended import *
from sqlalchemy import text
import time

Admin = Namespace(
    name='Admin',
    description="관리자 API"
)

#CORS(app)
#CORS(app, resources={r'*': {'origins': '*'}})

@Admin.route('/change_permission')
class Series_List_All(Resource):
    def post(self):
        """글 게시를 허용/비허용."""
        # 1. 시리즈 id를 parameter로 받아옴.
        author_id = int(request.form['author_id'])
        writing_id = int(request.form['writing_id'])
        permission = int(request.form['permission'])

        # 2. 시리즈 id에 해당하는 모든 글 정보를 DB에서 가져옴.
        #    이 때, permission은 0(TRUE)여야 함. permission이 1인 글은 아직 게시가 허락되지 않은 것.
        current_app.database.execute(text("""
                                                            UPDATE Writing SET permission = :permission WHERE id = :writing_id ;
                                                        """), {
            'writing_id': writing_id,
            'permission': permission
        })

        writingnumdata = current_app.database.execute(text("""
                                                            Select Count(*) From Writing Where series_id IN (SELECT series_id FROM Writing WHERE id = :writing_id AND permission = :permission )
                                                        """), {
            'writing_id': writing_id,
            'permission': 1
        })

        # 유저가 글 등록하고 수락 시 작가로 변환
        if permission == 1:
            current_app.database.execute(text("""
                                                            UPDATE User SET is_author = 1 WHERE id = :author_id ;
                                                        """), {
                'author_id': author_id
            })
            # 시리즈의 글 전체 갯수를 세서 writing_num 업데이트
            current_app.database.execute(text("""
                                                            UPDATE Series SET writing_num = :writing_num WHERE id IN (SELECT series_id FROM Writing WHERE id = :writing_id )
                                                        """), {
                'writing_id': writing_id,
                'writing_num': writingnumdata['Count(*)']+1
            })
        else:
            current_app.database.execute(text("""
                                                            UPDATE Series SET writing_num = :writing_num WHERE id IN (SELECT series_id FROM Writing WHERE id = :writing_id )
                                                        """), {
                'writing_id': writing_id,
                'writing_num': writingnumdata['Count(*)']-1
            })

        return jsonify({'result': 'success'})

@Admin.route('/all')
class Series_List_Allfd(Resource):
    def post(self):
        # 1. 시리즈 id를 parameter로 받아옴.
        permission = int(request.form['permission'])

        writing_list = current_app.database.execute(text("""
                                        SELECT * FROM Writing WHERE permission = :permission ;
                                    """), {'permission':permission}).fetchall()
# 3. 등록된 글이 있다면 모든 글의 정보를 리턴.
        if len(writing_list) > 0:
            d_writing_list = []
            for writing in writing_list:
                # permission 값을 가지고 업로드 여부를 체크함.
                d_writing = dict(writing)

                if d_writing['permission'] == 0:
                    d_writing['is_uploaded'] = False
                else:
                    d_writing['is_uploaded'] = True

                # series_id -> series_name
                d_writing['series_name'] = current_app.database.execute(text("""
                                                                                    SELECT title FROM Series WHERE id = :series_id;
                                                                                """), {
                    'series_id': d_writing['series_id']
                }).fetchone()['title']

                d_writing_list.append(d_writing)

            return jsonify([{
                    'id': writing['id'],
                    'series_id': writing['series_id'],
                    'series_name': writing['series_name'],
                    'author_id': writing['author_id'],
                    'is_uploaded': writing['is_uploaded'],
                    'episode_num': writing['episode_num'],
                    'title': writing['title'],
                    'image': writing['image'],
                    'date': writing['date'],
                    'comment_num': writing['comment_num'],
                    'hits': writing['hits']
                } for writing in d_writing_list])
        else:
            return jsonify([])



