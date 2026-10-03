from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-cocoffe-2026'

# CONFIGURACIÓN DE MYSQL (XAMPP por defecto usa usuario 'root' sin contraseña)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/cocoffe_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# MODELOS DE BASE DE DATOS
class User(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    presentacion = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class Client(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cedula_ruc = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# RUTAS Y CONTROLADORES
@app.route('/')
@login_required
def index():
    productos = Product.query.all()
    return render_template('dashboard.html', productos=productos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('¡Bienvenido al sistema, acceso concedido con éxito!', 'success')
            return redirect(url_for('index'))
        flash('Usuario o contraseña incorrectos. Verifique sus datos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

@app.route('/productos/nuevo', methods=['POST'])
@login_required
def nuevo_producto():
    try:
        nombre = request.form.get('nombre')
        presentacion = request.form.get('presentacion')
        precio = float(request.form.get('precio'))
        stock = int(request.form.get('stock'))
        
        nuevo = Product(nombre=nombre, presentacion=presentacion, precio=precio, stock=stock)
        db.session.add(nuevo)
        db.session.commit()
        flash('¡Producto de café registrado con éxito en el inventario!', 'success')
    except Exception as e:
        flash(f'Error al registrar el producto: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/clientes', methods=['GET', 'POST'])
@login_required
def clientes():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            cedula = request.form.get('cedula')
            telefono = request.form.get('telefono')
            cliente = Client(nombre=nombre, cedula_ruc=cedula, telefono=telefono)
            db.session.add(cliente)
            db.session.commit()
            flash('¡Cliente registrado correctamente!', 'success')
        except Exception as e:
            flash('Error: La cédula o RUC ya se encuentra registrada.', 'danger')
        return redirect(url_for('clientes'))
    
    todos_clientes = Client.query.all()
    return render_template('clientes.html', clientes=todos_clientes)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Crear usuario administrador por defecto si no existe
        if not User.query.filter_by(username='admin').first():
            hashed_pw = generate_password_hash('admin123')
            admin = User(username='admin', password=hashed_pw)
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)