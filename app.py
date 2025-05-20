from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_super_segura'
USER_DB = 'postgres'
PASS_DB = 'admin'
URL_DB = 'localhost'
NAME_DB = 'Flask'
FULL_URL_DB = f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'
app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modelo de Datos: Libro
class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Libro {self.titulo}>'

# Formulario para gestionar libros
class LibroForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    autor = StringField('Autor', validators=[DataRequired()])
    categoria = StringField('Categoría', validators=[DataRequired()])
    enviar = SubmitField('Guardar')

# Ruta de inicio: Listar libros
@app.route('/')
def inicio():
    libros = Libro.query.all()
    total_libros = Libro.query.count()
    return render_template('index.html', libros=libros, total_libros=total_libros)

# Ruta para agregar un libro
@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    libro = Libro()
    libro_form = LibroForm(obj=libro)
    if request.method == 'POST' and libro_form.validate_on_submit():
        libro_form.populate_obj(libro)
        db.session.add(libro)
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template('agregar.html', forma=libro_form)

# Ruta para editar un libro
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    libro = Libro.query.get_or_404(id)
    libro_form = LibroForm(obj=libro)
    if request.method == 'POST' and libro_form.validate_on_submit():
        libro_form.populate_obj(libro)
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template('editar.html', forma=libro_form)

# Ruta para eliminar un libro
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    libro = Libro.query.get_or_404(id)
    db.session.delete(libro)
    db.session.commit()
    return redirect(url_for('inicio'))

# Manejo de errores
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("error404.html", mensajeerror=error), 404

if __name__ == '__main__':
    app.run(debug=True)
