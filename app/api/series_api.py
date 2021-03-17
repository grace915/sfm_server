# 2020.12.27 made by Candykick(우수몽)

from flask import request, current_app, jsonify
from flask_restx import Resource, Api, Namespace, fields
from flask_jwt_extended import *
from sqlalchemy import text
import time

from . import image_upload_api

Series = Namespace(
    name='Series',
    description="시리즈 정보를 관리하는 API 모음."
)


@Series.route('')
class Series_List_All(Resource):
    def post(self):
        """모든 시리즈 정보를 불러옴. 정렬 순서는 0(최신순), 1(조회수), 2(찜꽁수), 3(인기도)"""
        # 1. 정렬 조건을 parameter로 받아옴.
        sort = request.form['sort']

        # 3. 최신순 정렬인 경우 -> id 내림차순 순서대로 쿼리.
        if sort == '0':
            series_list = current_app.database.execute(text("""
                                                        SELECT * FROM Series WHERE id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY id DESC;
                                                    """)).fetchall()
        # 3. 조회수 정렬인 경우 -> 조회수 내림차순 순서대로 쿼리.
        elif sort == '1':
            series_list = current_app.database.execute(text("""
                                                        SELECT * FROM Series WHERE id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY hits DESC;
                                                    """)).fetchall()
        # 3. 찜꽁수 정렬인 경우 -> 찜꽁수 내림차순 순서대로 쿼리.
        elif sort == '2':
            series_list = current_app.database.execute(text("""
                                                        SELECT * FROM Series WHERE id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY zzimkkong DESC;
                                                    """)).fetchall()
        # 3. 인기도 정렬인 경우 -> (랭킹은 찜꽁수 내림차순, 같으면 조회수 내림차순)
        elif sort == '3':
            classification = request.form['class']
            if classification == '0':  # 주간
                series_list = current_app.database.execute(text("""
                                                        SELECT * FROM Series WHERE id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY zzimkkong_week DESC, hits_week DESC;
                                                    """)).fetchall()
            elif classification == '1':  # 월간
                series_list = current_app.database.execute(text("""
                                                        SELECT * FROM Series WHERE id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY zzimkkong_month DESC, hits_month DESC;
                                                    """)).fetchall()
            else:  # 전체
                series_list = current_app.database.execute(text("""
                                                        SELECT * FROM Series WHERE id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY zzimkkong DESC, hits DESC;
                                                    """)).fetchall()

        # 3. ㄱㄴㄷ순 정렬인 경우 -> 이름 내림차순 순서대로 쿼리.
        else:
            series_list = current_app.database.execute(text("""
                                                        SELECT * FROM Series WHERE id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY title;
                                                    """)).fetchall()

        # 4. 등록된 작품이 있다면 모든 작품의 정보를 리턴.
        if len(series_list) > 0:
            d_series_list = []
            for series in series_list:
                d_series = dict(series)
                if d_series['is_end'] == 0:
                    d_series['is_end'] = False
                else:
                    d_series['is_end'] = True

                d_series_list.append(d_series)

            if sort == '3':
                if classification == '0':  # 주간
                    for d_series in d_series_list:
                        d_series['hits'] = d_series['hits_week']
                        d_series['zzimkkong'] = d_series['zzimkkong_week']
                elif classification == '1':  # 월간
                    for d_series in d_series_list:
                        d_series['hits'] = d_series['hits_month']
                        d_series['zzimkkong'] = d_series['zzimkkong_month']

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
                    'writing_num': series['writing_num'],
                } for series in d_series_list]
            )
        # 4. 등록된 작품이 없다면 204(No Content) 리턴.
        else:
            return [], 204


