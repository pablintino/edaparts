#
# MIT License
#
# Copyright (c) 2024 Pablo Rodriguez Nava, @pablintino
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#


import pytest
from app import db, create_app
from tests import setup_db, teardown_db, clean_db


class TestConfig:
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://test:test@10.10.80.232,4490/altium_db_test_ut?driver=ODBC+Driver+17+for+SQL+Server"
    REDIS_URL = "redis://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture(scope="session")
def app():
    yield create_app(config_class=TestConfig)


@pytest.fixture(scope="session")
def database(app):
    assert app is not None
    setup_db(app)
    yield db
    teardown_db()


@pytest.fixture(scope="function")
def db_session(database, app):
    assert app is not None
    with app.app_context():
        clean_db()
        yield database.session
        database.session.rollback()
