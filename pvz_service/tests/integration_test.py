import pytest
from ..app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()


def test_integration(client):
    
    #создается пвз
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


    # добавляется приемка

    resp = client.post('/dummyLogin', json={"role": "worker", "pvzId" : pvzId})
    assert resp.status_code == 200
    data = resp.get_json()

    token = data['token']
    headers = {"Authorization": f"Bearer : {token}"}

    resp = client.post('/receptions', json={
        "pvzId" : pvzId
    }, headers=headers)
        
    assert resp.status_code == 201

    # 50 товаров

    for i in range(50):

        resp = client.post('/products', json={
            "pvzId" : pvzId,
            "type" : "одежда"
        }, headers=headers)

        assert resp.status_code == 201

    ## удаление приемки

    resp = client.post(f'/pvz/{pvzId}/close_last_reception', json={}, headers=headers)

    assert resp.status_code == 200