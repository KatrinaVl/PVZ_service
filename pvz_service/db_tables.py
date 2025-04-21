from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import sql
import hashlib
from jose import jwt
from datetime import datetime
import uuid

DB_PARAMS = {
    'host': 'db',
    'database': 'pvz',
    'user': 'kv',
    'password': 'kv_password'
}

def get_conn():
    return psycopg2.connect(**DB_PARAMS)

SECRET_KEY = "TASK_AVITO"

def create_jwt_token(role):
    token = jwt.encode({"role": role}, SECRET_KEY)
    return token

def create_jwt_token_worker(role, pvzId):
    token = jwt.encode({"role": role, "pvzId" : pvzId}, SECRET_KEY)
    return token

def create_tables():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS PVZs (
                    id UUID PRIMARY KEY,
                    registration_date TIMESTAMP NOT NULL,
                    city VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(255) NOT NULL,
                    pvzId UUID REFERENCES PVZs(id)
                )
            """)
            conn.commit()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS reception (
                    id UUID PRIMARY KEY,
                    dateTime TIMESTAMP NOT NULL,
                    pvzId UUID REFERENCES PVZs(id),
                    status VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id UUID PRIMARY KEY,
                    dateTime TIMESTAMP NOT NULL,
                    type VARCHAR(255) NOT NULL,
                    receptionId UUID REFERENCES reception(id)
                )
            """)
            conn.commit()

    finally:
        conn.close()

