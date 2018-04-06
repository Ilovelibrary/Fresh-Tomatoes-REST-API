#!/usr/bin/python
from flask import Flask, jsonify, request, make_response
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from bson import json_util

from functools import wraps

client = MongoClient('localhost', 27017)
db = client.movie


def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']

		if not token:
			return jsonify({'message' : 'Token is missing!'}), 401

		try: 
			data = jwt.decode(token, app.secret_key)
			current_user = db.users.find_one({'username': data['username']})
		except:
			return jsonify({'message' : 'Token is invalid!'}), 401

		return f(current_user, *args, **kwargs)

	return decorated

# Build the server and set the routes
app = Flask(__name__)

@app.route('/users')
def users():
	cursor = db.users.find({})
	users = []
	for user in cursor:
		users.append(user)
	return json.dumps(users, default=json_util.default)


@app.route('/users/login', methods=['POST'])
def login():
	data = request.data
	data = json.loads(data)

	if not data or not data['username'] or not data['password']:
		return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

	user = db.users.find_one({'username': data['username']})

	if not user:
		return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

	if check_password_hash(user['password'], data['password']):
		token = jwt.encode({'username' : user['username'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.secret_key)
		return jsonify({'token' : token.decode('UTF-8')})

	return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})


@app.route('/users/signup', methods=['POST'])
def signup():
	data = request.get_json()
	print data
	if not data['username'] or not data['password']:
		return 'Please fill in both username and password'
	
	hashed_password = generate_password_hash(data['password'], method='sha256')

	new_user = {'username': data['username'], 'password': hashed_password, 'admin': False}
	if 'admin' in data:
		new_user['admin'] = data['admin']
	db.users.insert_one(new_user)
	
	return jsonify({'message' : 'New user created!'})

@app.route('/movies')
def movies():
	cursor = db.movies.find({})
	movies = []
	for movie in cursor:
		movies.append(movie)
	return json.dumps(movies, default=json_util.default)

# post one movie only by admin
@app.route('/movies', methods=['POST'])
@token_required
def post_movie(current_user):
	data = request.data
	data = json.loads(data)
	if current_user['admin']==True:
		new_movie = {}
		new_movie['title'] = data['title']
		new_movie['year'] = data['year']
		new_movie['description'] = data['description']
		new_movie['poster_url'] = data['poster_url']
		new_movie['comments'] = []
		db.movies.insert_one(new_movie)
		return json.dumps(new_movie, default=json_util.default)
	else:
		return 'You are not authorized to operate it.'

@app.route('/movies', methods=['DELETE'])
@token_required
def delete_movies(current_user):
	data = request.data
	if current_user['admin']==True:
		db.movies.delete_many({})
		db.comments.delete_many({})
		return 'All movies are deleted'
	else:
		return 'You are not authorized to operate it.'

@app.route('/movies/<movie_id>')
def movie(movie_id):
	movie = db.movies.find_one({"_id": ObjectId(movie_id)})
	return json.dumps(movie, default=json_util.default)

@app.route('/movies/<movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
	selected_movie = db.movies.find_one({"_id": ObjectId(movie_id)})
	for cid in selected_movie['comments']:
		db.comments.delete_one({"_id": cid})
	db.movies.delete_one({"_id": ObjectId(movie_id)})
	return json.dumps(selected_movie, default=json_util.default)

@app.route('/movies/<movie_id>/comments')
def comments(movie_id):
	selected_movie = db.movies.find_one({"_id": ObjectId(movie_id)})
	comments = []
	for cid in selected_movie['comments']:
		comments.append(db.comments.find_one({"_id": cid}))
	print comments
	return json.dumps(comments, default=json_util.default)

@app.route('/movies/<movie_id>/comments', methods=['POST'])
@token_required
def post_comments(current_user, movie_id):
	selected_movie = db.movies.find_one({"_id": ObjectId(movie_id)})
	data = json.loads(request.data)
	if not data['comment'] or not data['rating']:
		return 'Comment or rating is needed'
	new_comment = {'comment': data['comment'], 'author':current_user["_id"], 'rating': data['rating']}
	print new_comment
	new_comment_id = db.comments.insert(new_comment)
	db.comments.save(new_comment)
	print new_comment_id
	selected_movie['comments'].append(new_comment_id)
	db.movies.save(selected_movie)
	return json.dumps('Comment Submitted Successfully', default=json_util.default)

@app.route('/movies/<movie_id>/comments', methods=['DELETE'])
@token_required
def delete_comments(current_user, movie_id):
	selected_movie = db.movies.find_one({"_id": ObjectId(movie_id)})
	for cid in selected_movie['comments']:
		db.comments.delete_one({"_id": cid})
	selected_movie['comments'] = []
	db.movies.save(selected_movie)
	return json.dumps('All Comments for this movie deleted', default=json_util.default)

@app.route('/movies/<movie_id>/comments/<comment_id>')
def comment(movie_id, comment_id):
	selected_comment = db.comments.find_one({"_id": ObjectId(comment_id)})
	return json.dumps(selected_comment, default=json_util.default)

@app.route('/movies/<movie_id>/comments/<comment_id>', methods=['DELETE'])
@token_required
def delete_comment(current_user, movie_id, comment_id):
	selected_movie = db.movies.find_one({"_id": ObjectId(movie_id)})
	for i in xrange(len(selected_movie['comments'])):
		if selected_movie['comments'][i]==ObjectId(comment_id):
			index = i
			break
	selected_comment = db.comments.find_one({"_id": ObjectId(comment_id)})
	if selected_comment['author']==current_user["_id"]:
		db.comments.delete_one({"_id": ObjectId(comment_id)})
		selected_movie['comments'].pop(index)
		db.movies.save(selected_movie)
		return 'Comment Deleted'
	return 'You are not authorized to operate it'

if __name__ == '__main__':
	app.secret_key = 'super-secret-key'
	app.debug = True
	app.run(host='0.0.0.0', port=8000)

