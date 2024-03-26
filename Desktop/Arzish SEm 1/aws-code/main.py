from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)

# MySQL RDS database configuration
db_config = {
    'host': 'employee.c3o8uuyq6j6l.eu-north-1.rds.amazonaws.com',
    'user': 'arzish',
    'password': 'arzishrocks',
    'database': 'employee',
    'port': 3306
}

def connect_to_database():
    return pymysql.connect(**db_config)

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    # Connect to the database
    db_conn = connect_to_database()
    cursor = db_conn.cursor()

    # Sample data processing with database connection
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']

    # Insert employee data into the database
    insert_sql = "INSERT INTO employee (emp_id, first_name, last_name, pri_skill, location) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
    db_conn.commit()

    emp_name = first_name + " " + last_name
    print("Employee name:", emp_name)

    # Close database connection
    cursor.close()
    db_conn.close()

    return render_template('AddEmpOutput.html', name=emp_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)