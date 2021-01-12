from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from werkzeug.security import generate_password_hash, check_password_hash


Base = declarative_base()


class Organization(Base):
    __tablename__ = 'organization'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    uid = Column('uid', String(128), unique=True)
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
    username = Column('username', String(128))
    password_hash = Column('password', String(128))
    organization_uid = Column(String(128), ForeignKey('organization.uid', ondelete='CASCADE'))
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
    uid = Column('uid', String(128))
    name = Column('name', String(128), nullable=False, server_default="")
    description = Column('description', String(256), nullable=False, server_default="")
    party_info = Column('party_info', Text)


class DataSet(Base):
    __tablename__ = 'dataSet'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    uid = Column('uid', String(128), unique=True)
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
    dataSet_uid = Column(String(128), ForeignKey("dataSet.uid", ondelete='CASCADE'))


class WorkspaceDataset(Base):
    __tablename__ = 'workspaceDataset'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    workspace_uid = Column('workspace_uid', String(128), nullable=False, server_default="")
    dataset_uid = Column('dataset_uid', String(128), nullable=False, server_default="")
    workspace_name = Column('workspace_name', String(128), nullable=False, server_default="")
    dataset_name = Column('dataset_name', String(128), nullable=False, server_default="")


if __name__ == '__main__':
    # from sqlalchemy import create_engine
    # from sqlalchemy.orm import sessionmaker, scoped_session
    #
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
    # roles = {
    #     'USER': (Permission.USER, True),
    #     'ORG_ADMIN': (
    #         Permission.ORG_ADMIN | Permission.USER, False),
    #     'SYSTEM_ADMIN': (
    #         Permission.SYSTEM_ADMIN | Permission.ORG_ADMIN | Permission.USER, False)
    # }
    #
    # for r in roles:
    #     role = db.query(Role).filter_by(name=r).first()
    #     print(role)
    # #     if role is None:
    # #         role = Role(name=r)
    # #     role.permissions = roles[r][0]
    # #     role.default = roles[r][1]
    # #     print("-------")
    # #     db.add(role)
    # # db.commit()
    # Role.insert_roles(db)

    # Base.metadata.create_all(engine)
    print(generate_password_hash("123"))
    # Base.metadata.drop_all(engine)
