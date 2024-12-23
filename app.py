from flask import Flask, request, jsonify, g
import httpx
from dotenv import load_dotenv
import requests
import os
import uuid
from functools import wraps
from threading import Thread
from time import time
from flask_cors import CORS

# Load environment variables from .env
load_dotenv(dotenv_path=".env")

app = Flask(__name__)

user_service_url = os.getenv("USER_SERVICE_URL")
print("User service: ", user_service_url)
item_service_url = os.getenv("ITEM_SERVICE_URL")
CORS(app, resources={r"/*": {"origins": "http://3.147.35.222:4200"}})

def correlation_id_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'GET':  
            correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
            g.correlation_id = correlation_id 
        return f(*args, **kwargs)
    return decorated_function

def log_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time()
        print(f"[Correlation ID: {g.get('correlation_id', 'N/A')}] Before {request.method} request to {request.path}")
        response = f(*args, **kwargs)
        print(f"[Correlation ID: {g.get('correlation_id', 'N/A')}] After {request.method} request to {request.path}, took {time() - start_time}s")
        return response
    return decorated_function


@app.route('/api/mainResource', methods=['GET', 'POST'])
@correlation_id_middleware
@log_middleware
def main_resource():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        print(f"[Correlation ID: {g.correlation_id}] Fetching items from item service")
        item_response = requests.get(
            f"{item_service_url}/items",
            params={'page': page, 'per_page': per_page},
            headers={'X-Correlation-ID': g.correlation_id}
        )

        return jsonify({
            'items': item_response.json()
        })

    elif request.method == 'POST':
        data = request.json

        if 'username' in data:
            print("Creating user in user service")
            user_response = requests.post(f"{user_service_url}/users", json=data)
            return jsonify(user_response.json()), user_response.status_code
        elif 'name' in data:
            print("Creating item in item service")
            item_response = requests.post(f"{item_service_url}/items", json=data)
            return jsonify(item_response.json()), item_response.status_code
        else:
            return jsonify({"error": "Invalid data. Please provide either 'username' or 'name'."}), 400


@app.route('/api/mainResource/<int:resource_id>', methods=['GET', 'PUT'])
@correlation_id_middleware
@log_middleware
def main_resource_id(resource_id):
    if request.method == 'GET':
        user_response = requests.get(
            f"{user_service_url}/users/{resource_id}",
            headers={'X-Correlation-ID': g.correlation_id}
        )
        item_response = requests.get(
            f"{item_service_url}/items/{resource_id}",
            headers={'X-Correlation-ID': g.correlation_id}
        )

        return jsonify({
            'user': user_response.json() if user_response.status_code == 200 else None,
            'item': item_response.json() if item_response.status_code == 200 else None
        })

    elif request.method == 'PUT':
        data = request.json
        thread = Thread(target=async_update_user, args=(resource_id, data))
        thread.start()
        return jsonify({"message": "Update accepted"}), 202


def async_update_user(user_id, data):
    requests.put(f"{user_service_url}/users/{user_id}", json=data)


@app.route('/api/mainResource/<int:resource_id>/subResource', methods=['GET', 'PUT'])
@correlation_id_middleware
@log_middleware
def sub_resource(resource_id):
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        filter_param = request.args.get('filter')

        user_response = requests.get(
            f"{user_service_url}/users/{resource_id}/subResource",
            params={'page': page, 'per_page': per_page, 'filter': filter_param},
            headers={'X-Correlation-ID': g.correlation_id}
        )
        item_response = requests.get(
            f"{item_service_url}/items/{resource_id}/subResource",
            params={'page': page, 'per_page': per_page, 'filter': filter_param},
            headers={'X-Correlation-ID': g.correlation_id}
        )

        return jsonify({
            'user': user_response.json() if user_response.status_code == 200 else None,
            'item': item_response.json() if item_response.status_code == 200 else None
        })

    elif request.method == 'PUT':
        data = request.json
        thread = Thread(target=async_update_user, args=(resource_id, data))
        thread.start()
        return jsonify({"message": "Update accepted"}), 202


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
