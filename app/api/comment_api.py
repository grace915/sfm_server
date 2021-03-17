from flask import request, current_app, jsonify
from flask_restx import Resource, Api, Namespace, fields
from flask_jwt_extended import *
from sqlalchemy import text
import time

from . import image_upload_api

Comment = Namespace(
    name='Comment',
    description="댓글 API 모음."
)


@Comment.route('/list')
class Comment_List_All(Resource):
    def post(self):
        """글 id에 해당하는 모든 댓글 정보를 가져옴."""
        # 1. 글 id를 parameter로 받아옴.
        user_id = int(request.form['user_id'])
        writing_id = int(request.form['writing_id'])

        # 2. 글 id에 해당하는 모든 댓글 정보를 DB에서 가져옴

        comment_list = current_app.database.execute(text("""
                                                        SELECT * FROM Comment WHERE writing_id = :writing_id ORDER BY id DESC; 
                                                        """), {
            'writing_id': writing_id
        }).fetchall()

        # 3. 신고여부 확인

        if user_id != 0:
            report_info = current_app.database.execute(text("""
                                                            SELECT * FROM Report_comment WHERE reporter_id = :reporter_id; 
                                                            """), {
                'reporter_id': user_id
            }).fetchall()

            if report_info is None:
                report_result = False
            else:
                report_result = True
        else:
            report_result = False

        # 4. 등록된 댓글이 있다면 모든 댓글의 정보를 리턴.

        if len(comment_list) > 0:
            d_comment_list = []
            for comment in comment_list:
                d_comment = dict(comment)
                if d_comment['is_modified'] == 1:
                    d_comment['is_modified'] = True
                else:
                    d_comment['is_modified'] = False

                d_comment_list.append(d_comment)

            return jsonify(
                [{
                    'id': comment['id'],
                    'writing_id': comment['writing_id'],
                    'user_name': comment['user_name'],
                    'user_id': comment['user_id'],
                    'comment': comment['comment'],
                    'report_count': comment['report_count'],
                    'date': comment['date'],
                    'is_modified': comment['is_modified'],
                    'is_report': report_result
                } for comment in d_comment_list]
            )
            # 4. 등록된 글이 없다면 204(No Content) 리턴.
        else:
            return jsonify([]), 204


@Comment.route('/upload')
class Comment_Upload(Resource):
    @jwt_required
    def post(self):
        """새 댓글을 등록함 전체 내용을 DB에 등록함."""
        # 토큰값을 가져옴.
        current_user = get_jwt_identity()

        # 토큰값이 잘못된 경우
        if current_user is None:
            # 401(Unauthorized)를 리턴한다.
            return jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401
        # 토큰값이 정상인 경우
        else:
            # 시리즈 정보를 가져옴.
            user_id = int(request.form['user_id'])
            user_name = request.form['name']
            writing_id = int(request.form['writing_id'])
            comment = request.form['comment']
            date = time.strftime('%y.%m.%d')

            # 댓글 업로드
            current_app.database.execute(text("""
                                    INSERT INTO Comment( writing_id, user_id, comment, date, user_name)
                                      VALUES( :writing_id , :user_id , :comment , :date , :user_name);
                                """), {
                'writing_id': writing_id,
                'user_id': user_id,
                'comment': comment,
                'date': date,
                'user_name': user_name
            })

            # Writing DB의 comment_num 값도 하나 증가시킴.
            current_app.database.execute(text("""
                                            UPDATE Writing SET comment_num=comment_num+1 WHERE id = :writing_id ;
                                        """), {
                'writing_id': writing_id
            })

            return jsonify(
                {
                    "result": "success",
                    "contents": "success"
                }
            )


