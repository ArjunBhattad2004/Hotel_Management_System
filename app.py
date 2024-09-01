from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Configure session management
app.secret_key = app.config['SECRET_KEY']

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user WHERE username = %s", [username])
        if cur.fetchone():
            flash('Username already exists.', 'danger')
            cur.close()
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cur.execute("INSERT INTO user (username, password, role) VALUES (%s, %s, %s)", (username, hashed_password, role))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful, please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM user WHERE username = %s", [username])
        if result > 0:
            data = cur.fetchone()
            hashed_password = data[2]
            if bcrypt.check_password_hash(hashed_password, password_candidate):
                session['logged_in'] = True  # Set session variable to track login status
                session['username'] = username
                flash('Login successful.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid login. Try again.', 'danger')
        else:
            flash('User not found. Please register.', 'danger')
        cur.close()

    return render_template('login.html')

@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_no = request.form['room_no']
        room_type = request.form['room_type']
        status = request.form['status']
        price = request.form['price']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Room (Room_No, Room_Type, Status, Price) VALUES (%s, %s, %s, %s)",
                    (room_no, room_type, status, price))
        mysql.connection.commit()
        cur.close()
        flash('Room added successfully.', 'success')
        return redirect(url_for('home'))
    
    # Fetch all rooms from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM room")
    rooms = cur.fetchall()  # Fetch all rows from the Room table
    cur.close()

    return render_template('add_room.html', room = rooms)


@app.route('/manage_bookings', methods=['GET', 'POST'])
def manage_bookings():
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        status = request.form['status']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE Booking SET Booking_Status=%s WHERE Booking_Id=%s", (str(status), booking_id))
        mysql.connection.commit()
        cur.close()
        flash('Booking updated successfully.', 'success')
        return redirect(url_for('manage_bookings'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM booking")
    booking = cur.fetchall()

    cur.close()
    return render_template('manage_bookings.html', bookings = booking)




@app.route('/process_payment', methods=['GET', 'POST'])
def process_payment():
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        amount = request.form['amount']
        payment_date = request.form['payment_date']
        payment_method = request.form['payment_method']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO payment (Booking_Id, Amount, Payment_Date, Payment_Method) VALUES (%s, %s, %s, %s)",
                    (booking_id, amount,payment_date, payment_method))
        mysql.connection.commit()
        cur.close()
        flash('Payment processed successfully.', 'success')
        return redirect(url_for('home'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Booking WHERE Booking_Status = 'Confirmed'")
    bookings = cur.fetchall()
    cur.close()
    return render_template('process_payment.html', booking=bookings)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# Home route
@app.route('/')
def home():
    # Check if the user is logged in
    if 'logged_in' in session and session['logged_in']:
        return render_template('home.html')  # Render the home page if logged in
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
