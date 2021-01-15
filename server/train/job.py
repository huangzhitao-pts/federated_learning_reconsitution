from uuid import uuid1
import os
import json
from functools import partial
from flask import request, g, jsonify, views
from flask import current_app as app

from . import train
from arch.auth import login_required
from arch.storage.model.register_table import Workspace, WorkspaceDataset, DataSet, Job
from arch.storage.sql_result_to_dict import model_to_dict


def db_select_(model, db, result=None, **kwargs):
    resp = db.query(model).filter_by(**kwargs)
    return resp.all() if result else resp.first()


db_workspace = partial(db_select_, Workspace)
db_dataset = partial(db_select_, DataSet)
db_workspace_dataset = partial(db_select_, WorkspaceDataset)
db_job = partial(db_select_, Job)


# @train.route("/train/align/", methods=["GET", "POST", "DELETE"])
# @login_required
# def align_job():
#     """
#     GET：
#     data = {
#         "workspace_uid": String
#         "job_id": None or String
#     }
# 
#     POST:
# 
#     data = {
#         "workspace_uid": String,
#         "name": String,
#         "description": String,
#         "conf": {
#             "dataSet": [
#                 {"organization": "dataSet"}
#             ]
#         },
#     }
# 
#     DELETE:
#     data = {
#         "workspace_uid": String,
#         "job_uid": String,
#     }
#     :return:
#     """
#     req_method = request.method.upper()
#     if req_method == "GET":
#         data = request.get_json()
# 
#         workspace_uid=data["workspace_uid"]
#         job_id=data.get("job_uid")
# 
#         if db_workspace(app.db, uid=workspace_uid, user_uid=g.token["user_uid"]):
#             if job_id:
#                 job = db_job(app.db, uid=job_id)
#             else:
#                 job = db_job(app.db, result=True, workspace_uid=data["workspace_uid"])
#             if job:
#                 return jsonify({
#                     "code": 200,
#                     "train": model_to_dict(job)
#                 })
# 
#     if req_method == "POST":
#         data = request.get_json()
#         is_operability = db_workspace(
#             app.db,
#             uid=data["workspace_uid"],
#             user_uid=g.token["user_uid"]
#         )
#         if is_operability:
#             job_ = db_job(
#                 app.db,
#                 user_uid=g.token["user_uid"],
#                 workspace_uid=data["workspace_uid"],
#                 name=data["name"],
#             )
#             if not job_:
# 
#                 app.db.add(Job(
#                     uid=uuid1(),
#                     user_uid=g.token["user_uid"],
#                     workspace_uid=data["workspace_uid"],
#                     name=data["name"],
#                     description=data["description"],
#                     conf=json.dumps(data["conf"]),
#                     job_type=0,
#                 ))
#                 app.db.commit()
#                 return jsonify({"code": 200})
# 
#     if req_method == "DELETE":
#         data = request.get_json()
# 
#         result = db_job(
#             app.db,
#             workspace_uid=data["workspace_uid"],
#             uid=data["job_uid"],
#             user_uid=g.token["user_uid"],
#             job_type=0
#         )
#         if result:
#             model_url = result.model_url
#             if os.path.exists(model_url):
#                 os.remove(model_url)
#             app.db.delete(result)
#             app.db.commit()
#             return jsonify({"code": 200})
# 
#     return jsonify({"code": 400})


class Jobs(views.MethodView):
    methods = ["get", "post", "put", "patch", "delete"]
    decorators = (login_required,)
    JOB_TYPE = {
        "align": 0,
        "feature_engineering": 1,
        "horizontal": 2,
        "vertical": 3,
    }

    def get(self, job):
        """
        data = {
            "workspace_uid": String
            "job_id": None or String
        }
        :param job:
        :return:
        """
        resp = {"code": 400}

        data = request.get_json()

        workspace_uid = data["workspace_uid"]
        job_id = data.get("job_uid")
        job_type = self.JOB_TYPE.get(job)

        if db_workspace(app.db, uid=workspace_uid, user_uid=g.token["user_uid"]):
            if job_id:
                job = db_job(app.db, uid=job_id, job_type=job_type)
            else:
                job = db_job(app.db, result=True, workspace_uid=data["workspace_uid"], job_type=job_type)
            if job:
                resp["code"] = 200
                resp["data"] = model_to_dict(job)
        return jsonify(resp)

    def post(self, job):
        """
        align:
        data = {
            "workspace_uid": String,
            "name": String,
            "description": String,
            "conf": {
                "dataSet": [
                    {"organization": "dataSet"}
                ]
            },
        }


        feature_engineering:
        data = {
            "workspace_uid": String,
            "name": String,
            "description": String,
            "conf": {
                "align_dataSet": {"name": String, "uid": String},
                "param": dict
            },
        }

        horizontal:
        data = {
            "workspace_uid": String,
            "name": String,
            "description": String,
            "conf": {
                "dataSet": [
                    {"name": String, "uid": String},
                ],
                "target_dataSet": {"name": String, "uid": String},
                "epoch": String,
                "algorithm": {
                    "type": "",
                    "name": "",
                    "param": {}
                }
            }
        }

        vertical:
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

        :param job:
        :return:
        """
        resp = {"code": 400}

        data = request.get_json()
        job_type = self.JOB_TYPE.get(job)

        is_operability = db_workspace(
            app.db,
            uid=data["workspace_uid"],
            user_uid=g.token["user_uid"]
        )
        if is_operability:
            job_ = db_job(
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
                    job_type=job_type,
                ))
                app.db.commit()
                resp["code"] = 200
        return jsonify(resp)

    def patch(self, job):
        pass

    def delete(self, job):
        """
        data = {
            "workspace_uid": String,
            "job_uid": String,
        }
        :param job:
        :return:
        """
        resp = {"code": 400}

        data = request.get_json()
        job_type = self.JOB_TYPE.get(job)

        result = db_job(
            app.db,
            workspace_uid=data["workspace_uid"],
            uid=data["job_uid"],
            user_uid=g.token["user_uid"],
            job_type=job_type
        )
        if result:
            model_url = result.model_url
            if os.path.exists(model_url):
                os.remove(model_url)
            app.db.delete(result)
            app.db.commit()
            resp["code"] = 200
        return jsonify(resp)


job_view = Jobs.as_view(name='Jobs')
train.add_url_rule("/train/<string:job>/", view_func=job_view, methods=["GET", "POST", "DELETE", "PATCH"])

# train.add_url_rule(
#     "/train/<string:uid>", view_func=job_view, methods=["DELETE", "PATCH"]
# )
