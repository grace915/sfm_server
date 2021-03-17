# 2020.12.27 made by Candykick(우수몽)

from flask import request, current_app, jsonify
from flask_restx import Resource, Api, Namespace, fields
from flask_jwt_extended import *
from sqlalchemy import text
import time

from . import image_upload_api

Writing = Namespace(
    name='Writing',
    description="글 정보를 관리하는 API 모음."
)

@Writing.route('/list')
class Series_List_All(Resource):
    def post(self):
        """시리즈 id에 해당하는 모든 글 정보를 가져옴."""
        # 1. 시리즈 id를 parameter로 받아옴.
        user_id = int(request.form['user_id'])
        series_id = int(request.form['series_id'])
        sort = request.form['sort']

        # 2. 시리즈 id에 해당하는 모든 글 정보를 DB에서 가져옴.
        #    이 때, permission은 0(TRUE)여야 함. permission이 1인 글은 아직 게시가 허락되지 않은 것.
        if sort=='0': #등록순
            writing_list = current_app.database.execute(text("""
                                                                SELECT * FROM Writing WHERE permission = 1 AND series_id = :series_id ORDER BY episode_num;
                                                            """), {
                'series_id': series_id
            }).fetchall()
        else: #최신순
            writing_list = current_app.database.execute(text("""
                                                                SELECT * FROM Writing WHERE permission = 1 AND series_id = :series_id ORDER BY episode_num DESC;
                                                            """), {
                'series_id': series_id
            }).fetchall()

        # 3. 구독중인 시리즈인지 체크한다.
        if user_id != 0:
            subscribe_info = current_app.database.execute(text("""
                                                                SELECT * from Subscribe_Series WHERE user_id = :user_id AND series_id = :series_id ;
                                                            """), {
                'series_id': series_id,
                'user_id': user_id
            }).fetchone()

            if subscribe_info is None:
                subscribe_result = False
            else:
                subscribe_result = True
        else:
            subscribe_result = False

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

            # author info, introduce
            information = current_app.database.execute(text("""
                                                                                SELECT is_end, zzimkkong, author_id, author_name, introduction FROM Series WHERE id = :series_id;
                                                                            """), {
                'series_id': series_id
            }).fetchone()

            if information['is_end'] == 1:
                is_ended = True
            else:
                is_ended = False

            return jsonify({
                'author_id': information['author_id'],
                'author_name': information['author_name'],
                'introduce': information['introduction'],
                'zzimkkong': information['zzimkkong'],
                'is_end': is_ended,
                'is_subscribe': subscribe_result,
                'data':[{
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
                    'hits': writing['hits'],
                } for writing in d_writing_list]
            })
        # 3. 등록된 글이 없다면 204(No Content) 리턴.
        else:
            # author info, introduce
            information = current_app.database.execute(text("""
                                                                                SELECT zzimkkong, author_id, author_name, introduction FROM Series WHERE id = :series_id;
                                                                            """), {
                'series_id': series_id
            }).fetchone()

            return jsonify({
                'author_id': information['author_id'],
                'author_name': information['author_name'],
                'introduce': information['introduction'],
                'zzimkkong': information['zzimkkong'],
                'is_subscribe': subscribe_result,
                'data':[]
            })

@Writing.route('/contents')
class Series_List_All(Resource):
    def post(self):
        """글 id에 해당하는 글의 내용을 가져옴."""
        # 1. 글 id를 parameter로 받아옴.
        writing_id = request.form['id']

        # 2. 글 id에 해당하는 글 정보를 DB에서 가져옴.
        writing = current_app.database.execute(text("""
                                        SELECT * FROM Writing WHERE id = :writing_id ;
                                    """), {
            'writing_id': writing_id
        }).fetchone()

        if writing is not None:
            d_writing = dict(writing)

            d_series = current_app.database.execute(text("""
                                                                        SELECT * FROM Series WHERE id = :series_id;
                                                                    """), {
                'series_id': writing['series_id']
            }).fetchone()

            # 추가 : 조회수를 1 증가시킨다.
            d_writing['hits'] += 1
            current_app.database.execute(text("""
                                                        UPDATE Writing SET hits = :hits WHERE id = :writing_id ;
                                                    """), {
                'hits': d_writing['hits'],
                'writing_id': writing_id
            })
            # 시리즈 DB의 조회수도 1 증가시킨다.
            current_app.database.execute(text("""
                                                                    UPDATE Series SET hits=hits+1 WHERE id = :series_id ;
                                                                """), {
                'series_id': d_writing['series_id']
            })
            # 유저정보도 가져온다.
            d_user = current_app.database.execute(text("""
                                                                        SELECT * FROM User WHERE id = :id ;
                                                                    """), {
                'id': writing['author_id']
            }).fetchone()

            # 3. 정상적으로 받아왔다면 해당 글의 내용을 리턴.
            return jsonify(
                {
                    'series_name': d_series['title'],
                    'hash_tag': d_series['hash_tag'],
                    'episode_num': d_writing['episode_num'],
                    'author_id': writing['author_id'],
                    'author_name': d_user['name'],
                    'introduction': d_series['introduction'],
                    'title': d_writing['title'],
                    'image': d_writing['image'],
                    'date': d_writing['date'],
                    'contents': d_writing['contents'],
                    'music': d_writing['music'],
                    'comment_num': d_writing['comment_num'],
                    'hits': d_writing['hits'],
                    'permission': d_writing['permission'],
                    'series_id': d_writing['series_id']
                }
            )
        # 3. 정상 처리에 실패했다면 204(No content) 리턴.
        else:
            return [], 204

