#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, UserSchema

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class Signup(Resource):

    def post(self):
        data = request.get_json(silent=True)
        if (
            not isinstance(data, dict)
            or not data.get('username')
            or not data.get('password')
        ):
            return {'message': 'Username and password are required'}, 400

        user = User(username=data['username'])
        user.password_hash = data['password']
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        return UserSchema().dump(user), 201

class CheckSession(Resource):

    def get(self):
        user_id = session.get('user_id')
        user = db.session.get(User, user_id) if user_id is not None else None
        if user is None:
            return '', 204

        return UserSchema().dump(user), 200

class Login(Resource):

    def post(self):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {}, 401

        user = User.query.filter_by(username=data.get('username')).first()
        if user is None or not user.authenticate(data.get('password', '')):
            return {}, 401

        session['user_id'] = user.id
        return UserSchema().dump(user), 200

class Logout(Resource):

    def delete(self):
        session.pop('user_id', None)
        return '', 204

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(ClearSession, '/clear', endpoint='clear')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
