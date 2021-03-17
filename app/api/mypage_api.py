# 2021.01.05 made by Candykick(우수몽)

from flask import request, current_app, jsonify, make_response
from flask_restx import Resource, Api, Namespace, fields
from flask_jwt_extended import *
from sqlalchemy import text
import datetime, json

MyPage = Namespace(
    name='Mypage',
    description="마이페이지 정보를 관리하는 API 모음."
)


@MyPage.route('/user_info')
class User_Info(Resource):
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
            # 3. 유저 정보를 가져옴.
            user = current_app.database.execute(text("""
                                                            SELECT * FROM User WHERE id= :user_id ;
                                                        """), {
                'user_id': user_id
            }).fetchone()

            # 4. 유저 정보가 존재하지 않는다면 -> 오류 리턴
            if user is None:
                return [], 204
            # 4. 유저 정보가 존재한다면
            else:
                # 5. is_author 값을 가지고 작가 여부를 체크함.
                d_user = dict(user)

                if d_user['is_author'] == 0:
                    d_user['is_author'] = False
                else:
                    d_user['is_author'] = True

                return jsonify({
                    'id': d_user['id'],
                    'name': d_user['name'],
                    'profile': d_user['profile'],
                    'is_author': d_user['is_author'],
                    'email': d_user['email'],
                    'introduction': d_user['introduction'],
                    'coin': d_user['coin']
                })


@MyPage.route('/my_writing')
class Write_By_Me(Resource):
    @jwt_required
    def post(self):
        """내가 쓴 글 정보를 불러옴. 정렬 순서는 0(최신순), 1(인기순)"""
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
            # 3. 최신순 정렬인 경우 -> id 내림차순 순서대로 쿼리.
            writing_list = current_app.database.execute(text("""
                                                        SELECT * FROM Writing Where author_id = :author_id ORDER BY id DESC;
                                                    """), {
                'author_id': user_id
            }).fetchall()
            # if sort == 0:
            # writing_list = current_app.database.execute(text(
            #                                         SELECT * FROM Writing Where author_id = :author_id ORDER BY id DESC;
            #                                     ), {
            #      'author_id': user_id
            #   }).fetchall()
            # 3. 인기순 정렬인 경우 -> 인기도 내림차순 순서대로 쿼리.
            # (인기도를 구현하지 않은 관계로 일단 최신순 정렬과 동일하게 작동함.)
            # else:
            # writing_list = current_app.database.execute(text(

            # 4. 등록된 글이 있다면 모든 글의 정보를 리턴.
            if len(writing_list) > 0:
                d_writing_list = []
                for writing in writing_list:
                    d_writing = dict(writing)
                    # permission 값을 가지고 업로드 여부를 체크함.
                    # if d_writing['permission']==0:
                    #    d_writing['is_uploaded'] = False
                    # else:
                    #    d_writing['is_uploaded'] = True

                    # if d_writing['is_end']==0:
                    #    d_writing['is_end'] = False
                    # else:
                    #    d_writing['is_end'] = True

                    # series_id -> series_name
                    series_info = current_app.database.execute(text("""
                                                                            SELECT title, is_end FROM Series WHERE id = :series_id;
                                                                        """), {
                        'series_id': d_writing['series_id']
                    }).fetchone()
                    d_writing['series_name'] = series_info['title']
                    if series_info['is_end'] == 1:
                        d_writing['is_end'] = True
                    else:
                        d_writing['is_end'] = False

                    d_writing_list.append(d_writing)

                return jsonify(
                    [{
                        'id': writing['id'],
                        'series_id': writing['series_id'],
                        'series_name': writing['series_name'],
                        'episode_num': writing['episode_num'],
                        'title': writing['title'],
                        'image': writing['image'],
                        'date': writing['date'],
                        'hits': writing['hits'],
                        'comment_num': writing['comment_num'],
                        'permission': writing['permission'],
                        'is_end': writing['is_end'],
                        'author_id': writing['author_id'],
                        'contents': writing['contents']
                    } for writing in d_writing_list]
                )
            # 4. 등록된 작품이 없다면 204(No Content) 리턴.
            else:
                return jsonify([])


