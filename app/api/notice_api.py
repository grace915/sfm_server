# 2020.12.27 made by Candykick(우수몽)

from flask import request, current_app, jsonify
from flask_restx import Resource, Api, Namespace, fields
from sqlalchemy import text
import time

Notice = Namespace(
    name='Notice',
    description="공지사항 정보를 관리하는 API 모음."
)

@Notice.route('')
class Notice_List(Resource):
    def post(self):
        """공지사항 목록을 가져옴."""
        notice_list = current_app.database.execute(text("""
                                        SELECT * FROM Notice ORDER BY id DESC;
                                    """)).fetchall()

        if len(notice_list) > 0:
            return jsonify(
                [{
                    'id': notice['id'],
                    'title': notice['title'],
                    'contents': notice['contents'],
                    'date': notice['date'],
                    'watcher': notice['hit']
                } for notice in notice_list]
            )
        else:
            return [], 204

@Notice.route('/upload')
class Notice_Upload(Resource):
    def post(self):
        """공지사항을 업로드함."""
        title = request.form['title']
        contents = request.form['contents']
        date = time.strftime('%y.%m.%d')

        current_app.database.execute(text("""
                                        INSERT INTO Notice(title, contents, date) VALUE ( :title, :contents, :date );
                                    """), {
            'title': title,
            'contents': contents,
            'date': date
        })

        return jsonify(
            {
                'result': 'success',
                'contents': 'success'
            }
        )