@Comment.route('/delete')
class Comment_Delete(Resource):
    @jwt_required
    def post(self):
        """댓글 id에 해당하는 댓글을 삭제함"""
        # 토큰값을 가져옴.
        current_user = get_jwt_identity()
        # 1. 댓글 id, 유저 id, writing_id 를 parameter로 받아옴.
        comment_id = int(request.form['id'])
        user_id = int(request.form['user_id'])
        writing_id = int(request.form['writing_id'])

        # 토큰값이 잘못된 경우
        if current_user is None:
            # 401(Unauthorized)를 리턴한다.
            return jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401
        # 토큰값이 정상인 경우
        else:
            # id에 해당하는 글의 내용을 삭제한다.
            current_app.database.execute(text("""
                                                           DELETE FROM Comment WHERE id = :comment_id;
                                                       """), {
                'writing_id': writing_id,
                'user_id': user_id
            })
            # !!!!댓글 숫자 줄이기!!!!
            # 살짝 햇갈림
            current_app.database.execute(text("""
                                                        UPDATE Writing SET comment_num=comment_num-1 WHERE id = :writing_id ;
                                                    """), {
                'writing_id': writing_id
            })

            # 3. 결과값 리턴
            return jsonify(
                {
                    'result': 'success',
                    'contents': 'success'
                }
            )


@Comment.route('/modify')
class Comment_Modify(Resource):
    @jwt_required
    def post(self):
        # 토큰값을 가져옴.
        current_user = get_jwt_identity()
        # 댓글, 댓글아이디, 유저아이디, 글아이디, 시간 불러옴
        comment_id = int(request.form['id'])
        user_id = int(request.form['user_id'])
        writing_id = int(request.form['writing_id'])
        date = time.strftime('%y.%m.%d')
        comment = request.form['comment']

        # 기존 댓글 보여주는건 Intent로!

        if current_user is None:
            # 401(Unauthorized)를 리턴한다.
            return jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401
        # 토큰값이 정상인 경우
        else:
            # id에 해당하는 댓글의 내용을 수정한다.
            current_app.database.execute(text("""
                                                            UPDATE Comment SET date = :date, comment = :comment,  WHERE id = :comment_id;
                                                        """), {
                'date': date,
                'comment': comment,
                'comment_id': comment_id
            })

            # 결과 리턴
            return jsonify(
                {
                    'result': 'success',
                    'contents': 'success'
                }
            )


@Comment.route('/report')
class Comment_Report(Resource):
    @jwt_required
    def post(self):
        """ 댓글 신고 """

        # 토큰값 가져옴
        current_user = get_jwt_identify()

        if current_user is None:

            return jsonify({
                "result": "fail",
                "contents": "잘못된 토큰값입니다."
            }), 401

        # 토큰값 정상
        else:
            comment_id = int(request.form['comment_id'])  # 댓글 id
            writing_id = int(request.form['writing_id'])  # 글 id
            reporter_id = int(request.form['reporter_id'])  # 신고자 id
            contents = request.form['contents']  # 신고 사유

            # is_report 업데이트 (true로)
            current_app.database.excute(text("""
                            UPDATE Report_comment SET is_report = :is_report
                            WHERE reporter_id = :reporter_id;
            """), {
                'is_report': True,
                'reporter_id': reporter_id
            })

            # 신고 사유 업데이트
            current_app.database.excute(text("""
                            UPDATE Report_comment SET contents = :contents
                            WHERE reporter_id = :reporter_id
            """), {
                'contents': contents,
                'reporter_id': reporter_id
            })

            # 총 신고수 가져오기
            count = current_app.database.excute(text("""
                            SELECT count(*) FROM Comment, Report_comment
                            WHERE comment_id = :comment_id AND id = comment_id;
            """), {
                'comment_id': comment_id
            }).fetchall()

            # 신고수 10개 이상이면 자동 삭제
            if count > 9:
                current_app.database.excute(text("""
                            DELETE FROM Comment,  WHERE id = :comment_id;
                """), {
                    'comment_id': comment_id
                })

                current_app.database.excute(text("""
                            UPDATE Writing SET comment_num = comment_num-1
                            WHERE id = :writing_id;
                """), {
                    'writing_id': writing_id
                })

