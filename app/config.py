# https://velog.io/@inyong_pang/Flask-API-MySQL-%EC%97%B0%EB%8F%99-SQLAlchemy
db = {
    'user'     : 'admin',
    'password' : 'eosHeroine',
    'host'     : 'admin.cfw3muarvznt.ap-northeast-2.rds.amazonaws.com',
    'port'     : 3306,
    'database' : 'eosHeroine'
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

# 토큰 생성에 사용될 Secret Key를 flask 환경변수에 등록함.
JWT_SECRET_KEY = 'EOS_HEROINE_KEY'

# AWS S3 접근을 위한 값들
AWS_ACCESS_KEY = "AKIAIOVNZGTN27IG7FDA"
AWS_SECRET_KEY = "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"
BUCKET_NAME = "huhsapi.src"

