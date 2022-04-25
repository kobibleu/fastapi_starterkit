def test_read_all(client):
    res = client.get("/test/?page=1&size=1&sort=id,value.des")
    assert res.status_code == 200
    assert res.json() == {
        "content": [
            {
                "id": 2,
                "value": "value 2"
            }
        ],
        "page": 1,
        "page_size": 1,
        "total_pages": 3,
        "total_elements": 3
    }
    assert res.headers["Link"] == (
        "<http://testserver/test/?page=2&size=1&sort=id,value.des>; rel=\"next\", "
        "<http://testserver/test/?page=0&size=1&sort=id,value.des>; rel=\"prev\", "
        "<http://testserver/test/?page=0&size=1&sort=id,value.des>; rel=\"first\", "
        "<http://testserver/test/?page=3&size=1&sort=id,value.des>; rel=\"last\""
    )


def test_post(client):
    res = client.post("/test/", json={"value": "value 4"})
    assert res.status_code == 201
    assert res.json() == {"id": 4, "value": "value 4"}
    assert res.headers["Location"] == "http://testserver/test/4"

    res = client.post("/test/", json={})
    assert res.status_code == 422


def test_read_one(client):
    res = client.get("/test/1")
    assert res.status_code == 200
    assert res.json() == {"id": 1, "value": "value 1"}

    res = client.get("/test/10")
    assert res.status_code == 404


def test_put(client):
    res = client.put("/test/1", json={"value": "value 4"})
    assert res.status_code == 200
    assert res.json() == {"id": 1, "value": "value 4"}


def test_delete(client):
    res = client.delete("/test/1")
    assert res.status_code == 204

    res = client.delete("/test/1")
    assert res.status_code == 404
