from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return self.title


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.username


@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']

        item = Item(title=title, price=price)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return 'Error'
    else:
        return render_template('create.html')


@app.route('/delete_item/<int:id>', methods=['POST'])
def delete_item(id):
    item = Item.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit_item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    item = Item.query.get(id)
    if request.method == 'POST':
        item.title = request.form['title']
        item.price = request.form['price']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_item.html', item=item)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')


        new_user = User(username=username, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return 'Error during registration'

    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/reports')
def reports():
    # Товари з ціною більше 30
    items_over_30 = Item.query.filter(Item.price > 30).all()

    # Топ-5 найдорожчих товарів
    top_expensive = Item.query.order_by(Item.price.desc()).limit(5).all()

    # Загальна кількість товарів
    total_items = db.session.query(db.func.count(Item.id)).scalar()

    # Юзери з буквою 't' у username
    users_with_t = User.query.filter(User.username.ilike('%t%')).all()

    # Товари з цифрою '6' у прайсі
    items_with_6_in_price = Item.query.filter(Item.price.like('%6%')).all()

    return render_template(
        'reports.html',
        items_over_30=items_over_30,
        top_expensive=top_expensive,
        total_items=total_items,
        users_with_t=users_with_t,
        items_with_6_in_price=items_with_6_in_price
    )


if __name__ == '__main__':
    app.run(debug=True)