import logging
import os
import secrets

import bleach
from flask import request, Flask
from flask_sqlalchemy import SQLAlchemy
from gevent import pywsgi
from sqlalchemy.exc import IntegrityError
from flask_wtf.csrf import CSRFProtect
from models.loader import RoutesLoader
from models.singleton import Singleton


class WebManager(metaclass=Singleton):
    _SSL_KEY_PATH = os.environ.get("SSL_KEY_PATH", "./ssl/origin.key")
    _SSL_CERT_PATH = os.environ.get("SSL_CERT_PATH", "./ssl/origin.pem")

    def __init__(self):
        self._app = Flask(__name__)
        database_path = f"sqlite:///{self._app.root_path}/data.db"
        self._app.config["SQLALCHEMY_DATABASE_URI"] = database_path
        self._app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self._app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
        self._app.jinja_env.trim_blocks = True
        self._app.jinja_env.lstrip_blocks = True
        self._database = SQLAlchemy(self._app)
        self._session = self._database.session
        self.model = self._database.Model
        self.route = self._app.route
        CSRFProtect(self._app)

    @staticmethod
    def __load_routes():
        routes = RoutesLoader()
        routes.load_all()

    @staticmethod
    def get_param_and_sanitize(param: str) -> str:
        user_input = request.form.get(param)
        # Try to fetch from JSON if not in form data
        if not user_input:
            user_input = request.json.get(param)
        return bleach.clean(user_input)

    def __commit(self) -> bool:
        try:
            self._session.commit()
            return True
        # Handle potential database commit errors
        except IntegrityError as e:
            logging.error("Database commit error: %s", e)
            return False

    def serve(self, host: str, port: int):
        self.__load_routes()
        server_kwargs = {}
        if os.path.isfile(self._SSL_KEY_PATH) and os.path.isfile(self._SSL_CERT_PATH):
            server_kwargs["keyfile"] = self._SSL_KEY_PATH
            server_kwargs["certfile"] = self._SSL_CERT_PATH
            logging.info("Starting HTTPS server at [%s, %s]", host, port)
        else:
            logging.info("Starting HTTP server at [%s, %s] (no TLS certificates found)", host, port)
        s1 = pywsgi.WSGIServer((host, port), self._app, **server_kwargs)
        with self._app.app_context():
            self._database.create_all()
            s1.serve_forever()

    def add_and_commit(self, model) -> bool:
        self._session.add(model)
        return self.__commit()

    def del_and_commit(self, model) -> bool:
        self._session.delete(model)
        return self.__commit()

    def query(self, model_class, **filters):
        return self._session.query(model_class).filter_by(**filters).all()