@Series.route('/search')
class Series_List_Search(Resource):
    def post(self):
        """조건에 맞는 시리즈를 검색. 검색 조건은 0(제목), 1(작가명), 2(해쉬태그), 3(작품소개), 4(제목/작가명/해쉬태그/작품소개 모두 다 포함)"""
        # 1. 검색 조건과 검색어를 parameter로 받아옴.
        cond = int(request.form['cond'])
        terms = request.form['terms']
        sort = int(request.form['sort'])
        # 검색어는 %검색어% 형식으로 변경 (SQL 검색을 위함)
        search = "%{}%".format(terms)

        # 3. 제목으로 검색
        if cond == 0 and sort == 0:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE title LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY id DESC;
                                        """), {
                'search': search
            }).fetchall()
        elif cond == 0 and sort == 1:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE title LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY hits DESC;
                                        """), {
                'search': search
            }).fetchall()
        elif cond == 0 and sort == 2:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE title LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY zzimkkong DESC, hits DESC;
                                        """), {
                'search': search
            }).fetchall()
        elif cond == 0 and sort == 3:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE title LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY title;
                                        """), {
                'search': search
            }).fetchall()
        # 3. 작가명으로 검색
        elif cond == 1 and sort == 0:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE author_name LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY id DESC;
                                        """), {
                'search': search
            }).fetchall()
        elif cond == 1 and sort == 1:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE author_name LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY hits DESC;
                                        """), {
                'search': search
            }).fetchall()
        elif cond == 1 and sort == 2:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE author_name LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY zzimkkong DESC, hits DESC;
                                        """), {
                'search': search
            }).fetchall()
        elif cond == 1 and sort == 3:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE author_name LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY title;
                                        """), {
                'search': search
            }).fetchall()
        # 3. 해쉬태그로 검색
        elif cond == 2:
            if ',' in search:
                tag_query_origin = search.split(',')
                tag_query_list = []
                for tag_query in tag_query_origin:
                    tag_query = tag_query.replace(" ", "")
                    tag_query_list.append(tag_query)

            else:
                tag_query_list = search.split(' ')

            author_query_string = ""
            for tag_query in tag_query_list:
                author_query_string += 'hash_tag LIKE \"%'
                author_query_string += tag_query
                author_query_string += '%\" AND '

            author_query_string = author_query_string[0:len(author_query_string) - 5]
            author_query_string = 'SELECT * FROM Series WHERE id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) AND ' + author_query_string

            if sort == 0:
                series_list = current_app.database.execute(text(author_query_string + " ORDER BY id DESC;"), {
                    'search': search
                }).fetchall()
            elif sort == 1:
                series_list = current_app.database.execute(text(author_query_string + " ORDER BY hits DESC;"), {
                    'search': search
                }).fetchall()
            elif sort == 2:
                series_list = current_app.database.execute(
                    text(author_query_string + " ORDER BY zzimkkong DESC, hits DESC;"), {
                        'search': search
                    }).fetchall()
            elif sort == 3:
                series_list = current_app.database.execute(text(author_query_string + " ORDER BY title;"), {
                    'search': search
                }).fetchall()
        # 3. 작품소개로 검색-없앰
        # elif cond == 3 and sort == 0:
        #    series_list = current_app.database.execute(text("""
        #                                    SELECT * FROM Series WHERE introduction LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY id DESC;
        #                                """), {
        #        'search': search
        #    }).fetchall()
        # elif cond == 3 and sort == 1:
        #    series_list = current_app.database.execute(text("""
        #                                    SELECT * FROM Series WHERE introduction LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY hits DESC;
        #                                """), {
        #        'search': search
        #    }).fetchall()
        # elif cond == 3 and sort == 2:
        #    series_list = current_app.database.execute(text("""
        #                                    SELECT * FROM Series WHERE introduction LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY zzimkkong DESC, hits DESC;
        #                                """), {
        #        'search': search
        #    }).fetchall()
        # elif cond == 3 and sort == 3:
        #    series_list = current_app.database.execute(text("""
        #                                    SELECT * FROM Series WHERE introduction LIKE :search AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY title;
        #                                """), {
        #        'search': search
        #    }).fetchall()
        # 3. 제목/작가명/해쉬태그 다 포함해서 검색
        elif sort == 0:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE (title LIKE :search OR author_name LIKE :search
                                            OR hash_tag LIKE :search) AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY id DESC;
                                        """), {
                'search': search
            }).fetchall()
        elif sort == 1:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE (title LIKE :search OR author_name LIKE :search
                                            OR hash_tag LIKE :search) AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY hits DESC;
                                        """), {
                'search': search
            }).fetchall()
        elif sort == 2:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE (title LIKE :search OR author_name LIKE :search
                                            OR hash_tag LIKE :search) AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY zzimkkong DESC, hits DESC;
                                        """), {
                'search': search
            }).fetchall()
        elif sort == 3:
            series_list = current_app.database.execute(text("""
                                            SELECT * FROM Series WHERE (title LIKE :search OR author_name LIKE :search
                                            OR hash_tag LIKE :search) AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY title;
                                        """), {
                'search': search
            }).fetchall()

        # 4. 등록된 작품이 있다면 모든 작품의 정보를 리턴.
        if len(series_list) > 0:
            d_series_list = []
            for series in series_list:
                d_series = dict(series)
                if d_series['is_end'] == 0:
                    d_series['is_end'] = False
                else:
                    d_series['is_end'] = True

                d_series_list.append(d_series)

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
                    'writing_num': series['writing_num'],

                } for series in d_series_list]
            )
        # 4. 등록된 작품이 없다면 204(No Content) 리턴.
        else:
            return jsonify([])


@Series.route('/upload')
class Series_Upload(Resource):
    @jwt_required
    def post(self):
        """새 시리즈를 등록함. 이미지를 Storage에 올린 뒤, 이미지 주소를 받고, 전체 내용을 DB에 등록함."""
        # 토큰값을 가져옴.
        current_user = get_jwt_identity()
        noimage_url = "https://s3.ap-northeast-2.amazonaws.com/eos.heroine/imgsource/noimage.png"
        is_new = int(request.form['is_new'])

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
                # 시리즈 정보를 가져옴.
                author_id = int(request.form['id'])
                author_name = request.form['name']
                title = request.form['title']
                date = time.strftime('%y.%m.%d')
                introduction = request.form['introduction']
                hash_tag = request.form['hash_tag'],
                recent_update = time.strftime('%y.%m.%d')

                if str(type(hash_tag)) == "<class 'tuple'>":
                    hash_tag_str = ''.join(hash_tag)
                else:
                    hash_tag_str = str(hash_tag)

                # 이미지 정보가 있다면
                if 'image' in request.files:
                    # 이미지를 가져옴.
                    image = request.files['image']
                    # 이미지 업로드.
                    image_url = image_upload_api.upload_image(image, "series")

                    # 시리즈 업로드.
                    current_app.database.execute(text("""
                                        INSERT INTO Series (author_id, author_name, title, image, date, introduction, hash_tag, recent_update)
                                         VALUES (:author_id, :author_name, :title, :image_url, :date, :introduction, :hash_tag, :recent_update);
                                    """), {
                        'author_id': author_id,
                        'author_name': author_name,
                        'title': title,
                        'image_url': image_url,
                        'date': date,
                        'introduction': introduction,
                        'hash_tag': hash_tag_str,
                        'recent_update': recent_update
                    })
                # 이미지 정보가 없다면
                else:
                    # 시리즈 업로드 (기본 이미지 사용).
                    current_app.database.execute(text("""
                                        INSERT INTO Series( author_id, author_name, title, image, date, introduction, hash_tag, recent_update )
                                          VALUES( :author_id , :author_name , :title , :image_url , :date , :introduction , :hash_tag , :recent_update );
                                    """), {
                        'author_id': author_id,
                        'author_name': author_name,
                        'title': title,
                        'image_url': noimage_url,
                        'date': date,
                        'introduction': introduction,
                        'hash_tag': hash_tag_str,
                        'recent_update': recent_update
                    })

                # Author DB의 series_num 값도 하나 증가시킴.
                current_app.database.execute(text("""
                                                UPDATE User SET series_num=series_num+1 WHERE id = :author_id ;
                                            """), {
                    'author_id': author_id
                })

                return jsonify(
                    {
                        "result": "success",
                        "contents": "success"
                    }
                )
            # 기존 글 수정이면 1
            elif is_new == 1:

                # 시리즈 정보를 가져옴.
                author_id = int(request.form['id'])
                author_name = request.form['name']
                title = request.form['title']
                date = time.strftime('%y.%m.%d')
                introduction = request.form['introduction']
                hash_tag = request.form['hash_tag'],
                recent_update = time.strftime('%y.%m.%d')

                # 등록된 글의 id값을 파라미터로 받는다.
                writing_id = int(request.form['writing_id'])
                # 이미지를 가져옴.
                image = request.files['image']
                # 이미지 업로드.
                image_url = image_upload_api.upload_image(image, "series")

                # id에 해당하는 시리즈의 내용을 수정한다.

                current_app.database.execute(text("""
                                    UPDATE Series SET title = :title, image_url = :image_url, introduction = :introduction, hash_tag = :hash_tag
                                    

                                """), {
                    'title': title,
                    'image_url': image_url,
                    'introduction': introduction,
                    'hash_tag': hash_tag

                })

                # 결과 리턴
                return jsonify(
                    {
                        'result': 'success',
                        'contents': 'success'
                    }
                )


@Series.route('/delete')
class Series_Delete11(Resource):
    @jwt_required
    def post(self):
        """시리즈를 삭제함."""
        # 토큰값을 가져옴.
        current_user = get_jwt_identity()
        series_id = int(request.form['id'])
        author_id = int(request.form['author_id'])

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
                                        DELETE FROM Series WHERE id = :series_id ;
                                    """), {
                'series_id': series_id
            })

            # Author DB의 series_num 값도 하나 감소시킴.
            current_app.database.execute(text("""
                                            UPDATE User SET series_num=series_num-1 WHERE id = :author_id ;
                                        """), {
                'author_id': author_id
            })

            # 3. 결과값 대충 리턴
            return jsonify(
                {
                    'result': 'success',
                    'contents': 'success'
                }
            )


@Series.route('/finished')
class Series_List_End(Resource):
    def post(self):
        """완결된 작품 목록을 불러옴. 0(시간순), 1(ㄱㄴㄷ순)"""
        # 1. 정렬 조건을 parameter로 받아옴.
        sort = request.form['sort']

        # 3. 최신순 정렬인 경우 -> id 내림차순 순서대로 쿼리.
        if sort == '0':
            series_list = current_app.database.execute(text("""
                                                         SELECT * FROM Series WHERE is_end = 1 AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY id DESC; 
                                            """)).fetchall()
        # ㄱㄴㄷ순 정렬
        else:
            series_list = current_app.database.execute(text("""
                                                         SELECT * FROM Series WHERE is_end = 1 AND id IN (SELECT DISTINCT series_id FROM Writing WHERE permission=1) ORDER BY title;
                                                    """)).fetchall()

        if len(series_list) > 0:
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
                    'writing_num': series['writing_num'],
                    'is_end': True,
                } for series in series_list]
            )
        else:
            return jsonify([])

