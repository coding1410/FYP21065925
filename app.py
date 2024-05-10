from datetime import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from config import db, init_app
from models import Owner, Pet, UserCredentials
import schedule # type: ignore
import time

app = Flask(__name__)
init_app(app)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('homelogout'))  # Redirect to the custom logged-in homepage
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = UserCredentials.query.filter_by(username=username).first()
        if user and user.password == password:  # You should hash and verify the password
            session['username'] = username
            return redirect(url_for('homelogout'))  # Redirect to the custom logged-in homepage
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/homelogout')
def homelogout():
    if 'username' in session:
        return render_template('homelogout.html', username=session['username'])  # This is your logged-in homepage
    return redirect(url_for('login'))  # Redirect to login if not logged in

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')  # Always show login/signup options here

@app.route('/logout')
def logout():
    session.clear()  # This clears all data from the session
    return redirect(url_for('homepage'))  # Redirect to the general homepage with login/signup options

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Collecting form data
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        address = request.form['address']
        pet_name = request.form['pet_name']
        breed = request.form['breed']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        primary_vet = request.form['primary_vet']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        # Creating new records
        owner = Owner(full_name=full_name, phone_number=phone_number, email=email, address=address)
        pet = Pet(name=pet_name, breed=breed, dob=dob, primary_vet=primary_vet, owner=owner)
        user_credentials = UserCredentials(username=username, password=password, owner=owner)

        db.session.add_all([owner, pet, user_credentials])
        db.session.commit()
        flash('Account created successfully, please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/send-password-reset', methods=['POST'])
def send_password_reset():
    email = request.form['email']
    # Logic to verify email and send reset instructions
    # For example, check if the email is registered, generate a secure token, send email with reset link
    return "Reset password link has been sent if the email is registered."

@app.route('/records')
def records():
    # Assuming you retrieve the pet object from your database
    pet = Pet.query.first()  # Just an example, adjust according to your actual data retrieval logic
    current_year = datetime.now().year  # Get the current year
    if pet:
        return render_template('records.html', pet=pet, current_year=current_year)
    else:
        # Handle the case where no pet is found or you want to display a default message
        return render_template('records.html', pet=None)

@app.route('/consultation')
def consultation():
    current_date = datetime.now().strftime("%Y-%m-%d")  # Get current date in the format YYYY-MM-DD
    return render_template('consultation.html', current_date=current_date)

@app.route('/submit_consultation', methods=['POST'])
def submit_consultation():
    date = request.form['appointment_date']
    time = request.form['time']
    reason = request.form['reason']
    message = request.form['message']
    # Here, you can add database logic to store or process the consultation data
    flash('Consultation scheduled successfully.', 'success')
    return redirect(url_for('consultation'))

def get_current_date():
    return datetime.now().strftime('%Y-%m-%d')

@app.route('/nutrition')
def nutrition():
    return render_template('nutrition.html')  # or any other appropriate handling

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_credentials.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

@app.route('/shop')
def shop():
    products = Product.query.all()
    return render_template('shop.html', products=products)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        flash('You need to login to add items to the cart', 'error')
        return redirect(url_for('login'))
    
    product_id = request.form['product_id']
    existing_cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    
    if existing_cart_item:
        existing_cart_item.quantity += 1
    else:
        new_cart_item = Cart(user_id=session['user_id'], product_id=product_id)
        db.session.add(new_cart_item)
    
    db.session.commit()
    flash('Product added to cart successfully', 'success')
    return redirect(url_for('shop'))

@app.route('/view_cart')
def view_cart():
    if 'user_id' not in session:
        flash('You need to login to view your cart', 'error')
        return redirect(url_for('login'))
    
    cart_items = Cart.query.filter_by(user_id=session['user_id']).join(Product, Cart.product_id == Product.id).add_columns(
        Product.name, Product.price, Product.image, Cart.quantity).all()
    
    total_price = sum([item.quantity * item.price for item in cart_items])
    return render_template('cart.html', cart_items=cart_items, total=total_price)

@app.route('/update_cart/<int:cart_id>', methods=['POST'])
def update_cart(cart_id):
    new_quantity = request.json['quantity']
    cart_item = Cart.query.get(cart_id)
    if cart_item:
        cart_item.quantity = int(new_quantity)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    cart_item = Cart.query.get(cart_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

def init_db():
    db.drop_all()
    db.create_all()

    products = [
        Product(name='Colorful Dog Collar', price=15.99, image='static/images/dog_collar.jpg', category='Accessories'),
        Product(name='Plush Dog Toy', price=9.99, image='static/images/dog_toy.jpg', category='Toys'),
        Product(name='Premium Dog Food', price=22.50, image='static/images/dog_food.jpg', category='Food'),
        Product(name='Dog Shampoo', price=8.45, image='static/images/dog_shampoo.jpg', category='Grooming')
    ]

    db.session.bulk_save_objects(products)
    db.session.commit()

@app.route('/getstarted')
def getstarted():
    return render_template('getstarted.html')  # Assuming you have a getstarted.html template

@app.route('/learnmore')
def learnmore():
    return render_template('learnmore.html')


# Store reminders in a dictionary for simplicity
reminders = {}

# Function to send reminder notifications (replace this with your actual notification mechanism)
def send_notification(reminder_id, reminder_type, reminder_notes):
    print(f"Reminder: {reminder_type} - {reminder_notes}")

# Route to render the HTML page with the reminder form
@app.route('/set-reminder', methods=['GET'])
def set_reminder():
    return render_template('reminder.html')

# Route to handle the reminder form submission
@app.route('/set-reminder', methods=['POST'])
def handle_reminder():
    reminder_type = request.form['reminder-type']
    reminder_date_time = request.form['reminder-date-time']
    reminder_notes = request.form['reminder-notes']
    
    # Store reminder data
    reminder_id = len(reminders) + 1
    reminders[reminder_id] = {
        'type': reminder_type,
        'date_time': reminder_date_time,
        'notes': reminder_notes
    }
    
    # Schedule the reminder
    schedule_reminder(reminder_id, reminder_date_time, reminder_type, reminder_notes)
    
    return "Reminder set successfully!"

# Function to schedule the reminder
def schedule_reminder(reminder_id, reminder_date_time, reminder_type, reminder_notes):
    def job():
        send_notification(reminder_id, reminder_type, reminder_notes)
    
    # Parse the reminder date and time
    reminder_time = time.strptime(reminder_date_time, "%Y-%m-%dT%H:%M")
    
    # Schedule the reminder using schedule library
    schedule.every().day.at(time.strftime("%H:%M", reminder_time)).do(job)

# Function to run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    # Start the scheduler in a separate thread
    import threading
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

    # Create database tables
    with app.app_context():
        db.create_all()

    # Run the Flask app
    app.run(debug=True)
    app.run(host='0.0.0.0', port=8000)
