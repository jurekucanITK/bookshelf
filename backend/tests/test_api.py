"""Testi API-ja: iskanje, knjiznica, posoje in branje."""

from datetime import date

from app.services import openlibrary


def test_search_requires_four_characters(client):
    response = client.get("/books/search", params={"q": "abc"})

    assert response.status_code == 422


def test_search_by_isbn_returns_catalog_edition(client, edition):
    response = client.get("/books/search", params={"q": "978-0-7653-1178-8"})

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["edition_id"] == edition.id
    assert results[0]["work_id"] == edition.work_id
    assert results[0]["isbn"] == "9780765311788"


def test_search_adds_openlibrary_results_without_duplicates(client, edition, monkeypatch):
    def fake_search(query, limit):
        return [
            {"openlibrary_key": "/works/OL5738148W", "title": "The Final Empire",
             "author": "Brandon Sanderson"},
            {"openlibrary_key": "/works/OL5738150W", "title": "The Well of Ascension",
             "author": "Brandon Sanderson"},
        ]

    monkeypatch.setattr(openlibrary, "search", fake_search)
    response = client.get("/books/search", params={"q": "final empire"})

    assert response.status_code == 200
    results = response.json()["results"]
    assert [r["openlibrary_key"] for r in results] == ["/works/OL5738148W", "/works/OL5738150W"]
    assert results[0]["work_id"] == edition.work_id
    assert results[1]["work_id"] is None


def test_library_duplicate_needs_confirmation(client, user, edition):
    first = client.post("/library", json={"edition_id": edition.id})
    again = client.post("/library", json={"edition_id": edition.id})
    confirmed = client.post(
        "/library", json={"edition_id": edition.id, "confirm_duplicate": True}
    )

    assert first.status_code == 201
    assert again.status_code == 409
    assert again.json()["detail"] == "already_owned"
    assert confirmed.status_code == 201
    assert len(client.get("/library").json()) == 2


def test_loan_return_and_history(client, user, edition):
    book_id = client.post("/library", json={"edition_id": edition.id}).json()["id"]

    loan = client.post(f"/library/{book_id}/loans", json={"borrower_name": "Ana"})
    assert loan.status_code == 201
    second = client.post(f"/library/{book_id}/loans", json={"borrower_name": "Bor"})
    assert second.status_code == 409
    assert second.json()["detail"] == "already_loaned"

    returned = client.post(f"/loans/{loan.json()['id']}/return", json={})
    assert returned.status_code == 200
    assert returned.json()["returned_at"] == date.today().isoformat()

    again = client.post(f"/library/{book_id}/loans", json={"borrower_name": "Bor"})
    assert again.status_code == 201

    history = client.get("/loans", params={"active": "false"}).json()
    assert [h["id"] for h in history] == [loan.json()["id"]]
    assert history[0]["borrower_name"] == "Ana"


def test_finished_book_counts_towards_goal(client, user, edition):
    work_id = edition.work_id
    assert client.put(f"/reading/{work_id}", json={"status": "reading"}).status_code == 200

    response = client.put(f"/reading/{work_id}", json={"status": "read"})

    assert response.status_code == 200
    entry = response.json()
    assert entry["status"] == "read"
    assert len(entry["sessions"]) == 1
    assert entry["sessions"][0]["finished_at"] == date.today().isoformat()

    year = date.today().year
    goal = client.put(f"/goals/{year}", json={"target_books": 12})
    assert goal.status_code == 200
    assert goal.json() == {"year": year, "target_books": 12, "read_count": 1}
