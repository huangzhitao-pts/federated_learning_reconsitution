from uuid import uuid1
import os
import json
from functools import partial
from flask import request, g, jsonify
from flask import current_app as app

from . import train
from arch.auth import login_required
from arch.storage.mysql.model import Workspace, WorkspaceDataset, DataSet, Job
from arch.storage.mysql.sql_result_to_dict import model_to_dict


def db_select_(model, db, result=None, **kwargs):
    resp = db.query(model).filter_by(**kwargs)
    return resp.all() if result else resp.first()


db_workspace = partial(db_select_, Workspace)
db_dataset = partial(db_select_, DataSet)
db_workspace_dataset = partial(db_select_, WorkspaceDataset)
db_Job = partial(db_select_, Job)


@train.route("/jobs/horizontal/", methods=["GET", "POST", "DELETE"])
@login_required
def horizontal():
    """
    GET：
    data = {
        "workspace_uid": String
        "job_id": None or String
    }

    POST:

    data = {
        "workspace_uid": String,
        "name": String,
        "description": String,
        "conf": {
            "dataSet": [
                {"name": String, "uid": String},
            ],
            "target_dataSet": {"name": String, "uid": String, "label": String},
            "epoch": String,
            "algorithm": {
                "type": "",
                "name": "",
                "param": {}
            }
        }
    }

    DELETE:
    data = {
        "workspace_uid": String,
        "job_uid": String,
    }
    :return:
    """
    req_method = request.method.upper()
    if req_method == "GET":
        data = request.get_json()

        workspace_uid=data["workspace_uid"]
        job_id=data.get("job_uid")

        if db_workspace(app.db, uid=workspace_uid, user_uid=g.token["user_uid"]):
            if job_id:
                job = db_Job(app.db, uid=job_id, job_type=2)
            else:
                job = db_Job(app.db, result=True, workspace_uid=data["workspace_uid"], job_type=2)
            if job:
                return jsonify({
                    "code": 200,
                    "jobs": model_to_dict(job)
                })

    if req_method == "POST":
        data = request.get_json()
        is_operability = db_workspace(
            app.db,
            uid=data["workspace_uid"],
            user_uid=g.token["user_uid"]
        )
        if is_operability:
            job_ = db_Job(
                app.db,
                name=data["name"],
                workspace_uid=data["workspace_uid"],
            )
            if not job_:
                app.db.add(Job(
                    uid=uuid1(),
                    user_uid=g.token["user_uid"],
                    workspace_uid=data["workspace_uid"],
                    name=data["name"],
                    description=data["description"],
                    conf=json.dumps(data["conf"]),
                    job_type=2,
                ))
                app.db.commit()
                return jsonify({"code": 200})

    if req_method == "DELETE":
        data = request.get_json()

        result = db_Job(
            app.db,
            workspace_uid=data["workspace_uid"],
            uid=data["job_uid"],
            user_uid=g.token["user_uid"],
            job_type=2
        )
        if result:
            model_url = result.model_url
            if os.path.exists(model_url):
                os.remove(model_url)
            app.db.delete(result)
            app.db.commit()
            return jsonify({"code": 200})

    return jsonify({"code": 400})