@MyPage.route('/subscribe_author')
class Subscribe_List_Author(Resource):
    @jwt_required
    def post(self):
        """현재 유저가 구독하고 있는 모든 작가의 정보를 불러옴."""
        # 0. 토큰값을 가져옴.
        current_user = get_jwt_identity()
        # 1. Subscribe_Author 테이블에서 현재 유저가 구독하고 있는 모든 작가의 id 정보를 가져옴.
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
            subscribe_list = current_app.database.execute(text("""
                                    SELECT * FROM Subscribe_Author
                                    WHERE user_id = :user_id ;
                                """), {
                'user_id': user_id
            }).fetchall()

            # 3. 구독한 작가 정보가 있다면 다음으로 진행.
            if len(subscribe_list) > 0:
                # 4. 모든 작가의 id 정보를 OR로 연결한 문자열을 만듬. (3번 작업을 위함)
                author_query_string = ''
                for subscribe in subscribe_list:
                    author_query_string += 'id = '
                    author_query_string += str(subscribe['author_id'])
                    author_query_string += ' OR '

                author_query_string = author_query_string[0:len(author_query_string) - 4]
                author_query_string = 'SELECT * FROM User WHERE ' + author_query_string + ";"

                # 5. Author 테이블에서 모든 작가의 id 정보에 해당하는 작가 정보를 가져옴.
                author_list = current_app.database.execute(text(author_query_string)).fetchall()

                # 6. 구독한 작가 정보를 json array로 리턴함.
                return jsonify(
                    [{
                        'id': author['id'],
                        'name': author['name'],
                        'profile': author['profile'],
                        'series_num': author['series_num'],
                        'recent_update': author['recent_update'],
                        'zzimkkong': author['zzimkkong']
                    } for author in author_list]
                )
            # 구독한 작가 정보가 없다면 204(No Content) 리턴함.
            else:
                return jsonify([])


@MyPage.route('/add_subscribe_author')
class Add_Subscribe_Author(Resource):
    @jwt_required
    def post(self):
        """현재 유저의 작가 구독 목록에 새로운 작가를 추가함."""
        # 토큰값을 가져옴.
        current_user = get_jwt_identity()
        # user_id, author_id를 가져옴.
        user_id = request.form['user_id']
        author_id = request.form['author_id']
        is_subscribe = request.form['is_subscribe']

        # 토큰값이 잘못된 경우
        if current_user is None:
            # 401(Unauthorized)를 리턴한다.
            return make_response(jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401)
        # 토큰값이 정상인 경우
        else:
            # 구독하는 경우 처리
            if is_subscribe == 'T':
                # 1. 중복된 값을 찾아본다.
                duplication_value = current_app.database.execute(text("""
                        SELECT * FROM Subscribe_Author WHERE user_id=:user_id AND author_id=:author_id;
                    """), {
                    'user_id': user_id,
                    'author_id': author_id
                }).fetchall()

                # 2. 중복된 값이 없다면 등록을 진행하고 success를 리턴한다.
                if len(duplication_value) == 0:
                    current_app.database.execute(text("""
                            INSERT INTO Subscribe_Author (user_id, author_id) VALUES (:user_id, :author_id);
                        """), {
                        'user_id': user_id,
                        'author_id': author_id
                    })

                    # 추가 : 작가 DB의 zzimkkong 값을 하나 증가시킨다.
                    current_app.database.execute(text("""
                                                UPDATE User SET zzimkkong=zzimkkong+1 WHERE id = :author_id ;
                                            """), {
                        'author_id': author_id
                    })

                    return jsonify(
                        {
                            'result': 'success',
                            'contents': 'success'
                        }
                    )
                # 2. 중복된 값이 있다면 오류를 리턴한다.
                else:
                    return make_response(jsonify(
                        {
                            "result": "fail",
                            "contents": "중복된 값이 있습니다."
                        }
                    ), 202)

            # 구독을 취소하는 경우 처리
            else:
                # 1. 값이 있는지 찾아본다.
                duplication_value = current_app.database.execute(text("""
                                        SELECT * FROM Subscribe_Author WHERE user_id=:user_id AND author_id=:author_id;
                                    """), {
                    'user_id': user_id,
                    'author_id': author_id
                }).fetchall()

                # 2. 값이 있다면
                if len(duplication_value) > 0:
                    # 2. 구독 취소 처리를 하고 success 출력.
                    current_app.database.execute(text("""
                                                            DELETE FROM Subscribe_Author WHERE user_id = :user_id AND author_id = :author_id;
                                                        """), {
                        'user_id': user_id,
                        'author_id': author_id
                    })

                    # 추가 : 작가 DB의 zzimkkong 값을 하나 감소시킨다.
                    current_app.database.execute(text("""
                                                                    UPDATE User SET zzimkkong=zzimkkong-1 WHERE id = :author_id ;
                                                                """), {
                        'author_id': author_id
                    })

                    return jsonify(
                        {
                            'result': 'success',
                            'contents': 'success'
                        }
                    )

                # 해당 값이 없다면
                else:
                    return make_response(jsonify(
                        {
                            "result": "fail",
                            "contents": "해당하는 값이 없습니다."
                        }
                    ), 202)


