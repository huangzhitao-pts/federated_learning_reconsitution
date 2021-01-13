from uuid import uuid1

from flask import request, g, abort, jsonify
from flask import current_app as app

from . import register
from arch.auth import login_required
from arch.storage.model.register_table import Workspace, Organization, User
from arch.storage.sql_result_to_dict import model_to_dict


@register.route("/workspace/", methods=["GET", "POST"])
@login_required
def workspace():
    """
    GET: look over workspace list or single workspace

    POST： create workspace
    data = {
        "name": String,
        "description": String,
        "party_info": {
            "party_list": [
                {"organization": String, "user_uid": String}
            ]
        }
    }
    :return:
    """
    req_method = request.method.upper()
    if req_method == "GET":
        uid = request.args.get("uid")
        if uid:
            result = app.db.query(Workspace).filter_by(
                uid=uid,
                user_uid=g.token["user_uid"]
            ).first()

        else:
            result = app.db.query(Workspace).filter_by(
                user_uid=g.token["user_uid"]
            ).all()
        if result:
            return jsonify(model_to_dict(result))

    elif req_method == "POST":
        data = request.get_json()
        workspace_uid=uuid1()

        # party exist
        for i in data["party_info"]["party_list"]:
            r = app.db.query(User).join(
                Organization, Organization.uid == User.organization_uid
            ).filter(
                User.uid == i["user_uid"], Organization.name == i["organization"]
            ).with_entities(
                Organization.uid
            ).first()
            print(r)
            if not r:
                abort(403)
            app.db.add(Workspace(
                uid=workspace_uid,
                name=data["name"],
                description=data["description"],
                user_uid=i["user_uid"],
                organization_uid=r[0]
            ))
        else:
            app.db.add(Workspace(
                uid=workspace_uid,
                name=data["name"],
                description=data["description"],
                user_uid=g.token["user_uid"],
                organization_uid=g.token["organization_uid"],
                is_creator="1"
            ))
            app.db.commit()
    return ""


def db_select(db, model, result=None, **kwargs):
    resp = db.query(model).filter_by(**kwargs).all()
    return resp if result else bool(resp)