@Writing.route('/upload')
class Writing_Upload(Resource):
    @jwt_required
    def post(self):
        """글을 업로드함. 이미지를 Storage에 올린 뒤, 이미지 주소를 받고, 전체 내용을 DB에 등록함."""
        # 토큰값을 가져옴.
        current_user = get_jwt_identity()
        is_new = int(request.form['is_new'])
        user_id = int(request.form['id'])
        writing_id = int(request.form['writing_id'])
        series_id = int(request.form['series_id'])
        title = request.form['title']
        date = time.strftime('%y.%m.%d')
        permission = 0

        # 토큰값이 잘못된 경우
        if current_user is None:
            # 401(Unauthorized)를 리턴한다.
            return jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401
        # 토큰값이 정상인 경우
        else:
            if 'image' in request.files:
                image = request.files['image']
                # 이미지 업로드.
                image_url = image_upload_api.upload_image(image, "writing")
                # 글을 DB에 업로드함
                if is_new == 0:
                    current_app.database.execute(text("""
                                                UPDATE Writing SET title = :title, image = :image, date = :date, permission = :permission 
                                                WHERE id = :writing_id AND author_id = :author_id;
                                            """), {
                        'writing_id': writing_id,
                        'title': title,
                        'image': image_url,
                        'date': date,
                        'author_id': user_id,
                        'permission': permission
                    })
                else:
                    current_app.database.execute(text("""
                                                UPDATE Writing SET title = :title, image = :image, date = :date, 
                                                WHERE id = :writing_id AND author_id = :author_id;
                                            """), {
                        'writing_id': writing_id,
                        'title': title,
                        'image': image_url,
                        'date': date,
                        'author_id': user_id
                    })
            else:
                # 글을 DB에 업로드함
                if is_new == 0:
                    current_app.database.execute(text("""
                                                UPDATE Writing SET title = :title, date = :date, permission = :permission 
                                                WHERE id = :writing_id AND author_id = :author_id;
                                            """), {
                        'writing_id': writing_id,
                        'title': title,
                        'date': date,
                        'author_id': user_id,
                        'permission': permission
                    })
                else:
                    current_app.database.execute(text("""
                                                UPDATE Writing SET title = :title, date = :date, 
                                                WHERE id = :writing_id AND author_id = :author_id;
                                            """), {
                        'writing_id': writing_id,
                        'title': title,
                        'date': date,
                        'author_id': user_id
                    })

            # 작가 DB의 recent_update 값을 수정함.
            current_app.database.execute(text("""
                                                    UPDATE User SET recent_update = :date WHERE id = :user_id ;
                                                """), {
                'user_id': user_id,
                'date': date
            })

            # 시리즈 DB의 recent_update 값을 수정함.
            current_app.database.execute(text("""
                                                                UPDATE Series SET recent_update = :date WHERE id = :series_id ;
                                                            """), {
                'series_id': series_id,
                'date': date
            })

            # 결과 리턴
            return jsonify(
                {
                    'result': 'success',
                    'contents': 'success',
                    'writing_id': writing_id
                }
            )


