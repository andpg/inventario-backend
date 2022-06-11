from flask import Flask, jsonify, request
from flask_cors import CORS
from os import environ
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from random import randint

# Instantiation
app = Flask(__name__)
mongo = MongoClient(environ['MONGO_URI'])

# Settings
CORS(app)

# Database
db = mongo.inventario

# Routes: sesiones de usuario
@app.route('/login', methods=['POST'])
def log_in():
  usuario = db.usuarios.find_one({
    'email': request.form['email'],
    'contraseña': request.form['contraseña']
  })
  if usuario:
    return jsonify({
      '_id': str(ObjectId(usuario['_id'])),
      'nombre': usuario['nombre'],
      'email': usuario['email'],
    })
  else:
    return jsonify({'error': 'Correo o contraseña equivocados.'})

@app.route('/register', methods=['POST'])
def register():
  usuario = db.usuarios.find_one({'email': request.form['email']})
  if usuario:
    return jsonify({'error': 'Correo ya registrado.'})
  else:
    id = db.usuarios.insert({
      'nombre': request.form['nombre'],
      'email': request.form['email'],
      'contraseña': request.form['contraseña']
    })
    return jsonify({
      '_id': str(ObjectId(id)),
      'nombre': request.form['nombre'],
      'email': request.form['email'],
    })

# Routes: articulos
@app.route('/articulos', methods=['POST'])
def create_articulo():
  id = db.articulos.insert({
    'nombre': request.form['nombre'],
    'categoría': request.form['categoría'],
    'cantidad': 0
  })
  return jsonify({'_id': str(ObjectId(id))})

@app.route('/articulos', methods=['GET'])
def get_articulos():
  return jsonify([{
    '_id': str(ObjectId(articulo['_id'])),
    'nombre': articulo['nombre'],
    'categoría': articulo['categoría'],
    'cantidad': articulo['cantidad']
  } for articulo in db.articulos.find()])

@app.route('/articulos/<id>', methods=['GET'])
def get_articulo(id):
  articulo = db.articulos.find_one({'_id': ObjectId(id)})
  if articulo:
    return jsonify({
      '_id': str(ObjectId(articulo['_id'])),
      'nombre': articulo['nombre'],
      'categoría': articulo['categoría'],
      'cantidad': articulo['cantidad']
    })
  else:
    return jsonify({'error': 'El artículo no existe.'})

@app.route('/articulos/<id>', methods=['DELETE'])
def delete_articulo(id):
  db.articulos.delete_one({'_id': ObjectId(id)})
  return jsonify({'mensaje': 'El artículo fue eliminado.'})

@app.route('/articulos/<id>', methods=['POST'])
def edit_articulo(id):
  print(request.form)
  db.articulos.update_one({'_id': ObjectId(id)}, {"$set": {
    'nombre': request.form['nombre'],
    'categoría': request.form['categoría']
  }})
  return jsonify({'_id': str(ObjectId(id))})

@app.route('/articulos/<id>/vender', methods=['POST'])
def sell_articulo(id):
  articulo = db.articulos.find_one({'_id': ObjectId(id)})
  if not articulo:
    return jsonify({'error': 'El artículo no existe.'})
  elif int(request.form['cantidad']) > articulo['cantidad']:
    return jsonify({'error': 'No hay suficientes artículos de ${articulo["nombre"]}'})
  else:
    db.articulos.update_one({'_id': ObjectId(id)}, {"$inc": {
      'cantidad': - int(request.form['cantidad'])
    }})
    return jsonify({'_id': str(ObjectId(id))})

# Routes: pedidos
@app.route('/pedidos', methods=['POST'])
def pedir_articulo():
  articulo = db.articulos.find_one({'_id': ObjectId(request.form['id_articulo'])})
  if articulo:
    id = db.pedidos.insert({
      'id_articulo': ObjectId(request.form['id_articulo']),
      'proveedor': request.form['proveedor'],
      'cantidad': int(request.form['cantidad']),
      'fecha': datetime.utcnow(),
      'entrega': {
        'fecha': datetime.utcnow(),
        'cantidad': randint(articulo['cantidad'] * 0.8, articulo['cantidad'] * 1.2)
      }
    })
    db.articulos.update_one({'_id': ObjectId(id)}, {"$inc": {
      'cantidad': db.pedidos.find_one({'_id': ObjectId(id)})['entrega']['cantidad']
    }})
    return jsonify({'_id': str(ObjectId(id))})
  else:
    return jsonify({'error': 'El artículo no existe.'})

@app.route('/pedidos', methods=['GET'])
def get_pedidos():
  return jsonify([{
    '_id': str(ObjectId(pedido['_id'])),
    'id_articulo': str(ObjectId(pedido['id_articulo'])),
    'proveedor': pedido['proveedor'],
    'cantidad': pedido['cantidad'],
    'fecha': pedido['fecha'],
    'entrega': pedido['entrega']
  } for pedido in db.orders.find()])

@app.route('/pedidos/<id>', methods=['GET'])
def get_pedido(id):
  pedido = db.orders.find_one({'_id': ObjectId(id)})
  if pedido:
    return jsonify({
      '_id': str(ObjectId(pedido['_id'])),
      'id_articulo': str(ObjectId(pedido['id_articulo'])),
      'proveedor': pedido['proveedor'],
      'cantidad': pedido['cantidad'],
      'fecha': pedido['fecha'],
      'entrega': pedido['entrega']
    })
  else:
    return jsonify({'error': 'El artículo no existe.'})

@app.route('/pedidos/<id>', methods=['DELETE'])
def cancel_pedido(id):
  db.pedidos.delete_one({'_id': ObjectId(id)})
  return jsonify({'mensaje': 'El artículo fue eliminado.'})

if __name__ == "__main__":
    app.run()
