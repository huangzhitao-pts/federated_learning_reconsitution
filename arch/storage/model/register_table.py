from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, \
    String, Boolean,  DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from werkzeug.security import generate_password_hash, check_password_hash


Base = declarative_base()


class Organization(Base):
    __tablename__ = 'organization'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    uid = Column('uid', String(36), unique=True)
    name = Column('name', String(128))
    users = relationship('User', backref='organization')


class Permission:
    USER = 1
    ORG_ADMIN = 2
    SYSTEM_ADMIN = 3


class Role(Base):
    __tablename__ = 'roles'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(64), unique=True)
    default = Column('default', Boolean, default=False, index=True)
    permissions = Column('permissions', Integer)
    users = relationship('User', backref='role')

    @staticmethod
    def insert_roles(db):
        roles = {
            'USER': (Permission.USER, True),
            'ORG_ADMIN': (Permission.ORG_ADMIN, False),
            'SYSTEM_ADMIN': (Permission.SYSTEM_ADMIN, False)
        }

        for r in roles:
            role = db.query(Role).filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.add(role)
        db.commit()


class User(Base):
    __tablename__ = 'user'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    uid = Column('uid', String(36), unique=True)
    username = Column('username', String(128))
    password_hash = Column('password', String(128))
    organization_uid = Column(String(36), ForeignKey('organization.uid', ondelete='CASCADE'))
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Workspace(Base):
    __tablename__ = 'workspace'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    uid = Column('uid', String(36))
    name = Column('name', String(128), nullable=False, server_default="")
    description = Column('description', String(256), nullable=False, server_default="")
    user_uid = Column('user_uid', String(36), nullable=False, server_default="")
    organization_uid = Column('organization_uid', String(36), nullable=False, server_default="")
    is_creator = Column('is_creator', Integer, nullable=False, server_default="0")


class DataSet(Base):
    __tablename__ = 'dataSet'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    uid = Column('uid', String(36), unique=True)
    user_uid = Column('user_uid', String(36), nullable=False, server_default="")
    organization_uid = Column('organization_uid', String(36), nullable=False, server_default="")
    name = Column('name', String(128), nullable=False, server_default="")
    description = Column('description', String(256), nullable=False, server_default="")
    file_path = Column('file_path', String(256), nullable=False, server_default="")
    schema_fields = relationship("SchemaField", backref="dataSet")


class SchemaField(Base):
    __tablename__ = 'schemaField'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(128))
    chinese_name = Column('chinese_name', String(128), nullable=False, server_default="")
    explain = Column('explain', String(256), nullable=False, server_default="")
    type_ = Column('type_', String(128), nullable=False, server_default="Integer")
    distribute_type = Column('distribute_type', String(128), nullable=False, server_default="连续型")
    dataSet_uid = Column(String(36), ForeignKey("dataSet.uid", ondelete='CASCADE'))


class WorkspaceDataset(Base):
    __tablename__ = 'workspaceDataset'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    workspace_uid = Column('workspace_uid', String(128), nullable=False, server_default="")
    dataSet_uid = Column('dataSet_uid', String(128), nullable=False, server_default="")
    workspace_name = Column('workspace_name', String(128), nullable=False, server_default="")
    dataSet_name = Column('dataSet_name', String(128), nullable=False, server_default="")
    user_uid = Column('user_uid', String(36), nullable=False, server_default="")


class Job(Base):
    __tablename__ = 'Job'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    uid = Column('uid', String(36), primary_key=True)  # job_id
    user_uid = Column('user_uid', String(36))
    workspace_uid = Column('workspace_uid', String(36))
    name = Column('name', String(128))
    description = Column('description', String(256))
    creation_timestamp = Column('creation_timestamp', DateTime, default=datetime.utcnow)
    training_timestamp = Column('training_timestamp', DateTime, nullable=True)
    completion_timestamp = Column('completion_timestamp', DateTime, nullable=True)
    conf = Column('conf', Text)
    state = Column('state', Integer, default=0)
    job_type = Column('job_type', Integer, default=1)  # 1 for horizontal, 2 for vertical, 0 for all_job_type


if __name__ == '__main__':
    from uuid import uuid1
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session

    # engine = create_engine(
    #             "mysql+pymysql://root:111@192.168.89.155:3310/federated_learning?charset=utf8",
    #             echo=False,
    #             max_overflow=0,
    #             pool_size=20,
    #             pool_timeout=30,
    #             pool_recycle=3600
    # )
    # Session = sessionmaker(bind=engine)
    # db = scoped_session(Session)
    #
    # Role.insert_roles(db)
    #
    # point = Organization()
    # point.uid = uuid1()
    # point.name = "point"
    #
    # zhongyuan = Organization()
    # zhongyuan.uid = uuid1()
    # zhongyuan.name = "zhongyuan"
    #
    # tencent = Organization()
    # tencent.uid = uuid1()
    # tencent.name = "tencent"
    #
    # db.add(point)
    # db.add(zhongyuan)
    # db.add(tencent)
    #
    # db.add(User(
    #     uid=uuid1(),
    #     username="hzt",
    #     password="pbkdf2:sha256:150000$A4y5a3Pg$725e2cfc8c466c82751d5a68b5cafb19b6751f4dc36edd3c1ea8a0bf24e843a5",
    #     organization_uid=point.uid,
    #     role_id=2
    # ))
    # db.add(User(
    #     uid=uuid1(),
    #     username="zy",
    #     password="pbkdf2:sha256:150000$A4y5a3Pg$725e2cfc8c466c82751d5a68b5cafb19b6751f4dc36edd3c1ea8a0bf24e843a5",
    #     organization_uid=zhongyuan.uid,
    #     role_id=2
    # ))
    # db.add(User(
    #     uid=uuid1(),
    #     username="tx",
    #     password="pbkdf2:sha256:150000$A4y5a3Pg$725e2cfc8c466c82751d5a68b5cafb19b6751f4dc36edd3c1ea8a0bf24e843a5",
    #     organization_uid=tencent.uid,
    #     role_id=2
    # ))
    # db.commit()

    # print(generate_password_hash("123"))
    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)

