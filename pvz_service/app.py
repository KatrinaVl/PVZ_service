from flask import Flask, jsonify, request, Response
import psycopg2
from psycopg2 import sql
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_tables import create_tables, get_conn, delete_table, register_person, login_person, create_jwt_token, add_pvz, add_reception
from db_tables import add_products, close_reception, delete_product, get_pvzs, create_jwt_token_worker
from jose import jwt
from datetime import datetime

app = Flask(__name__)

# delete_table() # иногда полезно для тестов
create_tables()

def check_bearer_moderator():
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return False

    token = auth.split(" ")[2]

    try:
        d = jwt.decode(token, "TASK_AVITO")
        if d["role"] == "moderator":
            return True

        return False

    except Exception as e:
        return False

def check_bearer_worker(pvzId):
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return False

    token = auth.split(" ")[2]

    try:
        d = jwt.decode(token, "TASK_AVITO")
        if d["role"] == "worker" and d['pvzId'] == pvzId:
            return True

        return False

    except Exception as e:
        return False

def check_bearer_get():
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return False

    token = auth.split(" ")[2]

    try:
        d = jwt.decode(token, "TASK_AVITO")
        if d["role"] == "moderator" or d["role"] == "worker":
            return True

        return False

    except Exception as e:
        return False

@app.route('/dummyLogin', methods=['POST'])
def dummyLogin():
    data = request.get_json()
    if data['role'] in ["client", "moderator"]:
        return jsonify({"token" : create_jwt_token(data['role'])}), 200

    if data['role'] == "worker":
        return jsonify({"token" : create_jwt_token_worker(data['role'], data['pvzId'])}), 200

    return jsonify({"message": "Несуществующая роль"}), 400

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    pvzId = "None"

    if role not in ["client", "moderator", "worker"]:
        return jsonify({"message": "Несуществующая роль"}), 400

    if role == "worker":
        pvzId = data['pvzId']

    return register_person(data['email'], data['password'], data['role'], pvzId)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    return login_person(data['email'], data['password'])

@app.route('/pvz', methods=['POST'])
def pvz_post():
    if not check_bearer_moderator():
        return jsonify({"message": f"Доступ запрещен"}), 403

    data = request.get_json()

    if "city" not in data or data['city'] not in ["Москва", "Санкт-Петербург", "Казань"]:
        return jsonify({"message": f"Неверный город. Доступные города: Москва, Санкт-Петербург, Казань"}), 400

    return add_pvz(data['city'], datetime.now())


@app.route('/pvz', methods=['GET'])
def pvz_get():
    if not (check_bearer_get()):
        return jsonify({"message": f"Доступ запрещен"}), 403

    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    return get_pvzs(startDate, endDate, page, limit)


@app.route('/receptions', methods=['POST'])
def receptions():
    data = request.get_json()

    if not check_bearer_worker(data['pvzId']):
        return jsonify({"message": f"Доступ запрещен"}), 403

    return add_reception(data['pvzId'], datetime.now())

@app.route('/products', methods=['POST'])
def products():
    data = request.get_json()

    if not check_bearer_worker(data['pvzId']):
        return jsonify({"message": f"Доступ запрещен"}), 403
    
    if type_product not in ["электроника", "одежда", "обувь"]:
        return jsonify({"message": f"Неверный тип товара"}), 400
    date = datetime.now()

    return add_products(data['pvzId'], data['type'], date)

@app.route('/pvz/<pvzId>/close_last_reception', methods=['POST'])
def close_last_reception(pvzId):
    if not check_bearer_worker(pvzId):
        return jsonify({"message": f"Доступ запрещен"}), 403

    return close_reception(pvzId)


@app.route('/pvz/<pvzId>/delete_last_product', methods=['POST'])
def delete_last_product(pvzId):
    if not check_bearer_worker(pvzId):
        return jsonify({"message": f"Доступ запрещен"}), 403

    return delete_product(pvzId)





if __name__ == "__main__":
    
    app.run(debug=True, host='0.0.0.0', port='8090')