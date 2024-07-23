from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)  # More secure way to set secret key
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to establish database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='S@Ndhyavalmiki10',
        database='portfolio_db'
    )

# Route for login
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            qry = "SELECT * FROM admin WHERE username = %s AND password = %s"
            cursor.execute(qry, (username, password))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['userid'] = account['admin_id']  # Corrected session key to 'userid'
                session['username'] = account['username']
                msg = 'Logged in successfully!'
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect username/password!'
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            msg = 'An error occurred. Please try again later.'
        finally:
            cursor.close()
            connection.close()
    return render_template('login.html', msg=msg)

# Route for signup
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            else:
                cursor.execute("INSERT INTO admin (username, password) VALUES (%s, %s)", (username, password))
                connection.commit()
                msg = 'You have successfully registered!'
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            msg = 'An error occurred. Please try again later.'
        finally:
            cursor.close()
            connection.close()
    return render_template('sign_up.html', msg=msg)

# Route for home page
@app.route('/home')
def home():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM admin WHERE admin_id = %s', (session['userid'],))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('home.html', user=user)
    return redirect(url_for('login'))

# Route for about page
@app.route('/about')
def about():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM admin WHERE admin_id = %s', (session['userid'],))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('about.html', user=user)
    return redirect(url_for('login'))

# Route for project gallery
@app.route('/project_gallery')
def project_gallery():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM projects')
        projects = cursor.fetchall()
        cursor.execute('SELECT * FROM admin WHERE admin_id = %s', (session['userid'],))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('project_gallery.html', projects=projects, user=user)
    return redirect(url_for('login'))

# Route for resume
@app.route('/resume')
def resume():
    if 'loggedin' in session:
        user_id = session['userid']
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM experiences WHERE user_id = %s", (user_id,))
            experience = cursor.fetchall()
            
            cursor.execute("SELECT * FROM education WHERE user_id = %s", (user_id,))
            education = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            resume = {
                'experiences': experience,
                'education': education
            }
            
            return render_template('resume.html', user=session['username'], resume=resume)
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            flash('An error occurred. Please try again later.', 'danger')
            if connection:
                connection.rollback()
    return redirect(url_for('login'))

# Route for contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']
            
            # Server-side validation
            if not name or not email or not message:
                flash('Please fill out all fields', 'danger')
                return redirect(url_for('contact'))
            
            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                insert_query = "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (name, email, message))
                connection.commit()
                flash('Message sent successfully', 'success')
            except mysql.connector.Error as e:
                print("Error executing SQL query:", e)
                flash('Failed to send message', 'danger')
                connection.rollback()
            finally:
                cursor.close()
                connection.close()
            return redirect(url_for('contact'))
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM admin WHERE admin_id = %s', (session['userid'],))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('contact.html', user=user)
    return redirect(url_for('login'))

# Route for admin dashboard
@app.route('/admin/admin_dashboard', methods=['GET'])
def admin_dashboard():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM projects")
        projects = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('admin_dashboard.html', projects=projects)
    return redirect(url_for('login'))

# Route for adding a project
@app.route('/admin/add_project', methods=['GET', 'POST'])
def add_project():
    if 'loggedin' in session:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            technologies = request.form['technologies']
            project_url = request.form['project_url']
            source_url = request.form['source_url']

            # Check if the post request has the file part
            if 'image' not in request.files:
                flash('No file part', 'danger')
                return redirect(request.url)
            file = request.files['image']
            # If the user does not select a file, the browser submits an empty part without filename
            if file.filename == '':
                flash('No selected file', 'danger')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                if not title or not description or not technologies or not project_url or not source_url:
                    flash('Please fill out all fields', 'danger')
                    return redirect(url_for('add_project'))

                try:
                    connection = get_db_connection()
                    cursor = connection.cursor()

                    insert_query = """
                        INSERT INTO projects (title, description, technologies, image_url, project_url, source_url, user_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (title, description, technologies, image_url, project_url, source_url, session['userid']))
                    connection.commit()
                    flash('Project added successfully', 'success')
                    cursor.close()
                    connection.close()
                except mysql.connector.Error as e:
                    print("Error executing SQL query:", e)
                    flash('Failed to add project', 'danger')
                return redirect(url_for('admin_dashboard'))
        
        return render_template('add_project.html')

    return redirect(url_for('login'))

# Route for viewing projects
@app.route('/admin/view_projects', methods=['GET'])
def view_projects():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM projects")
        projects = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('view_projects.html', projects=projects)
    return redirect(url_for('login'))

# Route for editing a project
@app.route('/admin/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM projects WHERE project_id = %s", (project_id,))
        project = cursor.fetchone()

        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            technologies = request.form['technologies']
            project_url = request.form['project_url']
            source_url = request.form['source_url']
            file = request.files['image']

            # Check if the file is selected and is allowed
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                cursor.execute("""
                    UPDATE projects
                    SET title = %s, description = %s, technologies = %s, image_url = %s, project_url = %s, source_url = %s
                    WHERE project_id = %s
                """, (title, description, technologies, image_url, project_url, source_url, project_id))
            else:
                cursor.execute("""
                    UPDATE projects
                    SET title = %s, description = %s, technologies = %s, project_url = %s, source_url = %s
                    WHERE project_id = %s
                """, (title, description, technologies, project_url, source_url, project_id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Project updated successfully', 'success')
            return redirect(url_for('view_projects'))
        
        cursor.close()
        connection.close()
        return render_template('edit_project.html', project=project)
    return redirect(url_for('login'))

# Route for deleting a project
@app.route('/admin/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM projects WHERE project_id = %s", (project_id,))
            connection.commit()
            flash('Project deleted successfully', 'success')
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            flash('Failed to delete project', 'danger')
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
        return redirect(url_for('view_projects'))
    return redirect(url_for('login'))

# Route for logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('username', None)
    flash('You have successfully logged out', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
