from uuid import uuid1
import os
import json
from functools import partial
from flask import request, g, jsonify, views
from flask import current_app as app

from . import jobs
from arch.auth import login_required
from arch.storage.mysql.model import Workspace, WorkspaceDataset, DataSet, Job
from arch.storage.mysql.sql_result_to_dict import model_to_dict

from arch.job import align


def db_select_(model, db, result=None, **kwargs):
    resp = db.query(model).filter_by(**kwargs)
    return resp.all() if result else resp.first()


db_workspace = partial(db_select_, Workspace)
db_dataset = partial(db_select_, DataSet)
db_workspace_dataset = partial(db_select_, WorkspaceDataset)
db_job = partial(db_select_, Job)


# @jobs.route("/jobs/align/", methods=["GET", "POST", "DELETE"])
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
#                     "jobs": model_to_dict(job)
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


class JobState(object):
    UNKNOWN = 0
    DISABLED = 1
    TRAINING = 2
    FINISHED = 3
    FAILURE = 4
    PAUSED = 5
    PENDING = 6


class JobType(object):
    ALIGN = 0
    FEATURE_ENGINEERING = 1
    HORIZONTAL = 2
    VERTICAL = 3

    def get(self, item):
        item = item.upper()
        if hasattr(self, item):
            return getattr(self, item)


class Job(views.MethodView):
    methods = ["get", "post", "put", "patch", "delete"]
    decorators = (login_required,)
    JOB_TYPE = JobType()
    JOB_STATE = JobState()

    def get(self, job_type):
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
        job_type = self.JOB_TYPE.get(job_type)

        if db_workspace(app.db, uid=workspace_uid, user_uid=g.token["user_uid"]):
            if job_id:
                job = db_job(app.db, uid=job_id, job_type=job_type)
            else:
                job = db_job(app.db, result=True, workspace_uid=data["workspace_uid"], job_type=job_type)
            if job:
                resp["code"] = 200
                resp["data"] = model_to_dict(job)
        return jsonify(resp)

    def post(self, job_type):
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
            "description": String,conf
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
        job_type = self.JOB_TYPE.get(job_type)

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
                job_uid = str(uuid1())

                conf_dir = os.path.join(app.config["BASE_DIR_PATH"], "conf", job_uid)
                if not os.path.exists(conf_dir):
                    os.mkdir(conf_dir)
                with open(f"{conf_dir}/conf.json", "w", encoding="utf-8") as fp:
                    app.db.add(Job(
                        uid=job_uid,
                        user_uid=g.token["user_uid"],
                        workspace_uid=data["workspace_uid"],
                        name=data["name"],
                        description=data["description"],
                        conf_path=f"{conf_dir}/conf.json",
                        job_type=job_type,
                    ))
                    json.dump(data["conf"], fp)
                    app.db.commit()
                    resp["code"] = 200
        return jsonify(resp)

    def patch(self, job_type):
        """
        data = {
            "uid": String,
        }


        :param job:
        :return:
        """
        resp = {"code": 400}

        data = request.get_json()
        job_type = self.JOB_TYPE.get(job_type)

        # align
        if job_type == self.JOB_TYPE.ALIGN:
            # check job
            job = db_job(
                app.db,
                uid=data["uid"],
                user_uid=g.token["user_uid"],
                state=self.JOB_STATE.UNKNOWN,
                job_type=self.JOB_TYPE.ALIGN
            )
            print(job)
            if job:
                # start job
                job.state = self.JOB_STATE.TRAINING
                app.db.add(job)
                app.db.commit()

                result = align.delay(3, 4)
                print(result)
        return "ok"

    def delete(self, job_type):
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
        job_type = self.JOB_TYPE.get(job_type)

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

            conf_path = result.conf_path
            if os.path.exists(conf_path):
                os.remove(conf_path)

            app.db.delete(result)
            app.db.commit()
            resp["code"] = 200
        return jsonify(resp)


job_view = Job.as_view(name='Job')
jobs.add_url_rule("/job/<string:job_type>/", view_func=job_view, methods=["GET", "POST", "DELETE", "PATCH"])

# jobs.add_url_rule(
#     "/jobs/<string:uid>", view_func=job_view, methods=["DELETE", "PATCH"]
# )
