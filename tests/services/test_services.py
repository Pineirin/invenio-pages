# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import pytest

from invenio_pages.proxies import current_pages_service
from invenio_pages.records.errors import PageNotFoundError


def test_page_read(module_scoped_pages_fixture, simple_user_identity):
    """Test read service function."""
    page = current_pages_service.read(simple_user_identity, 1).data
    page.pop("created")
    page.pop("updated")
    expected_data = {
        "title": "Page for Dogs!",
        "description": "",
        "url": "/dogs",
        "content": "Generic dog.",
        "id": "1",
        "template_name": "invenio_pages/default.html",
        "links": {"self": "https://127.0.0.1:5000/api/pages/1"},
    }
    assert page == expected_data


def test_page_read_by_url(module_scoped_pages_fixture, simple_user_identity):
    """Test read_by_url service function."""
    page = current_pages_service.read_by_url(simple_user_identity, "/dogs").data
    page.pop("created")
    page.pop("updated")
    expected_data = {
        "title": "Page for Dogs!",
        "description": "",
        "url": "/dogs",
        "content": "Generic dog.",
        "id": "1",
        "template_name": "invenio_pages/default.html",
        "links": {"self": "https://127.0.0.1:5000/api/pages/1"},
    }
    assert page == expected_data


def test_search(module_scoped_pages_fixture, simple_user_identity):
    """Test search service function."""
    pages = current_pages_service.search(simple_user_identity)
    assert pages.total == 4

    pages = current_pages_service.search(simple_user_identity, {"size": 2})
    assert pages.total == 2

    pages = current_pages_service.search(simple_user_identity, {"sort": "title"})
    assert pages._results[0].id == 3

    pages = current_pages_service.search(
        simple_user_identity, {"sort": "title", "sort_direction": "desc"}
    )
    assert pages._results[0].id == 4

    pages = current_pages_service.search(
        simple_user_identity, {"sort_direction": "desc"}
    )

    assert pages._results[0].id == 4

    pages = current_pages_service.search(
        simple_user_identity, {"size": 3, "sort": "title", "sort_direction": "desc"}
    )
    assert pages._results[0].id == 4

    pages = current_pages_service.search(simple_user_identity, {"sort": "url"})
    assert pages._results[0].id == 3
    assert pages._results[3].id == 4

    pages = current_pages_service.search(simple_user_identity, {"q": "Generic dog"})
    assert pages.total == 1

    pages = current_pages_service.search(
        simple_user_identity, {"q": "dog", "sort_direction": "desc"}
    )
    assert pages.total == 3
    assert pages._results[0].id == 4


def test_create(module_scoped_pages_fixture, superuser_identity):
    data = {
        "url": "/astures",
        "title": "Astures",
        "content": "Astures",
        "description": "Los astures (astures en latín) fueron un grupo de pueblos celtas...",
        "template_name": "invenio_pages/default.html",
    }
    page = current_pages_service.create(superuser_identity, data)
    assert page["title"] == "Astures"

    id = page["id"]
    assert current_pages_service.read(superuser_identity, id)["title"] == "Astures"

    page = current_pages_service.create(superuser_identity, data)

    assert page.to_obj == None


def test_delete(module_scoped_pages_fixture, superuser_identity):
    data = {
        "url": "/cantabros",
        "title": "Cantabros",
        "content": "Cantabros",
        "description": "El término cántabros...",
        "template_name": "invenio_pages/default.html",
    }
    page = current_pages_service.create(superuser_identity, data)
    id = page["id"]
    assert current_pages_service.read(superuser_identity, id)["title"] == "Cantabros"
    current_pages_service.delete(superuser_identity, page["id"])
    with pytest.raises(PageNotFoundError):
        current_pages_service.read(superuser_identity, id)


def test_update(module_scoped_pages_fixture, superuser_identity):
    data = {
        "url": "/lusitanos",
        "title": "Lusitanos",
        "content": "Lusitanos",
        "description": "El término lusitanos...",
    }
    assert current_pages_service.read(superuser_identity, 1)["title"] != "Lusitanos"
    current_pages_service.update(superuser_identity, data, 1)

    page = current_pages_service.read(superuser_identity, 1)
    assert page["title"] == "Lusitanos"
    assert page["template_name"] == "invenio_pages/default.html"


def test_delete_all(module_scoped_pages_fixture, superuser_identity):
    current_pages_service.delete_all(superuser_identity)
    pages = current_pages_service.search(superuser_identity)
    assert pages.total == 0
