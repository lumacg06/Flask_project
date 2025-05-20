from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
import os
from werkzeug.utils import secure_filename
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
    precio = db.Column(db.String(20), nullable=False, server_default='0')
    portada = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Libro {self.titulo}>'

# Formulario para gestionar libros
class LibroForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    autor = StringField('Autor', validators=[DataRequired()])
    categoria = StringField('Categoría', validators=[DataRequired()])
    precio = StringField('Precio', validators=[DataRequired()])
    portada = FileField('Portada', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Solo imágenes')])
    enviar = SubmitField('Agregar')

# Ruta de inicio: Listar libros
@app.route('/')
def inicio():
    libros = Libro.query.all()
    total_libros = Libro.query.count()
    return render_template('index.html', libros=libros, total_libros=total_libros)

# Ruta para agregar un libro
@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    form = LibroForm()
    if form.validate_on_submit():
        filename = None
        if form.portada.data:
            filename = secure_filename(form.portada.data.filename)
            ruta = os.path.join('static/portadas', filename)
            form.portada.data.save(ruta)
        libro = Libro(
            titulo=form.titulo.data,
            autor=form.autor.data,
            categoria=form.categoria.data,
            precio=form.precio.data,
            portada=filename
        )
        db.session.add(libro)
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template('agregar.html', forma=form)

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

# Ruta para el catálogo de libros
@app.route('/catalogo')
def catalogo():
    libros = Libro.query.all()
    return render_template('catalogo.html', libros=libros)

# Manejo de errores
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("error404.html", mensajeerror=error), 404

if __name__ == '__main__':
    app.run(debug=True)