@Writing.route('/save')
class Writing_Save(Resource):
    @jwt_required
    def post(self):
        """글을 임시저장함."""
        # 토큰값을 가져옴.
        current_user = get_jwt_identity()
        is_new = int(request.form['is_new'])
        user_id = int(request.form['id'])
        series_id = int(request.form['series_id'])
        title = "임시저장 "+time.strftime('%y.%m.%d')
        date = time.strftime('%y.%m.%d')
        contents = request.form['contents']
        permission = 2
        music = ""
        comment_num = 0
        hits = 0

        # 토큰값이 잘못된 경우
        if current_user is None:
            # 401(Unauthorized)를 리턴한다.
            return jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401
        # 토큰값이 정상인 경우
        else:
            # 새 글이면 0
            if is_new == 0:
                # 시리즈 이미지를 찾아낸다.
                series_image = current_app.database.execute(text("""
                                                                        SELECT image from Series WHERE id = :series_id ;
                                                                    """), {
                    'series_id': series_id,
                }).fetchone()

                # episode_num 계산하기 = 현재 시리즈 id에 해당하는 글 갯수 + 1
                count = current_app.database.execute(text("""
                                                            SELECT COUNT(*) FROM Writing WHERE series_id = :series_id ;
                                                        """), {
                    'series_id': series_id
                }).fetchone()
                episode_num = count['COUNT(*)'] + 1

                # 글을 DB에 업로드함
                current_app.database.execute(text("""
                                                INSERT INTO Writing (series_id, episode_num, title, image, date, contents, permission, music, comment_num, hits, author_id)
                                                 VALUES (:series_id, :episode_num, :title, :image, :date, :contents, :permission, :music, :comment_num, :hits, :author_id);
                                            """), {
                    'series_id': series_id,
                    'episode_num': episode_num,
                    'title': title,
                    'image': series_image['image'],
                    'date': date,
                    'contents': contents,
                    'permission': permission,
                    'music': music,
                    'comment_num': comment_num,
                    'hits': hits,
                    'author_id': user_id
                })

                # 업로드가 제대로 이루어졌는지 찾아봄.
                writing_result = current_app.database.execute(text("""
                                                                        SELECT * FROM Writing WHERE series_id = :series_id AND episode_num = :episode_num;
                                                                    """), {
                    'series_id': series_id,
                    'episode_num': episode_num
                }).fetchone()

                # 결과 리턴
                if writing_result is None:
                    return jsonify(
                        {
                            'result': 'fail',
                            'contents': '등록 실패'
                        }
                    )
                else:
                    return jsonify(
                        {
                            'result': 'success',
                            'contents': 'success',
                            'writing_id': writing_result['id']
                        }
                    )

            # 기존 글 수정이면 1
            elif is_new == 1:
                # 등록된 글의 id값을 파라미터로 받는다.
                writing_id = int(request.form['writing_id'])

                # id에 해당하는 글의 내용을 수정한다.
                current_app.database.execute(text("""
                                                UPDATE Writing SET date = :date, contents = :contents WHERE id = :writing_id;
                                            """), {
                    'date': date,
                    'contents': contents,
                    'writing_id': writing_id
                })

                # 결과 리턴
                return jsonify(
                    {
                        'result': 'success',
                        'contents': 'success'
                    }
                )

@Writing.route('/delete')
class Serie03321(Resource):
    @jwt_required
    def post(self):
        """글 id에 해당하는 글을 삭제함"""
        # 토큰값을 가져옴.
        current_user = get_jwt_identity()
        # 1. 글 id를 parameter로 받아옴.
        writing_id = int(request.form['id'])

        # 토큰값이 잘못된 경우
        if current_user is None:
            # 401(Unauthorized)를 리턴한다.
            return jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401
        # 토큰값이 정상인 경우
        else:
            # 2. 글 id에 해당하는 글 정보를 DB에서 삭제함.
            current_app.database.execute(text("""
                                        DELETE FROM Writing WHERE id = :writing_id ;
                                    """), {
                'writing_id': writing_id
            })

            # 3. 결과값 대충 리턴
            return jsonify(
                {
                    'result': 'success',
                    'contents': 'success'
                }
            )


@Writing.route('/nextprev')
class Series_List_All(Resource):
    def post(self):
        """글 id에 해당하는 글의 내용을 가져옴."""
        # 1. 글 id를 parameter로 받아옴.
        series_id = request.form['series_id']
        episode_num = request.form['episode_num']

        # 2. 글 id에 해당하는 글 정보를 DB에서 가져옴.
        writing = current_app.database.execute(text("""
                                        SELECT * from Writing w WHERE series_id = :series_id AND episode_num = :episode_num ;
                                    """), {
            'series_id': series_id,
            'episode_num': episode_num
        }).fetchone()

        if writing is not None:
            d_writing = dict(writing)

            d_series = current_app.database.execute(text("""
                                                                        SELECT * FROM Series WHERE id = :series_id;
                                                                    """), {
                'series_id': writing['series_id']
            }).fetchone()

            # 추가 : 조회수를 1 증가시킨다.
            d_writing['hits'] += 1
            current_app.database.execute(text("""
                                                        UPDATE Writing SET hits = :hits WHERE id = :writing_id ;
                                                    """), {
                'hits': d_writing['hits'],
                'writing_id': d_writing['id']
            })
            # 시리즈 DB의 조회수도 1 증가시킨다.
            current_app.database.execute(text("""
                                                                    UPDATE Series SET hits=hits+1 WHERE id = :series_id ;
                                                                """), {
                'series_id': d_writing['series_id']
            })
            # 유저정보도 가져온다.
            d_user = current_app.database.execute(text("""
                                                                        SELECT * FROM User WHERE id = :id ;
                                                                    """), {
                'id': writing['author_id']
            }).fetchone() 

            # 3. 정상적으로 받아왔다면 해당 글의 내용을 리턴.
            return jsonify(
                {
                    'id': d_writing['id'],
                    'series_name': d_series['title'],
                    'hash_tag': d_series['hash_tag'],
                    'episode_num': d_writing['episode_num'],
                    'author_id': writing['author_id'],
                    'author_name': d_user['name'],
                    'introduction': d_series['introduction'],
                    'title': d_writing['title'],
                    'image': d_writing['image'],
                    'date': d_writing['date'],
                    'contents': d_writing['contents'],
                    'music': d_writing['music'],
                    'comment_num': d_writing['comment_num'],
                    'hits': d_writing['hits'],
                    'permission': d_writing['permission'],
                    'series_id': d_writing['series_id']
                }
            )
        # 3. 정상 처리에 실패했다면 204(No content) 리턴.
        else:
            return [],204

