import json
from pathlib import Path

import pytest

from src.htmx_experiments.contact import Contact


@pytest.fixture
def clean_db():
    Contact.db.clear()


@pytest.fixture
def handle_contact_json():
    "Creates and removes the contact.json created in the project root due to buggy Contact.save after a test is done."
    cwd = Path.cwd()
    path = cwd / "contacts.json"
    path.touch()
    yield None
    path.unlink()


@pytest.fixture
def sample_contact():
    return Contact(
        first="John", last="Doe", phone="1234567890", email="john@example.com"
    )


def test_init(sample_contact: Contact):
    assert sample_contact.id is None
    assert sample_contact.first == "John"
    assert sample_contact.last == "Doe"
    assert sample_contact.phone == "1234567890"
    assert sample_contact.email == "john@example.com"


def test_str(sample_contact: Contact):
    contact_str = str(sample_contact)
    data = json.loads(contact_str)

    assert isinstance(contact_str, str)
    assert "John" in contact_str
    assert "Doe" in contact_str
    assert "1234567890" in contact_str
    assert "john@example.com" in contact_str
    assert data["errors"] == {}


def test_update(sample_contact: Contact):
    sample_contact.update(
        first="Jane", last="Smith", phone="0987654321", email="jane@example.com"
    )

    assert sample_contact.first == "Jane"
    assert sample_contact.last == "Smith"
    assert sample_contact.phone == "0987654321"
    assert sample_contact.email == "jane@example.com"


def test_validate_missing_email(sample_contact: Contact):
    sample_contact.email = None
    valid = sample_contact.validate()

    assert not valid
    assert "email" in sample_contact.errors


def test_validate_unique_email(sample_contact: Contact):
    Contact.db[1] = Contact(
        id_=1, first="Jane", last="Smith", phone="0987654321", email="john@example.com"
    )

    valid = sample_contact.validate()
    assert not valid
    assert "email" in sample_contact.errors


def test_save_new_contact(handle_contact_json, sample_contact: Contact):
    Contact.db.clear()
    valid = sample_contact.save()
    assert valid
    assert sample_contact.id is not None
    assert len(Contact.db) == 1


def test_save_duplicate_email(handle_contact_json, sample_contact: Contact):
    Contact.db[1] = Contact(
        id_=1, first="Jane", last="Smith", phone="0987654321", email="john@example.com"
    )

    valid = sample_contact.save()
    assert not valid
    assert "email" in sample_contact.errors


def test_delete(handle_contact_json, sample_contact: Contact):
    sample_contact.id = 1
    Contact.db[1] = sample_contact
    n = len(Contact.db)

    sample_contact.delete()
    assert len(Contact.db) == n - 1


def test_count():
    Contact.db = {
        i: Contact(
            id_=i,
            first=f"Name{i}",
            last="Test",
            phone="1234567890",
            email=f"name{i}@example.com",
        )
        for i in range(1, 11)
    }
    assert Contact.count() == 10


def test_all_paginated():
    # Create 150 contacts
    Contact.db = {i: Contact(id_=i) for i in range(1, 151)}

    first_page = Contact.all()
    assert len(first_page) == 100

    second_page = Contact.all(page=2)
    assert len(second_page) == 50


def test_search():
    contact = Contact(
        id_=1,
        first="Alice",
        last="Smith",
        phone="1234567890",
        email="alice@example.com",
    )
    Contact.db[1] = contact

    # Search for substring in different fields
    search_results = Contact.search("ali")

    assert len(search_results) == 1
    assert search_results[0].id == 1


def test_find(sample_contact: Contact):
    sample_contact.id = 1
    Contact.db[1] = sample_contact

    found_contact = Contact.find(1)
    not_found = Contact.find(999)

    assert found_contact is not None
    assert found_contact.id == 1
    assert not_found is None


@pytest.mark.xfail(reason="Bug - Path to contacts.json hardcoded in Contact.")
def test_load_save_db(handle_contact_json):
    # Create a test contact
    contact = Contact(
        id_=1, first="Test", last="User", phone="1234567890", email="test@example.com"
    )
    contact.save()

    # Save and load the database
    contact.load_db()

    assert len(contact.db) == 1
    assert "Test" in str(contact.db[1])
