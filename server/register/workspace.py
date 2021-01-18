from uuid import uuid1
from functools import partial

from flask import request, g, abort, jsonify
from flask import current_app as app

from . import register
from arch.auth import login_required
from arch.storage.mysql.model import Workspace, Organization, \
    User, WorkspaceDataset, DataSet
from arch.storage.mysql.sql_result_to_dict import model_to_dict


def db_select_(model, db, result=None, **kwargs):
    resp = db.query(model).filter_by(**kwargs)
    return resp.all() if result else resp.first()


db_workspace = partial(db_select_, Workspace)
db_dataset = partial(db_select_, DataSet)
db_workspace_dataset = partial(db_select_, WorkspaceDataset)


@register.route("/workspace/", methods=["GET", "POST", "PATCH", "DELETE"])
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

    PATCH
    data = {
        "uid": String,
        "party_list": [
            {"organization": String, "user_uid": String}
        ]
    }

    DELETE
    uid String

    :return:
    """
    req_method = request.method.upper()
    if req_method == "GET":
        uid = request.args.get("uid")
        if uid:
            result = db_workspace(app.db, uid=uid, user_uid=g.token["user_uid"])
        else:
            result = db_workspace(app.db, result=True, user_uid=g.token["user_uid"])
        if result:
            return jsonify(model_to_dict(result))
    elif req_method == "POST":
        data = request.get_json()
        workspace_uid=uuid1()

        # workspace exits
        if db_workspace(
                app.db,
                name=data["name"],
                user_uid=g.token["user_uid"],
                organization_uid=g.token["organization_uid"]):
            abort(403)
        # party exist
        for i in data["party_info"]["party_list"]:
            r = app.db.query(User).join(
                Organization, Organization.uid == User.organization_uid
            ).filter(
                User.uid == i["user_uid"], Organization.name == i["organization"]
            ).with_entities(
                Organization.uid
            ).first()
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
        return "ok"
    elif req_method == "PATCH":
        data = request.get_json()
        uid = data.get("uid")
        workspace_ = db_workspace(app.db, uid=uid, user_uid=g.token["user_uid"], is_creator=1)
        if workspace_:

            # org user is exist
            edit_org_list = set()
            temp_record = None
            r = None
            for i in data["party_list"]:
                r = app.db.query(Organization).join(
                    User, Organization.uid == User.organization_uid
                ).filter(
                    Organization.name == i["organization"], User.uid == i["user_uid"]
                ).with_entities(
                    Organization.uid,
                    User.uid
                ).first()
                if not r:
                    return jsonify({
                        "code": 400,
                        "message": "organization or user not exist!!!"
                    })
                edit_org_list.add(r)
            else:
                temp_record = app.db.query(Workspace).filter_by(uid=uid).first()
                temp_record = model_to_dict(temp_record)
                temp_record.pop("id")
                temp_record.pop("user_uid")
                temp_record.pop("organization_uid")
                temp_record.pop("is_creator")

            # now workspace party
            org_list = app.db.query(
                Workspace.organization_uid,
                Workspace.user_uid,
            ).filter_by(
                uid=uid,
                is_creator=0
            ).all()
            org_list = set(org_list)

            if bool(edit_org_list) and edit_org_list != org_list:
                # add
                for i in (edit_org_list - org_list):
                    app.db.add(Workspace(
                        **temp_record,
                        organization_uid=i[0],
                        user_uid=i[1],
                    ))
                # delete
                for i in (org_list - edit_org_list):
                    app.db.query(Workspace).filter_by(
                        uid=uid,
                        organization_uid=i[0],
                        user_uid=i[1],
                        is_creator=0
                    ).delete()
                app.db.commit()
                return jsonify({"code": 200})
        return jsonify({"code": 400})
    elif req_method == "DELETE":
        uid = request.args.get("uid")
        # is creator
        is_creator = db_workspace(
            app.db,
            uid=uid,
            user_uid=g.token["user_uid"],
            organization_uid=g.token["organization_uid"],
            is_creator=1
        )
        if is_creator:
            # workspace_dataSet
            app.db.query(WorkspaceDataset).filter_by(
                workspace_uid=uid
            ).delete()

            # workspace_list
            app.db.query(Workspace).filter_by(
                uid=uid
            ).delete()

            app.db.commit()
            return jsonify({"code": 200})
        return jsonify({"code": 400})


@register.route("/workspace/dataSet/", methods=["GET", "POST", "DELETE"])
@login_required
def workspace_dataSet():
    """
    GET:
        uid: String

    POST:
        data = {
            "workspace_uid": "",
            "dataSet_uid": ""
        }

    DELETE:
        data = {
            "workspace_uid": "",
            "dataSet_uid": ""
        }
    :return:
    """
    req_method = request.method.upper()
    if req_method == "GET":
        uid = request.args.get("uid")
        result = app.db.query(WorkspaceDataset).join(
            Workspace, Workspace.uid == WorkspaceDataset.workspace_uid
        ).filter(
            Workspace.uid == uid,
            Workspace.user_uid == g.token["user_uid"],
            Workspace.organization_uid == g.token["organization_uid"],
        ).with_entities(
            Workspace.uid,
            Workspace.name,
            WorkspaceDataset.user_uid,
            WorkspaceDataset.dataSet_name,
            # Workspace.user_uid,
        ).all()
        resp_data = list()
        for i in result:
            resp_data.append({
                "workspace_uid": i[0],
                "workspace_name": i[1],
                "the_upload": 1 if i[2] == g.token["user_uid"] else 0,
                "dataSet_name": i[3]
            })
        return jsonify({
            "code": 200,
            "data": resp_data
        })
    if req_method == "POST":
        data = request.get_json()

        workspace = db_workspace(
            app.db,
            uid=data["workspace_uid"],
            user_uid=g.token["user_uid"],
            organization_uid=g.token["organization_uid"]
        )

        dataSet = db_dataset(
            app.db,
            uid=data["dataSet_uid"],
            user_uid=g.token["user_uid"],
            organization_uid=g.token["organization_uid"],
        )

        if workspace and dataSet:
            if not db_workspace_dataset(
                    app.db,
                    workspace_uid=data["workspace_uid"],
                    dataSet_uid=data["dataSet_uid"]):
                app.db.add(WorkspaceDataset(
                    workspace_uid=data["workspace_uid"],
                    dataSet_uid=data["dataSet_uid"],
                    workspace_name=workspace.name,
                    dataSet_name=dataSet.name,
                    user_uid=g.token["user_uid"]
                ))
                app.db.commit()
                return jsonify({"code": 200})
    if req_method == "DELETE":
        data = request.get_json()

        result = app.db.query(WorkspaceDataset).filter_by(
            workspace_uid=data["workspace_uid"],
            dataSet_uid=data["dataSet_uid"],
            user_uid=g.token["user_uid"]
        ).delete()
        app.db.commit()
        if result:
            return jsonify({"code": 200})
    return jsonify({"code": 400})
