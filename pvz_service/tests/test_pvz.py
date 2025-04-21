import pytest
from ..app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def test_dummy_login_client(client):
    resp = client.post('/dummyLogin', json={"role": "client"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'token' in data

def test_dummy_login_moderator(client):
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'token' in data

def test_dummy_login_worker(client):
    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : "6b1e5e43-bb05-4aca-91c4-6c52e2739357"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'token' in data

def test_dummy_login_wrong_role(client):
    resp = client.post('/dummyLogin', json={"role": "dancer"})
    assert resp.status_code == 400
    

def test_register_wrong_role(client):
    resp = client.post('/register', json={
        "email": "user@examplelksjbf.com",
        "password": "your_password",
        "role": "dancer",
        "pvzId" : "6b1e5e43-bb05-4aca-91c4-6c52e2739357"
    })
    assert resp.status_code == 400
    

def test_register_moderator(client):
    resp = client.post('/register', json={
        "email": "user@exampfdvscxxvsldvjhfcdfesdfvxvdfvaxcalksjbf.com",
        "password": "your_passworaerhad",
        "role": "moderator"
    })
    assert resp.status_code == 201
    data = resp.get_json()

    assert 'id' in data
    assert data['email'] == "user@exampfdvscxxvsldvjhfcdfesdfvxvdfvaxcalksjbf.com"
    assert data['password'] == "your_passworaerhad"
    assert data['role'] == "moderator"


def test_register_same_email(client):
    resp = client.post('/register', json={
        "email": "user@exampfdvldvdfexvdfvalksjbf.com",
        "password": "your_passworaerhad",
        "role": "moderator",
        "pvzId" : "6b1e5e43-bb05-4aca-91c4-6c52e2739357"
    })
    assert resp.status_code == 400

def test_register_login_do_not_exist(client):
    resp = client.post('/login', json={
        "email": "user@examplelksjbf.com",
        "password": "your_password"
    })
    assert resp.status_code == 400

def test_register_login_wrong_password(client):
    resp = client.post('/login', json={
        "email": "user@exampfdvldvdfexvdfvalksjbf.com",
        "password": "your_passworaerhadsfv"
    })
    assert resp.status_code == 400

def test_register_login(client):
    resp = client.post('/login', json={
        "email": "user@exampfdvldvdfexvdfvalksjbf.com",
        "password": "your_passworaerhad"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'token' in data

def test_pvz_post(client):
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Москва"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    assert 'id' in data and 'registration_date' in data


def test_pvz_post_forbidden(client):
    resp = client.post('/dummyLogin', json={"role": "client"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Москва"
    }, headers=headers)
    
    assert resp.status_code == 403

def test_pvz_post_fwrong_city(client):
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Унеча"
    }, headers=headers)
    
    assert resp.status_code == 400


def test_receptions(client):
    ## создание пвз
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Москва"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    pvzId = data['id']

    ## создание reception

    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : pvzId})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post('/receptions', json={
        "pvzId" : pvzId
    }, headers=headers)
        
    assert resp.status_code == 201

    data = resp.get_json()
    assert data['pvzId'] == pvzId
    assert data['status'] == "in_progress"
    assert 'id' in data and 'dateTime' in data

def test_receptions_forbidden(client):

    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post('/receptions', json={
        "pvzId" : "jgvhg"
    }, headers=headers)
        
    assert resp.status_code == 403

def test_receptions_opened_reception(client):

    ## создание пвз
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Москва"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    pvzId = data['id']

    ## создание reception

    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : pvzId})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post('/receptions', json={
        "pvzId" : pvzId
    }, headers=headers)
        
    assert resp.status_code == 201

    data = resp.get_json()
    assert data['pvzId'] == pvzId
    assert data['status'] == "in_progress"
    assert 'id' in data and 'dateTime' in data

    ## создание еще reception

    resp = client.post('/receptions', json={
        "pvzId" : pvzId
    }, headers=headers)
        
    assert resp.status_code == 400


