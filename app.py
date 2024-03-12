from flask import Flask, render_template, request, g, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)

# Set the secret key for session management
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Define the database path
DATABASE = 'turf_booking.db'


# Create the database tables
def create_tables():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# Connect to the database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


# Close the database connection when the app is closed
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


# Routes for HTML files

@app.route('/add_location', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location_name = request.form['location']
        if location_name:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO locations (name) VALUES (?)", (location_name,))
            db.commit()
    return render_template('add_location.html', l=get_locations())


@app.route('/add_manager', methods=['GET', 'POST'])
def add_manager():
    if request.method == 'POST':
        manager_username = request.form['muname']
        manager_password = request.form['mpass']
        if manager_username and manager_password:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO managers (username, password) VALUES (?, ?)",
                           (manager_username, manager_password))
            db.commit()
    return render_template('add_manager.html', mavail=get_managers())


@app.route('/add_price', methods=['GET', 'POST'])
def add_price():
    if request.method == 'POST':
        location_name = request.form['loc']
        price_value = request.form['price']
        if location_name and price_value:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO prices (location_id, price) VALUES (?, ?)",
                           (get_location_id(location_name), price_value))
            db.commit()
    return render_template('add_price.html', p=get_prices())


@app.route('/allocate_manager', methods=['GET', 'POST'])
def allocate_manager():
    if request.method == 'POST':
        manager_name = request.form['man']
        location_name = request.form['loc']
        if manager_name and location_name:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO allocations (manager_id, location_id) VALUES (?, ?)",
                           (get_manager_id(manager_name), get_location_id(location_name)))
            db.commit()
    return render_template('allocate_manager.html', a=get_allocations())


@app.route('/bill_generation', methods=['POST'])
def generate_bill():
    if request.method == 'POST':
        user_username = request.form['usr']
        if user_username:
            db = get_db()
            cursor = db.cursor()
            # Add logic to fetch data and generate the bill
            return render_template('bill_generated.html', u=user_username, l='Location Name', p='Price Value')


# @app.route('/book_turf', methods=['GET', 'POST'])
# def book_turf():
#     if request.method == 'POST':
#         location_name = request.form.get('loc')
#         if location_name:
#             # Retrieve user ID from the database
#             user_id = get_user_id(session.get('username'))
#
#             if user_id:
#                 # Insert booking into the database
#                 date = "your_date_value"  # Replace with the actual date
#                 time = "your_time_value"  # Replace with the actual time
#                 payment_status = "Pending"  # Assuming it's pending initially
#
#                 # Call the function to insert booking details into the user_bookings table
#                 insert_booking_into_database(user_id, location_name, date, time, payment_status)
#
#                 # Redirect to the user's booking history page
#                 return redirect(url_for('user_booking_history'))
#
#     # Render the book_turf page for GET requests or if form submission is not valid
#     return render_template('book_turf.html')


