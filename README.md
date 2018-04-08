Introduction
This is a REST API server for the fresh-tomatoes website. 

API Guide

Users
	GET: http://localhost:5000/users
	Get all users' information
	
	POST: http://localhost:5000/users/signup
	Create a new user
		Body Prarms:
			username: string
			password: string
			admin(optional): boolean

Authentication
	POST: http://localhost:5000/users/login
	Authenticate user
		Body Prarms:
			username: string
			password: string

Movies:
	GET: http://localhost:5000/movies
	Get All movies' information
	
	POST: http://localhost:5000/movies
	Create a new movie for admin users
		Header:
			x-access-token: token
		Body Prarms:
			title: string
			featured: boolean
			year: string
			urlPoster: string
			IMDbrating: string
			description: string
		
	DELETE: http://localhost:5000/movies
	Remove all movies
		Header:
			x-access-token: token
	
	GET: http://localhost:5000/movies/<movie_id>
	Get a movie with its movie_id
		Path Params:
			movie_id: string
	
	DELETE: http://localhost:5000/movies/<movie_id>
	Delete a movie with its movie_id
		Header:
			x-access-token: token
		Path Params:
			movie_id: string

Comments:
	GET: http://localhost:5000/movies/<movie_id>/comments
	Get comments of a movie
		Path Params:
	
	POST: http://localhost:5000/movies/<movie_id>/comments
	Create a new comment on a movie
		Header:
			x-access-token: token
		Path Params:
			movie_id: string
		Body Prarms:
			rating: integer
			comment: string
	
	DELETE: http://localhost:5000/movies/<movie_id>/comments
	Delete all comments of a movie
		Header:
			x-access-token: token
		Path Params:
			movie_id: string
	
	GET: http://localhost:5000/movies/<movie_id>/comments/<comment_id>
	Get a comments with its comment_id
		Path Params:
			movie_id: string
			comment_id: string
	
	DELETE: http://localhost:5000/movies/<movie_id>/comments/<comment_id>
	Delete a comment with its comment_id
		Header:
			x-access-token: token
		Path Params:
			movie_id: string
			comment_id: string
	