from uuid import uuid1
import os
import time
from flask import request, g, abort, jsonify
from flask import current_app as app

import pandas as pd
from werkzeug.utils import secure_filename

from . import register
from arch.auth import login_required
from arch.storage.model.register_table import SchemaField, DataSet, WorkspaceDataset
from arch.storage.sql_result_to_dict import model_to_dict


@register.route("/dataSet/", methods=["GET", "POST", "PATCH", "DELETE"])
@login_required
def dataSet():
    """
    GET: look over dataSet info


    POST： upload dataSet
    data = {
        "name": String,
        "description": String,
        "file": file obj
    }

    PATCH
    data = {
        "uid": String,
        "fields": [
            {"field": ""}
        ]
    }

    DELETE
    :return:
    """
    req_method = request.method.upper()
    if req_method == "GET":
        uid = request.args.get("uid")
        if uid:
            result = app.db.query(SchemaField).join(
                DataSet, DataSet.uid == SchemaField.dataSet_uid
            ).filter(
                DataSet.uid == uid,
                DataSet.user_uid == g.token["user_uid"],
            ).all()
        else:
            result = app.db.query(DataSet).filter_by(
                user_uid=g.token["user_uid"]
            ).all()
        if result:
            return jsonify({
                "code": 200,
                "data": model_to_dict(result)
            })
        else:
            return jsonify({
                "code": 400,
                "data": ""
            })
    elif req_method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        file_obj = request.files.get("file")

        files_dir = os.path.join(app.config.get("BASE_DIR_PATH"), "files")
        today_file_path = os.path.join(files_dir, time.strftime("%Y%m%d", time.gmtime()))
        if not os.path.exists(today_file_path):
            os.mkdir(today_file_path)

        # file is exist
        file_path = os.path.join(today_file_path, secure_filename(file_obj.filename))
        if os.path.exists(file_path) or file_in_dir(
                os.path.join(app.config.get("BASE_DIR_PATH"), ""), secure_filename(file_obj.filename)):
            return jsonify({
                "code": 400,
                "message": "File is exists"
            })
        else:
            # save file to disk
            file_obj.save(file_path)

            # read dataset field save to db
            df = pd.read_csv(file_path)

            dataSet_uid = uuid1()
            for c in df.columns:
                type_ = str(df[c].dtype)
                if type_ == "Object":
                    distribute_type = "String"
                    app.db.add(
                        SchemaField(name=c, type_=str(df[c].dtype), dataSet_uid=dataSet_uid, distribute_type=distribute_type))
                else:
                    app.db.add(
                        SchemaField(name=c, type_=str(df[c].dtype), dataSet_uid=dataSet_uid))

            # save dataset info to db
            app.db.add(DataSet(
                uid=dataSet_uid,
                name=name,
                description=description,
                user_uid=g.token["user_uid"],
                organization_uid=g.token["organization_uid"],
                file_path=file_path
            ))
            app.db.commit()
            return jsonify({
                "code": 200,
                "message": "Succeed !!!"
            })
    elif req_method == "PATCH":
        data = request.get_json()

        # permission
        if app.db.query(DataSet).filter_by(
            uid=data.get("uid"),
            user_uid=g.token["user_uid"]
        ).first():
            for f in data["fields"]:
                app.db.query(SchemaField).filter_by(
                    id=f.pop("id"),
                    dataSet_uid=data.get("uid")
                ).update(f)
            app.db.commit()
            return jsonify({"code": 200})
        return jsonify({"code": 400})
    elif req_method == "DELETE":
        uid = request.args.get("uid")

        # has or permission
        dataSet = app.db.query(DataSet).filter_by(
            uid=uid,
            user_uid=g.token["user_uid"]
        ).first()
        if dataSet:
            is_use = app.db.query(WorkspaceDataset).filter_by(
                dataset_uid=uid
            ).first()
            if not is_use:
                # db delete
                app.db.query(DataSet).filter_by(
                    uid=uid,
                    user_uid=g.token["user_uid"]
                ).delete()
                app.db.commit()

                # disk delete
                os.remove(dataSet.file_path)
                return jsonify({"code": 200})
        return jsonify({"code": 400})


def db_select(db, model, result=None, **kwargs):
    resp = db.query(model).filter_by(**kwargs).all()
    return resp if result else bool(resp)


def file_in_dir(dir_path, filename):
    assert os.path.exists(dir_path)

    for p in os.listdir(dir_path):
        dir_path = os.path.join(dir_path, p).replace("\\", "/")
        if not os.path.isdir(dir_path):
            if p == filename:
                return True
            return None
        return file_in_dir(dir_path, filename)