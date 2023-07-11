from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trip_wallet.db'
db = SQLAlchemy(app)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    amount = db.Column(db.Float)
    settlement = db.Column(db.String(255))
    calculation = db.Column(db.Float, default=0)

    def __init__(self, name, amount):
        self.name = name
        self.amount = amount
        self.settlement = ""


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])

        entry = Entry(name=name, amount=amount)
        db.session.add(entry)
        db.session.commit()

        table_data = Entry.query.order_by(Entry.id).all()
        update_settlement(table_data)  # Call update_settlement() with all entries

        db.session.commit()

    elif request.method == 'GET':
        table_data = Entry.query.order_by(Entry.id).all()

    for index, entry in enumerate(table_data, start=1):
        entry.no = index

    return render_template('index.html', table_data=table_data)


@app.route('/update', methods=['POST'])
def update_entry():
    entry_id = int(request.form['id'])
    new_amount = float(request.form['newAmount'])

    entry = Entry.query.get(entry_id)
    if entry:
        entry.amount = new_amount
        db.session.commit()

        table_data = Entry.query.order_by(Entry.id).all()
        update_settlement(table_data)  # Call update_settlement() with all entries

        db.session.commit()

    return jsonify({'message': 'Entry updated successfully'})


def update_settlement(entries):
    total_entries = len(entries)
    total_amount = sum(entry.amount for entry in entries)
    mean_amount = total_amount / total_entries

    for entry in entries:
        diff = mean_amount - entry.amount
        entry.calculation = diff

        if diff > 0:
            entry.settlement = f"Pay {diff:.2f} to others"
        elif diff < 0:
            entry.settlement = f"Receive {-diff:.2f} from others"
        else:
            entry.settlement = ""


@app.route('/delete', methods=['POST'])
def delete_entry():
    entry_id = int(request.form['id'])
    entry = Entry.query.get(entry_id)
    if entry:
        db.session.delete(entry)
        db.session.commit()

        table_data = Entry.query.order_by(Entry.id).all()
        update_settlement(table_data)  # Call update_settlement() with all entries

        db.session.commit()

    return jsonify({'message': 'Entry deleted successfully'})
