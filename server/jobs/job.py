from uuid import uuid1
from datetime import datetime
import os
import json
from functools import partial

from rq.command import send_stop_job_command

from flask import request, g, jsonify, views
from flask import current_app as app

from . import jobs
from arch.auth import login_required
from arch.storage.mysql.model import Workspace, WorkspaceDataset, DataSet, Job
from arch.storage.mysql.sql_result_to_dict import model_to_dict

from arch.job import align
from arch.job.job_state import JobState
from arch.job.job_type import JobType


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


class JobAction(object):
    START = 0
    PAUSE = 1


class Jobs(views.MethodView):
    methods = ["get", "post", "put", "patch", "delete"]
    decorators = (login_required,)
    JOB_TYPE = JobType
    JOB_STATE = JobState
    JOB_ACTION = JobAction

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
                job = app.redis.hgetall(job_id)
                if not job:
                    job = db_job(app.db, uid=job_id, job_type=job_type)
                    job = model_to_dict(job)
                    app.redis.hmset(job_id, job)
            else:
                job = db_job(app.db, result=True, workspace_uid=data["workspace_uid"], job_type=job_type)
                job = model_to_dict(job)
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
                    {"uid": "", "field": ""}
                ]
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
        print(is_operability)
        print(job_type)
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
                    job_ = Job(
                        uid=job_uid,
                        user_uid=g.token["user_uid"],
                        workspace_uid=data["workspace_uid"],
                        name=data["name"],
                        description=data["description"],
                        conf_path=f"{conf_dir}/conf.json",
                        state=self.JOB_STATE.DISABLED,
                        job_type=job_type
                    )
                    app.db.add(job_)
                    json.dump(data["conf"], fp)
                    app.db.commit()
                    resp["code"] = 200
        return jsonify(resp)

    def patch(self, job_type):
        """
        data = {
            "job_uid": String,
            "action": # start | pause
        }
        :param job:
        :return:
        """
        resp = {"code": 400}

        data = request.get_json()

        # job type
        #assert hasattr(self.JOB_TYPE, f"{job_type}_job")

        # check job
        job = db_job(
            app.db,
            uid=data["job_uid"],
            user_uid=g.token["user_uid"],
            # state=self.JOB_STATE.DISABLED,
            job_type=self.JOB_TYPE.ALIGN
        )
        print(job)
        if job:
            action = data["action"]
            job_state = job.state
            if action == "start" and job_state == self.JOB_STATE.DISABLED:
                # update db job status
                job.state = self.JOB_STATE.STARTED
                job.training_timestamp = datetime.utcnow()
                app.db.add(job)
                # update redis job status
                # start job
                # job_type.delay(job.uid)
                #getattr(self.JOB_TYPE, f"{job_type}_job")(job_id=job.uid)
                align.delay(job.uid)
            elif action == "pause" and job_state == self.JOB_STATE.STARTED:
                job.state = self.JOB_STATE.PAUSED
                send_stop_job_command(app.redis, data["job_uid"])

            # update redis job status
            mapping_data = {k: v for k, v in vars(job).items() if not k.startswith("_")}
            app.db.commit()
            mapping_data["creation_timestamp"] = mapping_data["creation_timestamp"].timestamp()
            mapping_data["completion_timestamp"] = mapping_data["completion_timestamp"].timestamp()
            mapping_data["training_timestamp"] = mapping_data["training_timestamp"].timestamp()

            app.redis.hmset(data["job_uid"], mapping_data)
            # app.redis.hset(data["job_uid"], "")
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

        job = db_job(
            app.db,
            workspace_uid=data["workspace_uid"],
            uid=data["job_uid"],
            user_uid=g.token["user_uid"],
            job_type=job_type
        )
        if job:
            if job.state == self.JOB_STATE.STARTED:
                send_stop_job_command(app.redis, data["job_uid"])
                app.redis.delete(data["job_uid"])
                app.redis.delete(f"rq:job:{data['job_uid']}")

            model_url = job.model_url
            if os.path.exists(model_url):
                os.remove(model_url)

            conf_path = job.conf_path
            if os.path.exists(conf_path):
                os.remove(conf_path)

            app.db.delete(job)
            app.db.commit()
            resp["code"] = 200
        return jsonify(resp)


job_view = Jobs.as_view(name='Job')
jobs.add_url_rule("/job/<string:job_type>/", view_func=job_view, methods=["GET", "POST", "DELETE", "PATCH"])

# jobs.add_url_rule(
#     "/jobs/<string:uid>", view_func=job_view, methods=["DELETE", "PATCH"]
# )
