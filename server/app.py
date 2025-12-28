#!/usr/bin/env python3
# server/app.py
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate # type: ignore
from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries, 200)

# CONSOLIDATED ROUTE (Handles both GET and PATCH)
@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if not bakery:
        return make_response({"error": "Bakery not found"}, 404)

    if request.method == 'GET':
        return make_response(bakery.to_dict(), 200)

    elif request.method == 'PATCH':
        for attr in request.form:
            setattr(bakery, attr, request.form.get(attr))
        db.session.commit()
        return make_response(bakery.to_dict(), 200)

@app.route('/baked_goods', methods=['POST'])
def post_baked_goods():
    new_baked_good = BakedGood(
        name=request.form.get('name'),
        price=int(request.form.get('price')),
        bakery_id=int(request.form.get('bakery_id'))
    )
    db.session.add(new_baked_good)
    db.session.commit()
    return make_response(new_baked_good.to_dict(), 201)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.filter_by(id=id).first()
    if not baked_good:
        return make_response({"error": "Baked good not found"}, 404)
    
    db.session.delete(baked_good)
    db.session.commit()
    return make_response({"message": "Baked good deleted successfully"}, 200)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    return make_response([bg.to_dict() for bg in baked_goods], 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    return make_response(most_expensive.to_dict(), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)