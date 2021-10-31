import os

print(
    os.environ.get('DB_BUCKET'),
    os.environ.get('DB_ORG'),
    os.environ.get('DB_TOKEN'),
    os.environ.get('DB_URL')
)