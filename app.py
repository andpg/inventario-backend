from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import dotenv_values
from pymongo import MongoClient
from bson import ObjectId

# Instantiation
env = dotenv_values()
app = Flask(__name__)
mongo = MongoClient(env['MONGO_URI'])

# Settings
CORS(app)

# Database
db = mongo.inventario

# Routes: usuario sessions
@app.route('/login', methods=['POST'])
def log_in():
  usuario = db.users.find_one({
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
    return jsonify({'error': 'El usuario no existe.'})

@app.route('/register', methods=['POST'])
def register():
  usuario = db.users.find_one({'email': request.form['email']})
  if usuario:
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
  else:
    return jsonify({'error': 'El usuario ya existe.'})

# Routes: inventory articulos
@app.route('/articulos', methods=['POST'])
def create_articulo():
  id = db.articulos.insert({
    'nombre': request.form['nombre'],
    'categoría': request.form['categoría'],
    'cantidad': 0
  })
  return jsonify(str(ObjectId(id)))

@app.route('/articulos', methods=['GET'])
def get_articulos():
  return jsonify([{
    '_id': str(ObjectId(articulo['_id'])),
    'nombre': articulo['nombre'],
    'categoría': articulo['categoría'],
    'cantidad': articulo['cantidad']
  } for articulo in db.articles.find()])

@app.route('/articulos/<id>', methods=['GET'])
def get_articulo(id):
  articulo = db.articles.find_one({'_id': ObjectId(id)})
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
  return jsonify(str(ObjectId(id)))

@app.route('/articulos/<id>/sell', methods=['POST'])
def sell_articulo(id):
  db.articulos.update_one({'_id': ObjectId(id)}, {"$inc": {
    'cantidad': - request.form['cantidad']
  }})
  return jsonify(str(ObjectId(id)))

# Routes: pedidoing
@app.route('/pedidos', methods=['POST'])
def pedido_articulo():
  id = db.pedidos.insert({
    'id_articulo': ObjectId(request.form['id_articulo']),
    'proveedor': request.form['proveedor'],
    'cantidad': request.form['cantidad'],
    'fecha': request.form['fecha']
  })
  return jsonify(str(ObjectId(id)))

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
    app.run(debug=True)
