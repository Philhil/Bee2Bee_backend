import awsgi
from app import create_app

app = create_app()

def lambda_handler(event, context):
    return awsgi.response(app, event, context)