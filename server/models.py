from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship('HeroPower', back_populates='hero')

    # add serialization rules
    serialize_rules = ('-hero_powers',)

    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship('HeroPower', back_populates='power')

    # add serialization rules
    serialize_rules = ('-hero_powers',)

    # add validation
    @validates('description')
    def validates_description(self, key, description):
        if not description:
            raise ValueError("Description input required.")
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters long.")


    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # add relationships
    hero_id = db.Column(db.Integer, ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, ForeignKey('powers.id'), nullable=False)
    hero = relationship('Hero', back_populates='hero_powers')
    power = relationship('Power', back_populates='hero_powers')

    # add serialization rules
    serialize_rules = ('-hero', '-power',)

    # add validation
    @validates('strenght')
    def validates_strenght(self, key, strenght):
        strenghts_arr = ['Strong', 'Weak', 'Average']
        if strenght not in strenghts_arr:
            raise ValueError("Strenght must be one of the following: 'Strong', 'Weak', 'Average'.")
        return strenght

    def __repr__(self):
        return f'<HeroPower {self.id}>'