@MyPage.route('/subscribe_series')
class Subscribe_List_Series(Resource):
    @jwt_required
    def post(self):
        """현재 유저가 구독하고 있는 모든 시리즈의 정보를 불러옴."""
        # 0. 토큰값을 가져옴.
        current_user = get_jwt_identity()
        # 1. Subscribe_Series 테이블에서 현재 유저가 구독하고 있는 모든 시리즈의 id 정보를 가져옴.
        user_id = request.form['id']

        # 토큰값이 잘못된 경우
        if current_user is None:
            # 401(Unauthorized)를 리턴한다.
            return make_response(jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401)
        # 토큰값이 정상인 경우
        else:
            subscribe_list = current_app.database.execute(text("""
                                            SELECT * FROM Subscribe_Series
                                            WHERE user_id = :user_id ;
                                        """), {
                'user_id': user_id
            }).fetchall()

            # 구독한 시리즈 정보가 있다면 다음으로 진행.
            if len(subscribe_list) > 0:
                # 2. 모든 시리즈의 id 정보를 OR로 연결한 문자열을 만듬. (3번 작업을 위함)
                series_query_string = ''
                for subscribe in subscribe_list:
                    series_query_string += 'id = '
                    series_query_string += str(subscribe['series_id'])
                    series_query_string += ' OR '

                series_query_string = series_query_string[0:len(series_query_string) - 4]
                series_query_string = 'SELECT * FROM Series WHERE ' + series_query_string + ";"

                # 3. Series 테이블에서 모든 시리즈의 id 정보에 해당하는 시리즈 정보를 가져옴.
                series_list = current_app.database.execute(text(series_query_string)).fetchall()

                d_series_list = []
                for series in series_list:
                    d_series = dict(series)
                    if d_series['is_end'] == 1:
                        d_series['is_end'] = True
                    else:
                        d_series['is_end'] = False

                    d_series_list.append(d_series)

                # 4. 구독한 시리즈 정보를 json array로 리턴함.
                return jsonify(
                    [{
                        'id': series['id'],
                        'author_id': series['author_id'],
                        'author_name': series['author_name'],
                        'title': series['title'],
                        'image': series['image'],
                        'date': series['date'],
                        'introduction': series['introduction'],
                        'hash_tag': series['hash_tag'],
                        'hits': series['hits'],
                        'comment_num': series['comment_num'],
                        'recent_update': series['recent_update'],
                        'zzimkkong': series['zzimkkong'],
                        'is_end': series['is_end'],
                        'writing_num': series['writing_num']
                    } for series in d_series_list]
                )
            # 구독한 시리즈 정보가 없다면 204(No Content) 리턴함.
            else:
                return jsonify([])


@MyPage.route('/add_subscribe_series')
class Add_Subscribe_Series(Resource):
    @jwt_required
    def post(self):
        """현재 유저의 시리즈 구독 목록에 새로운 시리즈를 추가함."""
        # 토큰값을 가져옴.
        current_user = get_jwt_identity()
        # user_id, series_id를 가져옴.
        user_id = request.form['user_id']
        series_id = request.form['series_id']
        is_subscribe = request.form['is_subscribe']

        # 토큰값이 잘못된 경우
        if current_user is None:
            # 401(Unauthorized)를 리턴한다.
            return make_response(jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401)
        # 토큰값이 정상인 경우
        else:
            # 구독 처리를 하는 경우
            if is_subscribe == 'T':
                # 1. 중복된 값을 찾아본다.
                duplication_value = current_app.database.execute(text("""
                        SELECT * FROM Subscribe_Series WHERE user_id=:user_id AND series_id=:series_id;
                    """), {
                    'user_id': user_id,
                    'series_id': series_id
                }).fetchall()

                # 2. 중복된 값이 없다면 등록을 진행하고 success를 리턴한다.
                if len(duplication_value) == 0:
                    current_app.database.execute(text("""
                            INSERT INTO Subscribe_Series (user_id, series_id) VALUES (:user_id, :series_id);
                        """), {
                        'user_id': user_id,
                        'series_id': series_id
                    })

                    # 추가 : 시리즈 DB의 zzimkkong 값을 하나 증가시킨다.
                    current_app.database.execute(text("""
                                                    UPDATE Series SET zzimkkong=zzimkkong+1 WHERE id = :series_id ;
                                                """), {
                        'series_id': series_id
                    })

                    return jsonify(
                        {
                            'result': 'success',
                            'contents': 'success'
                        }
                    )
                # 2. 중복된 값이 있다면 오류를 리턴한다.
                else:
                    return make_response(jsonify(
                        {
                            "result": "fail",
                            "contents": "중복된 값이 있습니다."
                        }
                    ), 202)

            # 구독 취소를 하는 경우
            else:
                # 1. 해당 값이 있는지 찾아본다.
                duplication_value = current_app.database.execute(text("""
                                        SELECT * FROM Subscribe_Series WHERE user_id=:user_id AND series_id=:series_id;
                                    """), {
                    'user_id': user_id,
                    'series_id': series_id
                }).fetchall()

                # 2. 해당 값이 있다면
                if len(duplication_value) > 0:
                    # 2. 구독 취소 처리를 하고 success 출력.
                    current_app.database.execute(text("""
                                                            DELETE FROM Subscribe_Series WHERE user_id = :user_id AND series_id = :series_id;
                                                        """), {
                        'user_id': user_id,
                        'series_id': series_id
                    })

                    # 추가 : 시리즈 DB의 zzimkkong 값을 하나 감소시킨다.
                    current_app.database.execute(text("""
                                                        UPDATE Series SET zzimkkong=zzimkkong-1 WHERE id = :series_id ;
                                                    """), {
                        'series_id': series_id
                    })

                    return jsonify(
                        {
                            'result': 'success',
                            'contents': 'success'
                        }
                    )

                # 해당 값이 없다면
                else:
                    return make_response(jsonify(
                        result="fail",
                        contents="해당하는 값이 없습니다."
                    ), 202)


