from flask import Flask

from .formatting import format_current, format_delta, format_voltage, format_voltage_short
from .routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.jinja_env.filters["current"] = format_current
    app.jinja_env.filters["voltage"] = format_voltage
    app.jinja_env.filters["volts"] = format_voltage_short
    app.jinja_env.filters["delta"] = format_delta
    return app
