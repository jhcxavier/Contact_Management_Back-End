"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, Contact
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/contact', methods=['POST', 'GET'])
def get_contact():

#Create a contact and retrieve all contacts!!

    if request.method == 'POST':
        body = request.get_json()

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if "name" not in body:
            raise APIException('You need to specify the name', status_code=400)
        if 'phone' not in body:
            raise APIException('You need to specify the phone', status_code=400)
        if 'email' not in body:
            raise APIException('You need to specify the email', status_code=400)
        if 'address' not in body:
            body['address'] = None

        contact1 = Contact(name=body['name'], phone = body['phone'], email = body['email'], address = body['address'])
        db.session.add(contact1)
        db.session.commit()

        return "ok", 200
    
    # GET request
    if request.method == 'GET':
        all_contact = Contact.query.all()
        all_contact = list(map(lambda x: x.serialize(), all_contact))
        return jsonify(all_contact), 200

    return "Invalid Method", 404

@app.route('/contact/<int:contact_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_contact(contact_id):
    """
    Single contact
    """

    # PUT request
    if request.method == 'PUT':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)

        contact1 = Contact.query.get(contact_id)
        if contact1 is None:
            raise APIException('User not found', status_code=404)

        if "name" in body:
            contact1.name = body["name"]
        if "phone" in body:
            contact1.phone = body["phone"]
        if "email" in body:
            contact1.email = body["email"]
        if "address" in body:
            contact1.address = body["address"]
        db.session.commit()

        return jsonify(contact1.serialize()), 200

    # GET request
    if request.method == 'GET':
        contact1 = Contact.query.get(contact_id)
        if contact1 is None:
            raise APIException('User not found', status_code=404)
        return jsonify(contact1.serialize()), 200

    # DELETE request
    if request.method == 'DELETE':
        contact1 = Contact.query.get(contact_id)
        if contact1 is None:
            raise APIException('User not found', status_code=404)
        db.session.delete(contact1)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
