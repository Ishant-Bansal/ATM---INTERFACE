from flask import Flask, render_template, request, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Session ke liye secret key

class ATM:
    def __init__(self, balance=50000, pin="9680"):
        self.balance = balance
        self.pin = pin
        self.max_attempts = 3

    def check_pin(self, entered_pin):
        return entered_pin == self.pin

    def check_balance(self):
        return self.balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True, f"₹{amount} deposited successfully!"
        return False, "Invalid deposit amount"

    def withdraw(self, amount):
        if amount > 0 and amount <= self.balance:
            self.balance -= amount
            return True, f"₹{amount} withdrawn successfully!"
        return False, "Insufficient balance or invalid amount"

# ATM instance
atm = ATM()

@app.route('/')
def home():
    session.clear()  # Clear previous session
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    entered_pin = request.form['pin']
    
    if 'attempts' not in session:
        session['attempts'] = 0
    
    session['attempts'] += 1
    
    if atm.check_pin(entered_pin):
        session['authenticated'] = True
        session['attempts'] = 0  # Reset attempts
        return redirect(url_for('dashboard'))
    else:
        remaining_attempts = atm.max_attempts - session['attempts']
        if remaining_attempts <= 0:
            return render_template('index.html', 
                                 error="Too many incorrect attempts. Please refresh to try again.",
                                 block=True)
        return render_template('index.html', 
                             error=f"Incorrect PIN. {remaining_attempts} attempts left.")

@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('home'))
    
    balance = atm.check_balance()
    message = session.pop('message', None)
    return render_template('index.html', authenticated=True, balance=balance, message=message)

@app.route('/check_balance')
def check_balance():
    if not session.get('authenticated'):
        return redirect(url_for('home'))
    
    balance = atm.check_balance()
    session['message'] = f"Your current balance is ₹{balance}"
    return redirect(url_for('dashboard'))

@app.route('/deposit', methods=['POST'])
def deposit():
    if not session.get('authenticated'):
        return redirect(url_for('home'))
    
    try:
        amount = float(request.form['amount'])
        success, message = atm.deposit(amount)
        session['message'] = message
    except ValueError:
        session['message'] = "Please enter a valid amount"
    
    return redirect(url_for('dashboard'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if not session.get('authenticated'):
        return redirect(url_for('home'))
    
    try:
        amount = float(request.form['amount'])
        success, message = atm.withdraw(amount)
        session['message'] = message
    except ValueError:
        session['message'] = "Please enter a valid amount"
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
