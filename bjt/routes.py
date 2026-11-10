from flask import Blueprint, render_template

from .engineering import DEFAULTS

bp = Blueprint("bias", __name__)


@bp.get("/")
def index():
    return render_template("index.html", values=DEFAULTS, errors={}, result=None)
