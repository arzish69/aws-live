from flask import Flask, render_template, request
import pymysql
import boto3

app = Flask(__name__)

# Database connection configuration
db_config = {
    'host': 'employee.c3o8uuyq6j6l.eu-north-1.rds.amazonaws.com',
    'user': 'arzish',
    'password': 'arzishrocks',
    'database': 'employee',
    'port': 3306  # Change if necessary
}

# S3 configuration
s3 = boto3.client('s3', region_name='eu-north-1')
bucket_name = 'addemployee'

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    if emp_image_file.filename == "":
        return "Please select a file"

    # Connect to the database
    db_conn = pymysql.connect(**db_config)

    # Insert data into MySQL database
    insert_sql = "INSERT INTO employee (emp_id, first_name, last_name, pri_skill, location) VALUES (%s, %s, %s, %s, %s)"
    try:
        with db_conn.cursor() as cursor:
            cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
            db_conn.commit()
        print("Data inserted into MySQL RDS")
    except Exception as e:
        return "Error inserting data into MySQL RDS: " + str(e)
    finally:
        db_conn.close()

    # Upload image file to S3
    try:
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3.upload_fileobj(emp_image_file, bucket_name, emp_image_file_name_in_s3)
        print("Image uploaded to S3")
    except Exception as e:
        return "Error uploading image to S3: " + str(e)

    emp_name = f"{first_name} {last_name}"
    print("All modifications done...")
    return render_template('AddEmpOutput.html', name=emp_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
