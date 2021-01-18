from flask import request, abort, g
from flask import current_app as app

from . import register
from arch.auth.token import encode_json
from arch.auth import login_required
from arch.storage.mysql.model import User, Organization


@register.route("/login", methods=["POST"])
def login():
    """
    organization: String
    username: String
    password: String
    :return:
    """
    username = request.form.get("username")
    password = request.form.get("password")
    organization = request.form.get("organization")

    result = app.db.query(User).join(
        Organization, Organization.name == organization
    ).filter_by(username=username).first()
    if result:
        user = app.db.query(User).filter_by(username=username).first()
        if user.verify_password(password):
            data = {
                "user_uid": user.uid,
                "user_name": username,
                "organization_uid": user.organization_uid,
                "role_id": user.role_id
            }
            token = encode_json(data).decode(encoding="utf-8")
            return token
    abort(403)


@register.route("/verify", methods=["GET"])
@login_required
def verify():
    print(g.token)
    return ""
