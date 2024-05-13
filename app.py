from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flaskext.mysql import MySQL
import boto3
import json

app = Flask(__name__)
api = Api(app)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'your_mysql_user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DATABASE_DB'] = 'your_database'
app.config['MYSQL_DATABASE_HOST'] = 'your_mysql_host'

mysql = MySQL()
mysql.init_app(app)

# AWS S3 configurations
s3 = boto3.client('s3', aws_access_key_id='your_aws_access_key', aws_secret_access_key='your_aws_secret_key')
bucket_name = 'your_s3_bucket_name'

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

api.add_resource(Name, '/name')

if __name__ == '__main__':
    app.run(debug=True)
