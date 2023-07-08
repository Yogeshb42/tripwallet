from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trip_wallet.db'
db = SQLAlchemy(app)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    amount = db.Column(db.Float)
    calculation = db.Column(db.Float, default=0)

    def __init__(self, name, amount):
        self.name = name
        self.amount = amount


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        calculation = amount - get_mean_amount()

        entry = Entry(name=name, amount=amount)
        db.session.add(entry)
        db.session.commit()

        update_calculation()
    table_data = Entry.query.order_by(Entry.id).all()

    for index, entry in enumerate(table_data, start=1):
        entry.no = index

    db.session.commit()

    return render_template('index.html', table_data=table_data)
    


@app.route('/update', methods=['POST'])
def update_entry():
    entry_id = int(request.form['id'])
    new_amount = float(request.form['newAmount'])

    entry = Entry.query.get(entry_id)
    if entry:
        entry.amount = new_amount
        db.session.commit()

    update_calculation()
    return jsonify({'message': 'Entry updated successfully'})


@app.route('/delete', methods=['POST'])
def delete_entry():
    entry_id = int(request.form['id'])
    entry = Entry.query.get(entry_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()

    update_calculation()
    return jsonify({'message': 'Entry deleted successfully'})

def get_mean_amount():
    entries = Entry.query.all()
    if entries:
        total_amount = sum(entry.amount for entry in entries)
        mean_amount = total_amount / len(entries)
        return mean_amount
    return 0


def update_calculation():
    mean_amount = get_mean_amount()
    entries = Entry.query.all()
    for entry in entries:
        entry.calculation = entry.amount - mean_amount
    db.session.commit()