def delete_table():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                DROP TABLE users 
            """)
            conn.commit()
    finally:
        conn.close()

def get_user(email):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            row = cur.fetchone()
            return row
    finally:
        conn.close()


def register_person(email, password, role, pvzId):
    sha = hashlib.sha256()
    sha.update(password.encode('utf-8'))

    if get_user(email) is not None:
        return jsonify({"message": "Неверный запрос", 
                        "content" : {"message": "Пользователь с такой почтой уже существует"}}), 400

    conn = get_conn()
    user_id = uuid.uuid4()
    try:
        with conn.cursor() as cur:
            if role != "worker":
                insert_query = sql.SQL("INSERT INTO users (id, email, password, role) VALUES (%s, %s, %s, %s)")
                cur.execute(insert_query, (str(user_id), email, sha.hexdigest(), role))
                conn.commit()
            else:
                insert_query = sql.SQL("INSERT INTO users (id, email, password, role, pvzId) VALUES (%s, %s, %s, %s, %s)")
                cur.execute(insert_query, (str(user_id), email, sha.hexdigest(), role, str(pvzId)))
                conn.commit()

        return jsonify({"id" : user_id,
                                    "email" : email, 
                                    "password" : password,
                                    "role" : role,
                                    "pvzId" : pvzId}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    finally:
        conn.close()

def login_person(email, password):

    user = get_user(email)
    if user is None:
        return jsonify({"message": "Не существует такого пользователя"}), 400

    check_sha = hashlib.sha256()
    check_sha.update(password.encode('utf-8'))

    if check_sha.hexdigest() != user[2]:
        return jsonify({"message": "Неверный пароль"}), 400

    if user[3] == "worker" :
        token = create_jwt_token_worker(user[3], user[4])
    else:
        token = create_jwt_token(user[3])

    return jsonify({"token": token}), 200


def add_pvz(city, date):
    pvz_id = uuid.uuid4()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            insert_query = sql.SQL("INSERT INTO PVZs (id, city, registration_date) VALUES (%s, %s, %s)")
            cur.execute(insert_query, (str(pvz_id), city, date,))
            conn.commit()

        return jsonify({"id" : str(pvz_id),
                        "city" : city,
                        "registration_date" : date  }), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    finally:
        conn.close()
    
def check_open_reception(pvzId):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, pvzId, status FROM reception WHERE pvzId=%s AND status=%s", (pvzId, "in_progress",))
            row = cur.fetchone()
            return row
    finally:
        conn.close()


def add_reception(pvzId, date) :
    reception_id = uuid.uuid4()
    if check_open_reception(pvzId) is not None:
        return jsonify({"message" : f"Приемка не закрыта"}), 400

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            insert_query = sql.SQL("INSERT INTO reception (id, dateTime, pvzId, status) VALUES (%s, %s, %s, %s)")
            cur.execute(insert_query, (str(reception_id), date, pvzId, "in_progress"))
            conn.commit()

        return jsonify({"id" : str(reception_id),
                        "dateTime" : date,
                        "pvzId" : str(pvzId),
                        "status" : "in_progress"  }), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    finally:
        conn.close()

def add_products(pvzId, type_product, date):
    product_id = uuid.uuid4()

    reception = check_open_reception(pvzId)
    if reception is None:
        return jsonify({"message" : "Приемка закрыта"}), 400

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            insert_query = sql.SQL("INSERT INTO products (id, dateTime, type, receptionId) VALUES (%s, %s, %s, %s)")
            cur.execute(insert_query, (str(product_id), date, type_product, str(reception[0])))
            conn.commit()

        return jsonify({"id" : str(product_id),
                        "dateTime" : date,
                        "type" : type_product,
                        "receptionId" : reception[0]  }), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    finally:
        conn.close()

def close_reception(pvzId):

    reception = check_open_reception(pvzId)
    if reception is None:
        return jsonify({"message" : "Приемка закрыта"}), 400

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM products WHERE receptionId=%s", (reception[0],))
            row = cur.fetchone()
            if row is None:
                return jsonify({"message" : "Не было товаров"}), 400
    finally:
        conn.close()

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            update_query = sql.SQL("UPDATE reception SET status=%s WHERE pvzId=%s")
            cur.execute(update_query, ("close", pvzId))
            conn.commit()

            cur.execute("SELECT id, dateTime, pvzId, status FROM reception WHERE pvzId=%s", (pvzId,))
            row = cur.fetchone()

        return jsonify({"id" : str(row[0]),
                        "dateTime" : row[1],
                        "pvzId" : str(row[2]),
                        "status" : row[3]  }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    finally:
        conn.close()


def check_products_in_reception(receptionId):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM products WHERE receptionId=%s", (receptionId,))
            row = cur.fetchone()
            return row
    finally:
        conn.close()


def delete_product(pvzId):

    reception = check_open_reception(pvzId)
    if reception is None:
        return jsonify({"message" : "Приемка закрыта"}), 400

    if check_products_in_reception(reception[0]) is None:
        return jsonify({"message" : "В течение приемки не было товаров"}), 400

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            delete_query = sql.SQL("DELETE FROM products WHERE id = (SELECT id FROM products ORDER BY dateTime DESC LIMIT 1)")
            cur.execute(delete_query)
            conn.commit()

        return jsonify({"message": "Последний товар успешно удален"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    finally:
        conn.close()


def get_pvzs(startDate, endDate, page, limit):

    startDate = datetime.strptime(startDate, "%a, %d %b %Y %H:%M:%S %Z")
    endDate = datetime.strptime(endDate, "%a, %d %b %Y %H:%M:%S %Z")

    startDateStr = startDate.strftime("%Y-%m-%d %H:%M:%S")
    endDateStr = endDate.strftime("%Y-%m-%d %H:%M:%S")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM PVZs WHERE registration_date >= %s AND registration_date <= %s", (startDate, endDate, ))
            pvzs = cur.fetchall()
            info = []
            for i in range((page - 1) * limit, min(len(pvzs), page * limit)):
                pvz = pvzs[i]
                pvz_json = {
                    'id': pvz[0],
                    "registrationDate" : pvz[1],
                    "city" : pvz[2],
                }
                cur.execute("SELECT * FROM reception WHERE pvzId = %s AND dateTime >= %s AND dateTime <= %s", (pvz[0], startDate, endDate,))
                receptions = cur.fetchall()
                info_reception = []
                for r in receptions:
                    reception_json = {
                        'id' : r[0],
                        'dateTime' : r[1],
                        'pvzId' : r[2],
                        'status' : r[3]}
                    
                    cur.execute("SELECT * FROM products WHERE receptionId = %s AND dateTime >= %s AND dateTime <= %s", (r[0], startDate, endDate,))
                    products = cur.fetchall()
                    info_products = []
                    for p in products:
                        info_products.append(
                        {
                            'id': p[0],
                            'dateTime': p[1],
                            'type' : p[2],
                            'receptionId': p[3]
                        })

                    info_reception.append({"reception" : reception_json, "products" : info_products})

                info.append({"a": limit, "pvz" : pvz_json, "receptions" : info_reception})
            return jsonify(info), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 400
    finally:
        conn.close()

