#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# GET /heroes
class Heroes(Resource):
    def get(self):
        heroes_dict_list = [hero.to_dict() for hero in Hero.query.all()]
        return make_response(heroes_dict_list, 200)

api.add_resource(Heroes, '/heroes')

# GET /heroes/:id
class HeroById(Resource):
    def get(self, id):
        hero = Hero.query.filter_by(id = id).first()
        if hero:
            serialized_hero = hero.to_dict(only=('id', 'name', 'super_name', 'hero_powers'))
            return make_response(serialized_hero, 200)
        else:
            response_dict = {
                "error": "Hero not found"
            }
            return make_response(response_dict, 404)

api.add_resource(HeroById, '/heroes/<int:id>')


# GET /powers
class Powers(Resource):
    def get(self):
        return make_response([power.to_dict() for power in Power.query.all()], 200)

api.add_resource(Powers, '/powers')


# GET /powers/:id
class PowersById(Resource):
    def get(self,id):
        powers = Power.query.filter_by(id = id).first()
        if powers:
            return make_response(powers.to_dict(), 200)
        else:
            response_dict= {
                "error": "Power not found"
            }
            return make_response(response_dict, 404)

api.add_resource(PowersById, '/powers/<int:id>')


# PATCH /powers/:id
class UpdatePower(Resource):
    def patch(self, id):
        power = Power.query.filter_by(id = id).first()
        if not power:
            return make_response({"error": "Power not found"}, 404)

        data = request.get_json()
        if 'description' in data:
            description = data['description']
            if not isinstance(description, str) or len(description) < 20:
                return make_response({"errors": ["validation errors"]}, 400)

        for attr in data:
            setattr(power, attr, data[attr])
        db.session.add(power)
        db.session.commit()

        response_data = {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
        return make_response(response_data, 200)

api.add_resource(UpdatePower, '/powers/<int:id>')


class CreateHeroPower(Resource):
    def post(self):
        data = request.json

        # Extract data from the request
        strength = data.get('strength')
        power_id = data.get('power_id')
        hero_id = data.get('hero_id')
        
        if strength not in ['Strong', 'Weak', 'Average']:
            return make_response({"error": "Invalid strength value"}, 400)

        hero = Hero.query.filter_by(id=hero_id).first()
        power = Power.query.filter_by(id=power_id).first()

        if not hero or not power:
            return make_response({"error": "Hero or Power not found"}, 404)

        hero_power = HeroPower(
            strength=strength,
            power_id=power_id,
            hero_id=hero_id
        )

        db.session.add(hero_power)
        db.session.commit()

        return make_response(hero_power.to_dict(), 201)

api.add_resource(CreateHeroPower, '/hero_powers')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