def test_products(client):
    ## создание пвз
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Москва"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    pvzId = data['id']

    ## создание reception

    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : pvzId})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post('/receptions', json={
        "pvzId" : pvzId
    }, headers=headers)
        
    assert resp.status_code == 201

    data = resp.get_json()
    reception_id = data['id']

    ## добавление продукта

    resp = client.post('/products', json={
        "pvzId" : pvzId,
        "type" : "одежда"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    assert data['type'] == 'одежда'
    assert data['receptionId'] == reception_id
    assert 'id' in data and 'dateTime' in data


def test_products_forbidden(client):
    resp = client.post('/dummyLogin', json={"role": "client"})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}


    resp = client.post('/products', json={
        "pvzId" : "kjgvhg",
        "type" : "одежда"
    }, headers=headers)

    assert resp.status_code == 403

def test_products_wrong_type(client):
    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : "hbvkhjwbd"})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}


    resp = client.post('/products', json={
        "pvzId" : "hbvkhjwbd",
        "type" : "куклы"
    }, headers=headers)

    assert resp.status_code == 400


def test_products_wrong_pvz(client):
    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : "hbvkhjwbd"})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}


    resp = client.post('/products', json={
        "pvzId" : "gfgbg",
        "type" : "одежда"
    }, headers=headers)

    assert resp.status_code == 403


def test_close_reception(client):
    ## создание пвз
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Москва"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    pvzId = data['id']

    ## создание reception

    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : pvzId})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post('/receptions', json={
        "pvzId" : pvzId
    }, headers=headers)
        
    assert resp.status_code == 201

    data = resp.get_json()
    reception_id = data['id']

    ## добавление продукта

    resp = client.post('/products', json={
        "pvzId" : pvzId,
        "type" : "одежда"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    assert data['type'] == 'одежда'
    assert data['receptionId'] == reception_id
    assert 'id' in data and 'dateTime' in data

    ## удаление приемки

    resp = client.post(f'/pvz/{pvzId}/close_last_reception', json={}, headers=headers)

    assert resp.status_code == 200
    data = resp.get_json()
    assert data['pvzId'] == pvzId
    assert data['status'] == "close"
    assert 'id' in data and 'dateTime' in data

def test_products_close_reception(client):
    ## создание пвз
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Москва"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    pvzId = data['id']

    ## создание reception

    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : pvzId})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post('/receptions', json={
        "pvzId" : pvzId
    }, headers=headers)
        
    assert resp.status_code == 201

    data = resp.get_json()
    reception_id = data['id']

    ## добавление продукта

    resp = client.post('/products', json={
        "pvzId" : pvzId,
        "type" : "одежда"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    assert data['type'] == 'одежда'
    assert data['receptionId'] == reception_id
    assert 'id' in data and 'dateTime' in data

    ## удаление приемки

    resp = client.post(f'/pvz/{pvzId}/close_last_reception', json={}, headers=headers)

    assert resp.status_code == 200
    data = resp.get_json()
    assert data['pvzId'] == pvzId
    assert data['status'] == "close"
    assert 'id' in data and 'dateTime' in data

    ## снова добавление продукта

    resp = client.post('/products', json={
        "pvzId" : pvzId,
        "type" : "одежда"
    }, headers=headers)

    assert resp.status_code == 400


def test_close_reception_closed(client):
    ## создание пвз
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Москва"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    pvzId = data['id']

    ## создание reception

    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : pvzId})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post('/receptions', json={
        "pvzId" : pvzId
    }, headers=headers)
        
    assert resp.status_code == 201

    data = resp.get_json()
    reception_id = data['id']

    ## добавление продукта

    resp = client.post('/products', json={
        "pvzId" : pvzId,
        "type" : "одежда"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    assert data['type'] == 'одежда'
    assert data['receptionId'] == reception_id
    assert 'id' in data and 'dateTime' in data

    ## удаление приемки

    resp = client.post(f'/pvz/{pvzId}/close_last_reception', json={}, headers=headers)

    assert resp.status_code == 200
    data = resp.get_json()
    assert data['pvzId'] == pvzId
    assert data['status'] == "close"
    assert 'id' in data and 'dateTime' in data

    ## снова удаление

    resp = client.post(f'/pvz/{pvzId}/close_last_reception', json={}, headers=headers)

    assert resp.status_code == 400



def test_close_reception_forbidden(client):
    resp = client.post('/dummyLogin', json={"role": "client"})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post(f'/pvz/{"jgvkjg"}/close_last_reception', json={}, headers=headers)

    assert resp.status_code == 403

def test_close_reception_closed_without_products(client):
    ## создание пвз
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Москва"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    pvzId = data['id']

    ## создание reception

    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : pvzId})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post('/receptions', json={
        "pvzId" : pvzId
    }, headers=headers)
        
    assert resp.status_code == 201

    data = resp.get_json()
    reception_id = data['id']

    ## удаление приемки

    resp = client.post(f'/pvz/{pvzId}/close_last_reception', json={}, headers=headers)

    assert resp.status_code == 400


