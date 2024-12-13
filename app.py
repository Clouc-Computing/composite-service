from flask import Flask, request, jsonify
import httpx
from dotenv import load_dotenv
import requests
import os
import asyncio
from functools import wraps
from threading import Thread
from time import time
from flask_cors import CORS
load_dotenv(dotenv_path=".env")

app = Flask(__name__)

user_service_url = os.getenv("USER_SERVICE_URL")
print("User service: ", user_service_url)
item_service_url = os.getenv("ITEM_SERVICE_URL")
CORS(app, resources={r"/*": {"origins": "http://3.147.35.222:4200"}})

# Middleware for logging
def log_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time()
        print(f"Before {request.method} request to {request.path}")
        response = f(*args, **kwargs)
        print(f"After {request.method} request to {request.path}, took {time() - start_time}s")
        return response
    return decorated_function


@app.route('/api/mainResource', methods=['GET', 'POST'])
@log_middleware
def main_resource():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        username_filter = request.args.get('username')

        user_response = requests.get(f"{user_service_url}/users", params={'page': page, 'per_page': per_page, 'username': username_filter})
        item_response = requests.get(f"{item_service_url}/items", params={'page': page, 'per_page': per_page})
        
        return jsonify({
            'users': user_response.json(),
            'items': item_response.json()
        })

    elif request.method == 'POST':
        data = request.json
        user_response = requests.post(f"{user_service_url}/users", json=data)
        return jsonify(user_response.json()), user_response.status_code


@app.route('/api/mainResource/<int:resource_id>', methods=['GET', 'PUT'])
@log_middleware
def main_resource_id(resource_id):
    if request.method == 'GET':
        user_response = requests.get(f"{user_service_url}/users/{resource_id}")
        item_response = requests.get(f"{item_service_url}/items/{resource_id}")

        return jsonify({
            'user': user_response.json() if user_response.status_code == 200 else None,
            'item': item_response.json() if item_response.status_code == 200 else None
        })

    elif request.method == 'PUT':
        data = request.json
        thread = Thread(target=async_update_user, args=(resource_id, data))
        thread.start()
        return jsonify({"message": "Update accepted"}), 202

# Asynchronous update function for User microservice
def async_update_user(user_id, data):
    requests.put(f"{user_service_url}/users/{user_id}", json=data)


@app.route('/api/mainResource/<int:resource_id>/subResource', methods=['GET', 'PUT'])
@log_middleware
def sub_resource(resource_id):
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        filter_param = request.args.get('filter')

        user_response = requests.get(f"{user_service_url}/users/{resource_id}/subResource", params={'page': page, 'per_page': per_page, 'filter': filter_param})
        item_response = requests.get(f"{item_service_url}/items/{resource_id}/subResource", params={'page': page, 'per_page': per_page, 'filter': filter_param})

        return jsonify({
            'user': user_response.json() if user_response.status_code == 200 else None,
            'item': item_response.json() if item_response.status_code == 200 else None
        })

    elif request.method == 'PUT':
        data = request.json
        thread = Thread(target=async_update_user, args=(resource_id, data))
        thread.start()
        return jsonify({"message": "Update accepted"}), 202


# Synchronous method for calling sub-resources
@app.route('/api/mainResource/<int:resource_id>/fetchSync', methods=['GET'])
@log_middleware
def fetch_sync(resource_id):
    user_response = requests.get(f"{user_service_url}/users/{resource_id}")
    item_response = requests.get(f"{item_service_url}/items/{resource_id}")
    
    return jsonify({
        'user': user_response.json(),
        'item': item_response.json()
    })

# Asynchronous method for fetching both resources concurrently
@app.route('/api/mainResource/<int:resource_id>/fetchAsync', methods=['GET'])
@log_middleware
async def fetch_async(resource_id):
    async with httpx.AsyncClient() as client:
        user_request = client.get(f"{user_service_url}/users/{resource_id}")
        item_request = client.get(f"{item_service_url}/items/{resource_id}")
        user_response, item_response = await asyncio.gather(user_request, item_request)

        return jsonify({
            'user': user_response.json(),
            'item': item_response.json()
        })


# Error handling
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# Example route
@app.route('/')
def index():
    return jsonify({"message": "composite service"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
