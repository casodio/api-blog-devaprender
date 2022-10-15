#primeira api com flask
# flask ou flaskrestfull
# no caso usaremos o flask por ser mais facil 

# from crypt import methods
import json
from flask import Flask, jsonify, request, make_response
from datab import Autor, Postagem, app, db
import jwt
from datetime import datetime, timedelta
from functools import wraps

# from symbol import decorated, decorator

def token_obrigatorio(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagen':'token nao foi incluido'}, 401)
            
        # se temos um tokem, validar acesso
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'mensagem': 'token é invalido'}, 401)
        return f(autor, *args, **kwargs)
    return decorator


@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.utcnow(
        ) + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token':token})
    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})


#rota padrao - GET - http://localhost:5000
@app.route('/')
@token_obrigatorio
def obter_postagens(autor):
    postagens = Postagem.query.all()

    list_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        list_postagens.append(postagem_atual)
    return jsonify({'postagens': list_postagens})

# Obter postagem por id - GET https://localhost:5000/postagem/1


@app.route('/postagem/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_indice(autor,id_postagem):
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    postagem_atual = {}
    try:
        postagem_atual['titulo'] = postagem.titulo
    except:
        pass
    postagem_atual['id_autor'] = postagem.id_autor

    return jsonify({'postagens': postagem_atual})

# Criar uma nova postagem - POST https://localhost:5000/postagem


@app.route('/postagem', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(
        titulo=nova_postagem['titulo'], id_autor=nova_postagem['id_autor'])

    db.session.add(postagem)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem criada com sucesso'})

# Alterar uma postagem existente - PUT https://localhost:5000/postagem/1


@app.route('/postagem/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor,id_postagem):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    try:
        postagem.titulo = postagem_alterada['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_alterada['id_autor']
    except:
        pass

    db.session.commit()
    return jsonify({'mensagem': 'Postagem alterada com sucessso'})

# Excluir uma postagem - DELETE - https://localhost:5000/postagem/1


@app.route('/postagem/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def excluir_postagem(autor,id_postagem):
    postagem_a_ser_excluida = Postagem.query.filter_by(
        id_postagem=id_postagem).first()
    if not postagem_a_ser_excluida:
        return jsonify({'mensagem': 'Não foi encontrado uma postagem com este id'})
    db.session.delete(postagem_a_ser_excluida)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem excluída com sucesso!'})

#------------------------------------------------------------------------------
# acessando a lista de autores
# http://localhost:5000/autores
@app.route('/autores')
@token_obrigatorio
def autores(autor):
    autores = Autor.query.all()
    lista_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        lista_autores.append(autor_atual)

    return jsonify({'autores': lista_autores})

# acessando um autor especifico
# http://localhost:5000/autores/0
@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def autores_id(autor,id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify(f'Autor nao encontrado!')
    else:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email

        return jsonify(f'Voce buscou pelo autor {autor_atual}')

# adicionando um novo autor
@app.route('/autores', methods=['POST'])
@token_obrigatorio
def add_autor(autor):
    new_autor = request.get_json()
    autor = Autor(
        nome=new_autor['nome'], senha=new_autor['senha'], email=new_autor['email'])

    db.session.add(autor)
    db.session.commit()

    return jsonify({'mensagem':'usuario adicionado com sucesso'})

# atualizando um autor
@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def update_autor(autor,id_autor):
    usuario_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify(f'este usuario nao foi encontrado!')
    try:
        if usuario_alterar['nome']:
            autor.nome = usuario_alterar['nome']
    except:
        pass
    try:
        if usuario_alterar['senha']:
            autor.senha = usuario_alterar['senha']
    except:
        pass
    try:
        if usuario_alterar['email']:
            autor.email = usuario_alterar['email']
    except:
        pass
        
    db.session.commit()
    return jsonify(f'usuario atualizado com sucesso')

# deletando um autor
@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def del_autor(autor,id_autor):

    autor_existe = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existe:
        return jsonify({'este autor não foi encontrado'})

    db.session.delete(autor_existe)
    db.session.commit()

    return jsonify({'menssagem': 'autor excluido com sucesso'})


#**********************************************************************************
app.run(port=5000, host='localhost', debug=True)

