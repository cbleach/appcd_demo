from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flaskext.mysql import MySQL
import boto3
import json
import os

app = Flask(__name__)
api = Api(app)

# MySQL configurations using AWS RDS
app.config['MYSQL_DATABASE_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.environ.get('MYSQL_DB')
app.config['MYSQL_DATABASE_HOST'] = os.environ.get('MYSQL_HOST')

mysql = MySQL()
mysql.init_app(app)

# AWS S3 configurations
s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)
bucket_name = os.environ.get('S3_BUCKET_NAME')

# AWS RDS client
rds_client = boto3.client(
    'rds',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION')
)

class Name(Resource):
    def post(self):
        data = request.get_json()
        firstname = data.get('firstname')
        lastname = data.get('lastname')

        if not firstname or not lastname:
            return {"error": "Firstname and lastname are required"}, 400

        # Save to MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO names (firstname, lastname) VALUES (%s, %s)", (firstname, lastname))
        conn.commit()
        cursor.close()
        conn.close()

        # Save to S3
        name_data = json.dumps({"firstname": firstname, "lastname": lastname})
        s3.put_object(Bucket=bucket_name, Key=f'{firstname}_{lastname}.json', Body=name_data)

        return {"message": "Name added successfully"}, 201

class RDSInstances(Resource):
    def get(self):
        try:
            instances = rds_client.describe_db_instances()
            db_instances = instances['DBInstances']
            return jsonify(db_instances)
        except Exception as e:
            return {"error": str(e)}, 500

api.add_resource(Name, '/name')
api.add_resource(RDSInstances, '/rds-instances')

if __name__ == '__main__':
    app.run(debug=True)