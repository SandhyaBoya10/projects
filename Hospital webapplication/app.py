from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Function to establish database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='S@Ndhyavalmiki10',
            database='hospital_db'
        )
        cursor = connection.cursor()
        return connection, cursor
    except mysql.connector.Error as e:
        print('Error connecting to MySQL:', e)
        return None, None

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/doctor')
def doctor():
    return render_template('doctor.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/display', methods=['POST'])
def display():
    if request.method == 'POST':
        # Print form data for debugging
        print("Form Data:", request.form)
        
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        gender = request.form.get('gender')
        date = request.form.get('date')
        comment = request.form.get('comment')

        try:
            connection, cursor = get_db_connection()
            if connection is None or cursor is None:
                return "Database connection error"
            
            insert_query = """
                INSERT INTO appointments (fname, lname, email, mobile, gender, date, comment)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (fname, lname, email, mobile, gender, date, comment))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('dashboard'))
        
        except mysql.connector.Error as er:
            print('System error:', er)
            return "Database error during insertion"

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    try:
        connection, cursor = get_db_connection()
        if connection is None or cursor is None:
            return "Database connection error"
        
        cursor.execute("SELECT * FROM appointments")
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('dashboard.html', data=data)
    
    except mysql.connector.Error as e:
        print("System error:", e)
        return "Error fetching data from the database"

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if request.method == 'GET':
        try:
            connection, cursor = get_db_connection()
            if connection is None or cursor is None:
                return "Database connection error"

            cursor.execute('SELECT * FROM appointments WHERE id = %s', (id,))
            data = cursor.fetchone()
            cursor.close()
            connection.close()

            if data:
                return render_template('edit.html', data=data)
            else:
                return "Appointment not found"

        except mysql.connector.Error as e:
            print("System error during fetch:", e)
            return "Error fetching data from the database"

    elif request.method == 'POST':
        try:
            connection, cursor = get_db_connection()
            if connection is None or cursor is None:
                return "Database connection error"

            # Print form data for debugging
            print("Form Data:", request.form)
            
            id = request.form.get('id')
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            email = request.form.get('email')
            mobile = request.form.get('mobile')
            gender = request.form.get('gender')
            date = request.form.get('date')
            comment = request.form.get('comment')

            update_query = """
                UPDATE appointments 
                SET fname=%s, lname=%s, email=%s, mobile=%s, gender=%s, date=%s, comment=%s 
                WHERE id=%s
            """
            cursor.execute(update_query, (fname, lname, email, mobile, gender, date, comment, id))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('dashboard'))

        except mysql.connector.Error as er:
            print('System error during update:', er)
            return "Database error during update"

    else:
        return "Invalid request method"

@app.route('/delete/<int:id>')
def delete(id):
    try:
        connection, cursor = get_db_connection()
        if connection is None or cursor is None:
            return "Database connection error"

        cursor.execute('DELETE FROM appointments WHERE id = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('dashboard'))

    except mysql.connector.Error as e:
        print("System error during delete:", e)
        return "Error deleting data from the database"

if __name__ == '__main__':
    app.run(debug=True)