@MyPage.route('/update_introduction')
class User_Intro(Resource):
    @jwt_required
    def post(self):
        """현재 유저의 정보를 가져옴."""
        # 0. 토큰값을 가져옴.
        current_user = get_jwt_identity()
        # 1. 필요한 값들을 parameter로 받아옴.
        user_id = request.form['id']
        intro = request.form['introduction']
        user_name = request.form['name']

        # 2. 토큰값이 잘못된 경우
        if current_user is None:
            # 3. 401(Unauthorized)를 리턴한다.
            return make_response(jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401)
        # 2. 토큰값이 정상인 경우
        else:
            # 3. 유저 정보를 가져옴.
            current_app.database.execute(text("""
                                                            UPDATE User SET introduction = :intro, name = :name WHERE id = :user_id ;
                                                        """), {
                'user_id': user_id,
                'intro': intro,
                'name': user_name
            })

            return jsonify(
                {
                    'result': 'success',
                    'contents': 'success'
                }
            )


@MyPage.route('/my_series')
class Series_By_Me(Resource):
    @jwt_required
    def post(self):
        """내가 쓴 시리즈 정보를 불러옴."""
        # 0. 토큰값을 가져옴.
        current_user = get_jwt_identity()
        # 1. 필요한 값들을 parameter로 받아옴.
        user_id = request.form['id']

        # 2. 토큰값이 잘못된 경우
        if current_user is None:
            # 3. 401(Unauthorized)를 리턴한다.
            return jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401
        # 2. 토큰값이 정상인 경우
        else:
            # 3. 최신순 정렬인 경우 -> id 내림차순 순서대로 쿼리.
            writing_list = current_app.database.execute(text("""
                                                        SELECT * FROM Series Where author_id = :author_id ORDER BY id DESC;
                                                    """), {
                'author_id': user_id
            }).fetchall()

            d_series_list = []
            for series in writing_list:
                d_series = dict(series)
                if d_series['is_end'] == 1:
                    d_series['is_end'] = True
                else:
                    d_series['is_end'] = False

                d_series_list.append(d_series)

            if len(writing_list) > 0:
                return jsonify(
                    [{
                        'id': series['id'],
                        'author_id': series['author_id'],
                        'author_name': series['author_name'],
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
                    } for series in writing_list]
                )
            else:
                return jsonify([])


@MyPage.route('/finish_series')
class Finish_Series(Resource):
    @jwt_required
    def post(self):
        """시리즈를 완결시킴."""
        # 토큰값을 가져옴.
        current_user = get_jwt_identity()
        # user_id, series_id를 가져옴.
        user_id = request.form['id']
        series_id = request.form['series_id']
        is_ended = request.form['is_end']

        # 토큰값이 잘못된 경우
        if current_user is None:
            # 401(Unauthorized)를 리턴한다.
            return jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401
        # 토큰값이 정상인 경우
        else:
            # 완결인 경우
            if is_ended == 'T':
                current_app.database.execute(text("""
                            UPDATE Series SET is_end = 1 WHERE id = :series_id ;
                        """), {
                    'series_id': series_id
                })
            elif is_ended == 'F':
                current_app.database.execute(text("""
                            UPDATE Series SET is_end = 0 WHERE id = :series_id ;
                        """), {
                    'series_id': series_id
                })

            return jsonify(
                {
                    'result': 'success',
                    'contents': 'success'
                }
            )

def json_default(value):
    if isinstance(value, datetime.date):
        return value.strftime('%y.%m.%d');
    raise TypeError('not JSON serializable')
data = {'date': datetime.date.today()}
json_data = json.dumps(data, default=json_default)
