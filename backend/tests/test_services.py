"""Testi pomoznih funkcij: ISBN in branje Goodreads izvoza."""

from datetime import date

import pytest

from app.models import ReadingStatus
from app.services.goodreads import NotGoodreadsExport, parse_export
from app.services.isbn import to_isbn13


def test_to_isbn13_converts_valid_isbns():
    assert to_isbn13("978-0-7653-1178-8") == "9780765311788"
    assert to_isbn13("0439023483") == "9780439023481"
    assert to_isbn13("076531178X") == "9780765311788"


def test_to_isbn13_rejects_invalid_isbns():
    assert to_isbn13("9780765311789") is None
    assert to_isbn13("0439023484") is None
    assert to_isbn13("12345") is None
    assert to_isbn13("not an isbn") is None


def test_parse_export_reads_statuses_isbns_and_dates():
    csv = (
        "Book Id,Title,Author,ISBN,ISBN13,Exclusive Shelf,Date Read\n"
        '1,The Final Empire,Brandon  Sanderson,"=""""","=""9780765311788""",read,2026/03/15\n'
        '2,The Hunger Games,Suzanne Collins,"=""0439023483""","=""""",currently-reading,'
        "2026/04/01\n"
        '3,Dune,Frank Herbert,"=""""","=""""",to-read,\n'
    )
    rows, skipped = parse_export(csv.encode())

    assert skipped == []
    assert [r["status"] for r in rows] == [
        ReadingStatus.read,
        ReadingStatus.reading,
        ReadingStatus.want_to_read,
    ]
    assert [r["isbn"] for r in rows] == ["9780765311788", "9780439023481", None]
    assert [r["date_read"] for r in rows] == [date(2026, 3, 15), None, None]
    assert rows[0]["author"] == "Brandon Sanderson"


def test_parse_export_rejects_other_csv():
    with pytest.raises(NotGoodreadsExport):
        parse_export(b"name,email\nAna,ana@example.com\n")
