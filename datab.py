from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#criando a API flask
app = Flask(__name__)

#criando a instancia SQLAlchemy
app.config['SECRET_KEY'] = 'M@rc10'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
db:SQLAlchemy

#definindo a estrutura da tabela postagens
# id_postagem, titulo, autor
class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))


#definindo a estrutura da tabela autor
# id_autor, nome, email, senha, admin, postagens
class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem')


def inicializar_db():
# executando o comando para criar o banco de dados
    db.drop_all()
    db.create_all()

    # criando usuarios e administradores
    autor = Autor(nome='marcio', email='marcio@email.com',senha='123456',admin=True)
    db.session.add(autor)
    db.session.commit()

if __name__== '__main__':
    inicializar_db()