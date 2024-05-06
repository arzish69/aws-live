from flask import Flask, render_template, request, redirect
from pymysql import connections, IntegrityError
import boto3
from botocore.exceptions import ClientError
import base64

app = Flask(__name__)
s3_client = boto3.client(
        's3',
        aws_access_key_id='AKIAXYKJTNYMMGEVGBEK',
        aws_secret_access_key='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'
    )

def retrieve_image_from_s3(s3_client, bucket_name, key):
    try:
        # Get the image object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        
        # Read and encode the image data as base64
        image_data = response['Body'].read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        # Check if the image is PNG format
        if key.endswith('.png'):
            return encoded_image
        else:
            print("Error: Image format is not PNG.")
            return None

    except ClientError as e:
        # Handle any errors (e.g., image not found)
        print(f"Error retrieving image from S3: {e}")
        return None

db_conn = connections.Connection(
    host="doctor.c3o8uuyq6j6l.eu-north-1.rds.amazonaws.com",
    port=3306,
    user="admin",
    password="admin123",
    db="doctor"
)

try:
    with db_conn.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("Connected to MySQL database successfully!")

except Exception as e:
    print("Error connecting to MySQL database:", e)

output = {}
table = 'doctor'

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')

@app.route("/about", methods=['GET', 'POST'])
def about_page():
    return redirect('https://www.xavier.ac.in/')

@app.route("/getemp", methods=['GET', 'POST'])
def put_id():
    return render_template('GetEmp.html')

@app.route("/fetchdata", methods=['POST'])
def fetching():
    emp_id = request.form['emp_id']
    employ_no = None

    with db_conn.cursor() as cursor:
            # Fetch data from the database based on the employee ID
            cursor.execute("SELECT * FROM doctor WHERE empid = %s", (emp_id))
            result = cursor.fetchone()  # Assuming there's only one record for the given ID
            if result:
            # Accessing individual columns of the result tuple
                employ_no = result[0]
                first_name = result[1]
                last_name = result[2]
                pri_skill = result[3]
                location = result[4]
                image_png = retrieve_image_from_s3(s3_client,'addempimg',f'{employ_no}.png')

                return render_template('GetEmpOutput.html', id=employ_no, fname=first_name,
                                       lname=last_name, interest=pri_skill,
                                       location=location,image_png=image_png)
            else:
                return render_template('NoFetchOut.html', id=emp_id)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO doctor VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = first_name + " " + last_name

        # Upload image file to S3
        if 'emp_image_file' not in request.files:
            return 'No file part'

        if emp_image_file.filename == '':
            return 'No selected file'

        # Upload file to S3
        try:
            s3_client.upload_fileobj(emp_image_file, 'addempimg', emp_image_file.filename)
            print('File uploaded successfully')
        except Exception as e:
            return f'Error uploading file: {str(e)}'

    except IntegrityError as ie:
        db_conn.rollback()  # Rollback the transaction
        return render_template('Dupe.html')  # Render a template for duplicate emp_id error

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    print("All modifications done...")
    return render_template('AddEmpOutput.html', name=emp_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)