def get_user_id(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

def get_location_id(location_name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM locations WHERE name = ?", (location_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

@app.route('/book_turf', methods=['GET', 'POST'])
def book_turf():
    if request.method == 'POST':
        location_name = request.form.get('location_name')
        booking_date = request.form.get('booking_date')
        booking_time = request.form.get('booking_time')
        if location_name and booking_date and booking_time:
            user_id = get_user_id("user1")  # Replace "user1" with actual username obtained from session or login
            location_id = get_location_id(location_name)
            if user_id and location_id:
                db = get_db()
                cursor = db.cursor()
                cursor.execute("INSERT INTO user_bookings (user_id, location_id, date, time, payment_status) VALUES (?, ?, ?, ?, ?)",
                               (user_id, location_id, booking_date, booking_time, 'Pending'))
                db.commit()
                return redirect(url_for('home_user'))
    else:
        location_name = request.args.get('location_name')
        return render_template('book_turf.html', location_name=location_name)
def insert_booking_into_database(location_name, user_id):
    db = get_db()
    cursor = db.cursor()
    # Modify the query based on your database schema
    cursor.execute("INSERT INTO user_bookings (user_id, location) VALUES (?, ?)", (user_id, location_name))
    db.commit()


def get_user_id(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result['id'] if result else None


@app.route('/booking_history', methods=['POST'])
def booking_history():
    if request.method == 'POST':
        location_name = request.form['loc']
        if location_name:
            db = get_db()
            cursor = db.cursor()
            # Add logic to fetch booking history
            return render_template('booking_history.html', l=location_name,
                                   u=['User1', 'User2'])  # Example data, replace with actual data


@app.route('/check_availability', methods=['GET'])
def check_availability():
    if session.get('user_type') == 'user':
        # Fetch available turf locations from the database
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT location_id FROM prices")
        available_locations_data = cursor.fetchall()

        available_locations = [get_location_name(row['location_id']) for row in available_locations_data]

        return render_template('check_availability.html', available_locations=available_locations)

    return render_template('login.html', error='Unauthorized access.')


@app.route('/check_rates', methods=['GET', 'POST'])
def check_rates():
    if request.method == 'POST':
        # Handle the form submission if needed
        location_name = request.form.get('loc')
        if location_name:
            # Fetch rates for the specified location from the database
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT location_id, price FROM prices WHERE location_id = ?",
                           (get_location_id(location_name),))
            prices = cursor.fetchall()
            rates = [{'location': get_location_name(row['location_id']), 'price': row['price']} for row in prices]

            return render_template('check_rates.html', rates=rates)

    # Render the template for the initial GET request or if the form submission is not valid
    return render_template('check_rates.html')


@app.route('/check_turf', methods=['GET'])
def check_turf():
    if session.get('user_type') == 'user':
        # Fetch turf locations and prices from the database
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT location_id, price FROM prices")
        turf_data = cursor.fetchall()

        turf_list = [{'location': get_location_name(row['location_id']), 'price': row['price']} for row in turf_data]

        return render_template('check_turf.html', turf_list=turf_list)

    return render_template('login.html', error='Unauthorized access.')


@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    return render_template('confirm_booking.html')

# ... (previous code)

def contact_exp():
    # Add logic to handle contact form submission
    return render_template('contact_exp.html')


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')


@app.route('/contact_info', methods=['GET'])
def contact_info():
    return render_template('contact_info.html')


@app.route('/bill_generated', methods=['POST'])
def bill_generated():
    if request.method == 'POST':
        user_username = request.form['usr']
        if user_username:
            db = get_db()
            cursor = db.cursor()
            # Add logic to fetch data and generate the bill
            return render_template('generate_bill.html', u=user_username, l='Location Name', p='Price Value')


# ... (previous routes)

@app.route('/home_admin', methods=['POST'])
def home_admin():
    if session.get('user_type') == 'admin':
        if 'submit_button' in request.form:
            action = request.form['submit_button']

            if action == 'Add turf location':
                # Logic for adding turf location
                return render_template('add_location.html', l=get_locations())

            elif action == 'Provide credentials & Add a manager':
                # Logic for providing credentials and adding a manager
                return render_template('add_manager.html', mavail=get_managers())

            elif action == 'Allocate a manager':
                # Logic for allocating a manager
                return render_template('allocate_manager.html', a=get_allocations())

            elif action == 'Add price list':
                # Logic for adding price list
                return render_template('add_price.html', p=get_prices())

            elif action == 'View Booking':
                # Logic for viewing bookings
                return render_template('view_bookings.html', bookings=['Booking1', 'Booking2'])

            elif action == 'View visits':
                # Logic for viewing visits
                return render_template('view_visits.html', visits=['Visit1', 'Visit2'])

            elif action == 'Contact':
                # Logic for contact
                return render_template('contact.html')

            elif action == 'Log out':
                # Logic for logging out
                session.clear()
                return render_template('login.html')

        return render_template('home_admin.html', email='admin@example.com')
    return render_template('login.html', error='Unauthorized access.')


@app.route('/home_manager', methods=['POST'])
def home_manager():
    if session.get('user_type') == 'manager':
        if request.method == 'POST':
            if 'submit_button' in request.form:
                action = request.form['submit_button']

                # Add logic for different actions here
                if action == 'Check rates':
                    return redirect(url_for('check_rates'))
                elif action == 'View Request':
                    return redirect(url_for('view_requests'))
                elif action == 'Confirm Booking':
                    return redirect(url_for('confirm_booking'))
                elif action == 'Bill Generation':
                    return redirect(url_for('bill_generated'))
                elif action == 'Booking History':
                    return redirect(url_for('booking_history'))
                elif action == 'View visits':
                    # Logic for viewing visits
                    return render_template('view_visits.html', visits=['Visit1', 'Visit2'])

                elif action == 'Contact':
                    # Logic for contact
                    return render_template('contact.html')

                elif action == 'Log out':
                    # Logic for logging out
                    session.clear()
                    return render_template('login.html')
                # Add more actions as needed

        return render_template('home_manager.html', email='manager@example.com')
    return render_template('login.html', error='Unauthorized access.')


# Modify the home_user route
# Modify the home_user route for debugging
@app.route('/home_user', methods=['GET', 'POST'])
def home_user():
    if request.method == 'POST':
        action = request.form.get('submit_button')

        if action == 'Check turf':
            return redirect(url_for('check_turf'))
        elif action == 'Check rates':
            return redirect(url_for('check_rates'))
        elif action == 'Check availability':
            return redirect(url_for('check_availability'))
        elif action == 'Book a turf':
            return redirect(url_for('book_turf'))
        elif action == 'My history':
            return redirect(url_for('user_booking_history'))
        elif action == 'View visits':
            return redirect(url_for('view_visits'))
        elif action == 'Contact':
            return redirect(url_for('contact'))
        elif action == 'Log out':
            return redirect(url_for('logout'))

    # Render the template for the initial GET request or if the form submission is not valid
    return render_template('home_user.html', email=session.get('email'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check against admins
        if check_credentials('admins', username, password):
            session['user_type'] = 'admin'
            return render_template('home_admin.html', email='admin@example.com')

        # Check against managers
        elif check_credentials('managers', username, password):
            session['user_type'] = 'manager'
            return render_template('home_manager.html', email='manager@example.com')

        # Check against users
        elif check_credentials('users', username, password):
            session['user_type'] = 'user'
            return render_template('home_user.html', email='user@example.com')

        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)

    return render_template('login.html', error=None)


@app.route('/my_history', methods=['POST'])
def my_history():
    return render_template('my_history.html', l='Location Name',
                           u=['User1', 'User2'])  # Example data, replace with actual data


@app.route('/view_bookings', methods=['GET'])
def view_bookings():
    db = get_db()
    cursor = db.cursor()
    # Add logic to fetch booking data
    return render_template('view_bookings.html',
                           bookings=['Booking1', 'Booking2'])  # Example data, replace with actual data


@app.route('/view_requests', methods=['GET'])
def view_requests():
    db = get_db()
    cursor = db.cursor()
    # Add logic to fetch booking requests
    return render_template('view_requests.html',
                           requests=['Request1', 'Request2'])  # Example data, replace with actual data


@app.route('/visitors', methods=['GET'])
def visitors():
    db = get_db()
    cursor = db.cursor()
    # Add logic to fetch visitor data
    return render_template('visitors.html', visitors=['Visitor1', 'Visitor2'])  # Example data, replace with actual data


# ... (previous code)

def get_locations():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM locations")
    return [row['name'] for row in cursor.fetchall()]


def get_managers():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT username FROM managers")
    return [row['username'] for row in cursor.fetchall()]


def get_prices():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT location_id, price FROM prices")
    return [(get_location_name(row['location_id']), row['price']) for row in cursor.fetchall()]


def get_allocations():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT manager_id, location_id FROM allocations")
    return [(get_manager_name(row['manager_id']), get_location_name(row['location_id'])) for row in cursor.fetchall()]


def get_location_name(location_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM locations WHERE id = ?", (location_id,))
    result = cursor.fetchone()
    return result['name'] if result else None


def get_manager_name(manager_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT username FROM managers WHERE id = ?", (manager_id,))
    result = cursor.fetchone()
    return result['username'] if result else None


def get_location_id(location_name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM locations WHERE name = ?", (location_name,))
    result = cursor.fetchone()
    return result['id'] if result else None


def get_manager_id(manager_name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM managers WHERE username = ?", (manager_name,))
    result = cursor.fetchone()
    return result['id'] if result else None


# ... (previous code)

def check_credentials(user_type, username, password):
    db = get_db()
    cursor = db.cursor()

    if user_type == 'admins':
        # Allow only a specific admin username and password
        allowed_admin_username = 'admin'
        allowed_admin_password = 'admin_password'
        if username == allowed_admin_username and password == allowed_admin_password:
            return True
        else:
            return False

    # For other user types, check against the database
    cursor.execute(f"SELECT * FROM {user_type} WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    return result is not None


# ... (Previous code)

# Add new route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect(url_for('login'))
    return render_template('register.html')


# Add new route for user booking history
# @app.route('/user_booking_history', methods=['GET'])
# def user_booking_history():
#     if session.get('user_type') == 'user':
#         # Fetch user's booking history from the database
#         db = get_db()
#         cursor = db.cursor()
#         cursor.execute("SELECT * FROM user_bookings WHERE user_id = ?", (session['user_id'],))
#         bookings = cursor.fetchall()
#         return render_template('user_booking_history.html', bookings=bookings)
#     return render_template('login.html', error='Unauthorized access.')
# Update the user_booking_history route
@app.route('/user_booking_history', methods=['GET'])
def user_booking_history():
    user_id = session.get('user_id')

    if user_id and session.get('user_type') == 'user':
        # Fetch user's booking history from the database
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM user_bookings WHERE user_id = ?", (user_id,))
        bookings = cursor.fetchall()
        return render_template('user_booking_history.html', bookings=bookings)

    return render_template('user_booking_history.html', error='Unauthorized access.')


# ... (Previous code)

# ... (remaining code)


# ... (previous code)

# Routes for additional HTML files


# Run the app
if __name__ == '__main__':
    create_tables()  # Initialize the database tables
    app.run(debug=True)
