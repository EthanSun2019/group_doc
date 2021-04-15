import datetime

from itsdangerous import SignatureExpired, BadSignature

from mongoengine import *

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mongoengine.context_managers import switch_db

from werkzeug.security import generate_password_hash, check_password_hash

from controller.document_controller import host_controller

connect(alias="local", db='group_docs', host="127.0.0.1", port=27017)


# connect(alias="remote", db='group_docs', host=master_ip, port=27017, username="groupadmin", password="groupadmin123.")

# 提供一个带认证的数据库，或者认证的接口

class user_info(Document):
    meta = {
        'db_alias': 'local'
    }
    user_name = StringField(required=True, max_length=64)
    user_password = StringField(required=True, max_length=128)
    user_token = StringField(required=False, max_length=256)
    user_role = IntField(required=True)
    user_email = StringField(required=False)
    user_from = StringField(required=False)
    create_time = DateTimeField(required=True)
    update_time = DateTimeField(required=True)


class user_controller():
    SECRET_KEY = 'abcd7g6efghijklmm'

    # 生成token, 有效时间为600min
    def generate_auth_token(self, user_name):
        # 第一个参数是内部私钥
        # 第二个参数是有效期（秒）
        s = Serializer(self.SECRET_KEY, expires_in=36000)
        return s.dumps({'user_name': user_name})

    # 验证token
    def verify_auth_token(self, token):
        s = Serializer(self.SECRET_KEY)
        # token正确
        try:
            data = s.loads(token)
            return data
        # token过期
        except SignatureExpired:
            return None
        # token错误
        except BadSignature:
            return None

    # 检查用户是否存在
    def is_user_exists(self, user_name):
        with switch_db(user_info, 'local'):
            myuser = user_info.objects(user_name=user_name)
        if len(myuser) > 0:
            return True
        else:
            return False

    def check_local_user(self, user_name):
        with switch_db(user_info, 'local'):
            myuser = user_info.objects(user_name=user_name)
        if len(myuser) > 0:
            return True
        else:
            return False

    # 用户注册
    def register(self, user_name, user_password, user_email):
        # try:
        master_exists = self.is_user_exists(user_name)
        local_ip = host_controller().get_local_host_ip()
        print(local_ip)
        if master_exists == True:
            # print("注册失败,用户已存在")
            return {
                "result": {
                    "resultCode": "20000299",
                    "resultMessage": "用户注册失败,用户已存在"
                }
            }
        else:
            # if master_ip == "127.0.0.1":
            #     with switch_db(user_info, 'local'):
            #         new_user = user_info(
            #             user_name=user_name,
            #             user_password=generate_password_hash(user_password),
            #             user_token=self.generate_auth_token(user_name).decode("utf-8"),
            #             user_email=user_email,
            #             user_role=1,
            #             user_from=local_ip,
            #             create_time=datetime.datetime.now(),
            #             update_time=datetime.datetime.now()
            #         )
            #         print("local")
            #         new_user.save()
            #     return {
            #         "result": {
            #             "resultCode": "20000200",
            #             "resultMessage": "用户注册成功"
            #         }
            #     }
            # else:
            with switch_db(user_info, 'local'):
                new_user = user_info(
                    user_name=user_name,
                    user_password=generate_password_hash(user_password),
                    user_token=self.generate_auth_token(user_name).decode("utf-8"),
                    user_email=user_email,
                    user_role=1,
                    user_from=local_ip,
                    create_time=datetime.datetime.now(),
                    update_time=datetime.datetime.now()
                )
                print("local")
                new_user.save()
                # with switch_db(user_info, 'remote'):
                #     a_user = user_info(
                #         user_name=user_name,
                #         user_password=generate_password_hash(user_password),
                #         user_token=self.generate_auth_token(user_name).decode("utf-8"),
                #         user_role=1,
                #         user_from=local_ip,
                #         create_time=datetime.datetime.now(),
                #         update_time=datetime.datetime.now()
                #     )
                #     a_user.save()
                return {
                    "result": {
                        "resultCode": "20000200",
                        "resultMessage": "用户注册成功"
                    }
                }

    # 用户登录
    def login(self, user_name, user_password):
        with switch_db(user_info, 'local'):
            myuser = user_info.objects(user_name=user_name)
            if len(myuser) > 0:
                # print(myuser[0].user_password)
                bool_pass = check_password_hash(myuser[0].user_password, str(user_password))
                # print(bool_pass)
                if bool_pass == True:
                    result = {
                        "result": {"resultCode": "20000202", "resultMessage": "登录成功"},
                        "userInfo": {
                            "username": user_name,
                            "token": str(self.generate_auth_token(user_name).decode('utf-8'))
                        }}
                    myuser.update(user_token=self.generate_auth_token(user_name).decode('utf-8'))
                else:
                    result = {
                        "result": {"resultCode": "20000298", "resultMessage": "登录失败,密码错误"},
                        "userInfo": {
                            "username": "",
                            "token": None
                        }
                    }
            else:
                result = {
                    "result": {
                        "resultCode": "20000298",
                        "resultMessage": "登录失败,用户不存在"
                    },
                    "userInfo": {
                        "username": "",
                        "token": None
                    }
                }

        return result

    # 用户列表
    def local_user_info(self):
        connect(db='group_docs', host="127.0.0.1", port=27017, alias='local')
        myuser = user_info.objects()
        return myuser

    def get_user_token(self, user_name):
        connect(db='group_docs', host="127.0.0.1", port=27017, alias='local')
        myuser = user_info.objects(user_name=user_name)
        if len(myuser) > 0:
            return myuser[0].user_token
        else:
            return None

    def get_user_info(self, user_name):
        connect(db='group_docs', host="127.0.0.1", port=27017, alias='local')
        myuser = user_info.objects(user_name=user_name)
        if len(myuser) > 0:
            reuslt = {
                "user_name": myuser[0].user_name,
                "user_email": myuser[0].user_email,
                "user_from": myuser[0].user_from
            }
            return reuslt
        else:
            return None

    # 用户删除
    def user_info_delete(self):
        connect(db='group_docs', host="127.0.0.1", port=27017, alias='local')
        myuser = user_info.objects()
        myuser.delete()

    # 用户更新
    def user_info_update(self):
        pass

# h=user_controller().get_user_token("sunjiale")
# print(h)
