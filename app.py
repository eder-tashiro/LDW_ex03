from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_marshmallow import Marshmallow
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Habilita CORS para toda a aplicação
api = Api(app)
ma = Marshmallow(app)

mongo_uri = os.getenv('MONGO_URI')

# Conexão com o MongoDB
client = MongoClient(mongo_uri)
db = client.library_db
books_collection = db.books

# Schema do Livro
class BookSchema(ma.Schema):
    class Meta:
        fields = ('_id', 'title', 'genre', 'year', 'authors')

book_schema = BookSchema()
books_schema = BookSchema(many=True)

# Recursos da API
class BookListResource(Resource):
    def get(self):
        books = list(books_collection.find())
        for book in books:
            book['_id'] = str(book['_id'])
        return books_schema.dump(books)

    def post(self):
        new_book = request.json
        inserted_id = books_collection.insert_one(new_book).inserted_id
        book = books_collection.find_one({"_id": inserted_id})
        book['_id'] = str(book['_id'])
        return book_schema.dump(book), 201

class BookResource(Resource):
    def get(self, book_id):
        book = books_collection.find_one({"_id": ObjectId(book_id)})
        if book:
            book['_id'] = str(book['_id'])
            return book_schema.dump(book)
        return {"message": "Livro não encontrado"}, 404

    def put(self, book_id):
        updated_data = request.json
        books_collection.update_one({"_id": ObjectId(book_id)}, {"$set": updated_data})
        updated_book = books_collection.find_one({"_id": ObjectId(book_id)})
        updated_book['_id'] = str(updated_book['_id'])
        return book_schema.dump(updated_book), 200

    def delete(self, book_id):
        result = books_collection.delete_one({"_id": ObjectId(book_id)})
        if result.deleted_count:
            return {"message": "Livro apagado com sucesso"}, 200
        return {"message": "Livro não encontrado"}, 404

# Rotas da API
api.add_resource(BookListResource, '/books')
api.add_resource(BookResource, '/books/<string:book_id>')

if __name__ == '__main__':
    app.run(debug=True)
