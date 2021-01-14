# from uuid import uuid1
# from functools import partial
# from flask import request, g, abort, jsonify
# from flask import current_app as app
#
# from . import train
# from arch.auth import login_required
# from arch.storage.model.register_table import Workspace, Organization, \
#     User, WorkspaceDataset, DataSet
# from arch.storage.sql_result_to_dict import model_to_dict
#
#
# def db_select_(db, model, result=None, **kwargs):
#     resp = db.query(model).filter_by(**kwargs).all()
#     return resp.all() if result else resp.first()
#
#
# db_select = partial(db_select_, app.db)
#
#
# @train.route("/train/align/")
# def align_job():
#     """
#     GET：
#
#     POST:
#
#     data = {
#         "workspace_uid": String,
#         "name": String,
#         "description": String,
#         "conf": {},
#         "job_type": Integer
#     }
#
#
#     :return:
#     """
#     req_method = request.method.upper()
#     if req_method == "GET":
#         pass
#
#     if req_method == "POST":
#         data = request.get_json()
#
#         is_operability = db_select()
#
#
#     pass
#
#