def test_delete_product(client):
    ## создание пвз
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Москва"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    pvzId = data['id']

    ## создание reception

    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : pvzId})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post('/receptions', json={
        "pvzId" : pvzId
    }, headers=headers)
        
    assert resp.status_code == 201

    data = resp.get_json()
    reception_id = data['id']

    ## добавление продукта

    resp = client.post('/products', json={
        "pvzId" : pvzId,
        "type" : "одежда"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    assert data['type'] == 'одежда'
    assert data['receptionId'] == reception_id
    assert 'id' in data and 'dateTime' in data

    ## удаление товара

    resp = client.post(f'/pvz/{pvzId}/delete_last_product', json={}, headers=headers)

    assert resp.status_code == 200

    # проверка на удаление, если нет товаров

    resp = client.post(f'/pvz/{pvzId}/delete_last_product', json={}, headers=headers)

    assert resp.status_code == 400
    

def test_delete_product_without_reception(client):
    ## создание пвз
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.post('/pvz', json={
        "city" : "Москва"
    }, headers=headers)

    assert resp.status_code == 201
    data = resp.get_json()
    pvzId = data['id']

    ## создание reception

    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : pvzId})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post('/receptions', json={
        "pvzId" : pvzId
    }, headers=headers)
        
    assert resp.status_code == 201

    data = resp.get_json()
    reception_id = data['id']

    ## добавление продукта

    resp = client.post('/products', json={
        "pvzId" : pvzId,
        "type" : "одежда"
    }, headers=headers)

    assert resp.status_code == 201

    # закрытие приемки

    resp = client.post(f'/pvz/{pvzId}/close_last_reception', json={}, headers=headers)

    assert resp.status_code == 200

    ## удаление товара

    resp = client.post(f'/pvz/{pvzId}/delete_last_product', json={}, headers=headers)

    assert resp.status_code == 400


def test_delete_product_forbidden(client):
    resp = client.post('/dummyLogin', json={"role": "client"})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    ## удаление товара

    resp = client.post(f'/pvz/{"sfdv"}/delete_last_product', json={}, headers=headers)

    assert resp.status_code == 403


def test_pvz_get_forbidden(client):
    resp = client.post('/dummyLogin', json={"role": "client"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.get(
        '/pvz',
        query_string={
            'startDate': 'Sun, 20 Apr 2025 17:00:00 GMT',
            'endDate': 'Sun, 20 Apr 2025 17:30:59 GMT'
        },
        headers=headers
    )
    assert resp.status_code == 403


def test_pvz_get(client):
    resp = client.post('/dummyLogin', json={"role": "moderator"})
    assert resp.status_code == 200
    data = resp.get_json()
    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}
    resp = client.get(
        '/pvz',
        query_string={
            'startDate': 'Sun, 20 Apr 2025 17:00:00 GMT',
            'endDate': 'Sun, 20 Apr 2025 17:30:59 GMT'
        },
        headers=headers
    )
    assert resp.status_code == 200
    