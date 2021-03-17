# 2020.12.28 made by Candykick(우수몽)
import boto3
import time
from PIL import Image
from flask import request, current_app, jsonify
from flask_restx import Resource, Api, Namespace, fields

Images = Namespace(
    name='Images',
    description="이미지 업로드 관리."
)

# S3에 접속하는 함수
def s3_connect():
    s3 = boto3.client('s3',
                      aws_access_key_id = "AKIAIOVNZGTN27IG7FDA",
                      aws_secret_access_key = "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")
    return s3

# S3에 이미지 업로드하는 함수.
# image는 이미지 파일, path는 업로드 경로.
def upload_image(image, path):
    s3 = s3_connect()
    imagename = str(time.strftime('%Y%m%d%H%M%S%w'))+image.filename

    s3.put_object(
        Bucket = "eos.heroine",
        Body = image,
        Key = path+"/"+imagename,
        ContentType = image.content_type
    )

    # 업로드한 이미지의 주소 반환
    image_url = f'https://s3.ap-northeast-2.amazonaws.com/eos.heroine/{path}/{imagename}'
    return image_url

def image_resize_test(img):
    w = img.width
    h = img.height
    if img.width > img.height and img.height > 800:
        ratio = 800/img.height
        h = 800
        w = img.width * ratio
    elif img.width <= img.height and img.width > 800:
        ratio = 800/img.width
        w = 800
        h = img.height * ratio

    img_resize = img.resize((int(w), int(h)))
    return img_resize

@Images.route('/upload')
class Image_Upload(Resource):
    def post(self):
        """이미지를 업로드함."""
        # 이미지를 가져옴.
        img = request.files['image']
        # 이미지 업로드하고 url 받아옴
        image_url = upload_image(img, "writing")

        return jsonify(
            {
                'img': image_url
            })

@Images.route('/upload2')
class Image_Upload2(Resource):
    def post(self):
        """이미지 여러 장을 업로드함."""
        # 이미지를 가져옴.
        files = request.files.getlist("images[]")

        img_url = []
        for file in files:
            # 이미지 업로드하고 url 받아옴
            image_url = upload_image(file, "writing")
            img_url.append(image_url)

        return jsonify(
            [
                    img
                for img in img_url])

