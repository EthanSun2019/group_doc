import datetime
import uuid

import pymongo
import time

from gridfs import GridFS
from mongoengine import *
from mongoengine.context_managers import switch_db

connect(db='group_docs', host="127.0.0.1", port=27017, alias="local")


class host_info(Document):
    meta = {
        'db_alias': 'local'
    }
    ip = StringField(required=True, max_length=128)
    host_name = StringField(required=False, max_length=128)
    status = IntField(required=False)
    is_local = IntField(required=False)


class class_info(Document):
    meta = {
        'db_alias': 'local'
    }
    class_name = StringField(required=True, max_length=128)
    author = StringField(required=True, max_length=128)
    host = StringField(required=False)
    is_published = StringField(required=True)
    explain = StringField(required=True, max_length=256)
    create_time = DateTimeField(required=True)
    update_time = DateTimeField(required=True)


class document_info(Document):
    meta = {
        'db_alias': 'local'
    }
    doc_id = StringField(required=True)
    title = StringField(required=True, max_length=128)
    author = StringField(required=True, max_length=128)
    class_name = StringField(required=False, max_length=128)
    host = StringField(required=False, max_length=128)
    doc_type = StringField(required=False)
    page_view = IntField(required=False)
    comment_count = IntField(required=False)
    download = IntField(required=False)
    is_published = IntField(required=False)
    data = StringField(required=False)
    create_time = DateTimeField(required=True)
    update_time = DateTimeField(required=True)


class comment_info(Document):
    meta = {
        'db_alias': 'local'
    }
    comment_id = IntField(required=True)
    doc_id = StringField(required=True)
    user = StringField(required=False, max_length=128)
    comment = StringField(required=False)
    like_count = IntField(required=False, default=0)
    like_records = StringField(required=False)
    create_time = DateTimeField(required=True)
    update_time = DateTimeField(required=True)


class like_info(Document):
    meta = {
        'db_alias': 'local'
    }
    comment_id = IntField(required=True)
    user = StringField(required=False, max_length=128)
    is_like = IntField(required=False)


def set_c_type(c_type):
    def wrapper(func):
        def inner(*args, **kwargs):
            with switch_db(c_type, 'local'):
                ret = func(*args, **kwargs)  # 被装饰函数
                return ret

        return inner

    return wrapper


class host_controller():
    @set_c_type(host_info)
    def is_host_exists(self, ip):
        myuser = host_info.objects(ip=ip)
        if len(myuser) > 0:
            return True
        else:
            return False

    @set_c_type(host_info)
    def list_local_hosts(self):
        info = host_info.objects()
        return info

    @set_c_type(host_info)
    def get_local_host_ip(self):
        info = host_info.objects(is_local=1)
        return info[0].ip

    @set_c_type(host_info)
    def add_host_db(self, ip, host_name, status, is_local):
        is_exists = self.is_host_exists(ip)
        if is_exists == False:
            connect(db='group_docs', host="127.0.0.1", port=27017)
            info = host_info(
                ip=ip,
                host_name=host_name,
                status=status,
                is_local=is_local
            )
            info.save()
            result = {"code": "20000300", "message": "主机信息添加成功"}
            return result

        else:
            result = {"code": "20000399", "message": "主机信息添加失败,主机IP已存在"}
            return result


class document_controller():

    @set_c_type(class_info)
    def is_class_exists(self, class_name):
        myuser = class_info.objects(class_name=class_name)
        if len(myuser) > 0:
            return True
        else:
            return False

    @set_c_type(class_info)
    def list_local_class(self):
        info = class_info.objects()
        return info

    #获取个人的分类信息
    @set_c_type(class_info)
    def list_my_class(self,author):
        info = class_info.objects(author=author)
        return info

    @set_c_type(class_info)
    def list_public_class(self):
        info = class_info.objects(is_published='true')
        return info

    @set_c_type(class_info)
    def add_local_class(self, class_name, host, author, explain, is_published):
        try:
            is_exists = self.is_class_exists(class_name=class_name)
            if is_exists == False:
                # print(is_published)
                # host = host_info.objects(is_local=1)[0].ip
                new_class = class_info(
                    class_name=class_name,
                    author=author,
                    host=host,
                    explain=explain,
                    is_published=is_published,
                    create_time=datetime.datetime.now(),
                    update_time=datetime.datetime.now()
                )
                new_class.save()
                result = {"code": "20000500", "message": "文档分类添加成功"}
                return result
            else:
                result = {"code": "20000599", "message": "文档分类名称已存在"}
                return result

        except:
            result = {"code": "20000599", "message": "文档分类添加失败"}
            return result

    @set_c_type(class_info)
    def delete_local_class(self, class_name, host):
        is_exists = self.is_class_exists(class_name, host=host)
        if is_exists == True:
            my_class_list = class_info.objects(class_name=class_name, host=host)
            for my_c in my_class_list:
                my_c.delete()
            return {
                "code": "20000501", "message": "文档分类删除成功"
            }
        else:
            return {
                "code": "20000599", "message": "文档分类不存在"
            }

    @set_c_type(document_info)
    def add_local_document(self, title, author, class_name, host, is_published, data, doc_type):

        try:
            result = {}
            is_exists = len(document_info.objects(title=title, author=author))
            if title != None and data != None \
                    and title != "" and data != "" and is_exists == 0 and class_name != None and class_name != "":
                new_doc = document_info(
                    doc_id=author + str(int(time.time())),
                    title=title,
                    author=author,
                    class_name=class_name,
                    host=host,
                    data=data,
                    doc_type=doc_type,
                    is_published=is_published,
                    page_view=0,
                    comment_count=0,
                    download=0,
                    create_time=datetime.datetime.now(),
                    update_time=datetime.datetime.now()
                )
                new_doc.save()
                result = {"code": "20000400", "message": "文章添加成功"}
            else:
                result = {"code": "20000499", "message": "标题,内容,文档集不能为空,且标题不允许重复"}
            # return result

        except Exception as e:
            result = {"code": "20000499", "message": "文章添加失败,具体原因:" + e}
            # return result
        finally:
            return result

    @set_c_type(document_info)
    def filter_document_by_class_name(self, class_name, is_published):
        info = document_info.objects(is_published=is_published, class_name=class_name)
        return info

    @set_c_type(document_info)
    def filter_document_by_class_name_no_public(self, class_name, author):
        info = document_info.objects(class_name=class_name)
        result = []
        for my in info:
            if my["is_published"] == 1 or my["author"] == author:
                result.append(my)
        return result

    @set_c_type(document_info)
    def filter_document_by_docname(self, doc_name, author):
        info = document_info.objects()
        result = []
        for my in info:
            # 判断公用的或者作者为自己的文档
            if my["is_published"] == 1 or my["author"] == author:
                if str(doc_name).upper() in str(my["title"]).upper():
                    result.append(my)
        return result

    @set_c_type(document_info)
    def filter_document_by_docid(self, doc_id):
        info = document_info.objects(doc_id=doc_id)
        return info

    @set_c_type(document_info)
    def filter_local_documents(self, class_name):
        info = document_info.objects(class_name=class_name)
        return info

    @set_c_type(document_info)
    def page_view_add(self, doc_id):
        info = document_info.objects(doc_id=doc_id)
        if len(info) > 0:
            for my in info:
                old = my.page_view
                my.page_view = int(old) + 1
                my.save()

    @set_c_type(document_info)
    def download_add(self, doc_id):
        info = document_info.objects(doc_id=doc_id)
        if len(info) > 0:
            for my in info:
                old = my.download
                my.download = int(old) + 1
                my.save()


class gridfs_controller(object):
    def __init__(self):
        self.db = "group_docs"
        self.db_url = "mongodb://localhost:27017"

    def connect_db(self):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        return db

    # 上传文件
    def upLoadFile(self, file_id, file_name, class_name, host, author, is_published, file_type, file_data, remark,
                   url):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        # file_id = str(uuid.uuid1())
        filter_condition = {
            "file_id": file_id,
            "file_name": file_name,
            "class_name": class_name,
            # "file_path": file_path,
            # "url": "http://" + host + ":10018/files/download/" + file_id,
            "url": url,
            "host": host,
            "author": author,
            "file_type": file_type,
            "is_published": is_published,
            "download":0,
            "remark": remark
        }
        gridfs_col = GridFS(db, collection="file_info")
        query = {"file_name": "", "author": ""}
        query["file_name"] = file_name
        query["author"] = author
        if gridfs_col.exists(query):
            result = {
                "code": "20000699",
                "message": "文件已经存在"
            }
        else:
            try:
                # with open(file_path, 'rb') as file_r:
                # file_data = file_data
                gridfs_col.put(data=file_data, **filter_condition)
                result = {
                    "code": "20000600",
                    "message": "文件上传成功"}
            except Exception as e:
                result = {
                    "code": "20000699",
                    "message": "文件上传失败,原因:" + e
                }

        return result

    def downLoadFile(self, file_id):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        gridfs_col = GridFS(db, collection="file_info")
        query = {"file_id": ""}
        query["file_id"] = file_id
        if gridfs_col.exists(query) == False:
            file_data = None
        else:
            file_name = self.filter_single_grid_info(file_id=file_id)[0]["file_name"]
            print(file_name)
            file_data = gridfs_col.get_version(file_id=file_id, version=-1).read()
        return file_data, file_name

    def get_infos(self):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        coll = db["file_info.files"]
        all_list = coll.find()
        files = []
        if all_list.count() > 0:
            for file in all_list:
                files.append(
                    {
                        "file_id": file["file_id"],
                        "file_name": file["file_name"],
                        "class_name": file["class_name"],
                        "url": file["url"],
                        "host": file["host"],
                        "author": file["author"],
                        "file_type": file["file_type"],
                        "is_published": file["is_published"],
                        "md5": file["md5"],
                        "length": file["length"],
                        "download":file["download"],
                        "uploadDate": file["uploadDate"].strftime("%Y-%m-%d %H:%M:%S")

                    }
                )
        return files

    def filter_single_grid_info(self, file_id):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        coll = db["file_info.files"]
        query = {"file_id": ""}
        query["file_id"] = file_id
        file_info = coll.find(query)
        return file_info

    def filter_file_by_class_name(self, class_name, is_published):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        coll = db["file_info.files"]
        query = {"class_name": "", "is_published": ''}
        query["class_name"] = class_name
        query["is_published"] = is_published
        file_info = coll.find(query)
        return file_info

    # 获取公共的文档和私人可见的文档
    def filter_file_by_class_name_no_public(self, class_name, author):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        coll = db["file_info.files"]
        query = {"class_name": ""}
        query["class_name"] = class_name
        file_info = coll.find(query)
        result = []
        if file_info.count() > 0:
            for file in file_info:
                if file["is_published"] == "是" or file["author"] == author:
                    result.append(file)
        return result

    # 根据名称模糊搜索公共文档与可见的文档
    def filter_file_like_name(self, file_name, author):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        coll = db["file_info.files"]
        file_info = coll.find()
        result = []
        if int(file_info.count()) > 0:
            for file in file_info:
                if file["is_published"] == "是" or file["author"] == author:
                    if str(file_name).upper() in str(file["file_name"]).upper():
                        result.append(file)
        return result

    def get_public_infos(self):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        coll = db["file_info.files"]
        all_list = coll.find({"is_published": 1})
        files = []
        if all_list.count() > 0:
            for file in all_list:
                files.append(
                    {
                        "file_id": file["file_id"],
                        "file_name": file["file_name"],
                        "class_name": file["class_name"],
                        "url": file["url"],
                        "host": file["host"],
                        "author": file["author"],
                        "file_type": file["file_type"],
                        "is_published": file["is_published"],
                        "md5": file["md5"],
                        "length": file["length"],
                        "uploadDate": file["uploadDate"].strftime("%Y-%m-%d %H:%M:%S")

                    }
                )
        return files

    def public_infos_or_not(self, file_id, is_publish):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        coll = db["file_info.files"]
        coll.update_one(filter={"file_id": file_id}, update={"$set": {"is_published": is_publish}})

    def download_count(self, file_id):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        coll = db["file_info.files"]
        info = coll.find_one(filter={"file_id": file_id})
        download = int(info["download"]) + 1
        coll.update_one(filter={"file_id": file_id}, update={"$set": {"download": download}})


class comment_controller():
    @set_c_type(comment_info)
    def get_max_id(self):
        try:
            all_infos = comment_info.objects()
            if len(all_infos) > 0:
                max_id = 1
                for info in all_infos:
                    if max_id < info.comment_id:
                        max_id = info.comment_id
            else:
                max_id = 0
        except:
            max_id = 0
        finally:
            return max_id

    @set_c_type(like_info)
    def is_like_comment(self, user, comment_id):
        bool_like = 0
        try:
            info = like_info.objects(user=user, comment_id=comment_id)
            if len(info) > 0:
                bool_like = 1
        except:
            bool_like = 0
        finally:
            return bool_like

    @set_c_type(like_info)
    def add_like_comment(self, user, comment_id):
        info = like_info.objects(user=user, comment_id=comment_id)
        if len(info) > 0:
            for k in info:
                k.bool_like = 1
                k.save()
        else:
            new_info = like_info(
                user=user,
                comment_id=comment_id,
                is_like=1
            )
            new_info.save()

    @set_c_type(like_info)
    def minus_like_comment(self, user, comment_id):
        info = like_info.objects(user=user, comment_id=comment_id)
        if len(info) > 0:
            for k in info:
                k.delete()

    @set_c_type(comment_info)
    def add_comment(self, doc_id, user, comment):
        comment_id = self.get_max_id() + 1
        info = comment_info(
            comment_id=comment_id,
            doc_id=doc_id,
            user=user,
            comment=comment,
            create_time=datetime.datetime.now(),
            update_time=datetime.datetime.now(),
        )
        info.save()
        result = {"code": "20000800", "message": "评论成功"}
        return result

    @set_c_type(comment_info)
    def list_comments(self, doc_id, current_user):
        info = comment_info.objects(doc_id=doc_id)
        count_of_info = len(info)
        if count_of_info > 0:
            floor = 1
            result = []
            for k in info:
                bool_like = 0
                if current_user == "游客" or current_user == "" or current_user == None:
                    bool_like = 0
                else:
                    bool_like = self.is_like_comment(user=current_user, comment_id=k.comment_id)
                result.append(
                    {
                        "comment_id": k.comment_id,
                        "floor": floor,
                        "doc_id": k.doc_id,
                        "user": k.user,
                        "comment": k.comment,
                        "create_time": k.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "like_count": self.get_like_count(comment_id=k.comment_id),
                        "bool_like": bool_like

                    }
                )
                floor = floor + 1
        else:
            result = []
        return result

    @set_c_type(comment_info)
    def count_of_comments(self, doc_id):
        info = comment_info.objects(doc_id=doc_id)
        count_of_info = len(info)
        return count_of_info

    @set_c_type(comment_info)
    def like_action(self, comment_id, user):
        bool_like = self.is_like_comment(user=user, comment_id=comment_id)
        # print(bool_like)
        if bool_like == 0:
            info = comment_info.objects(comment_id=comment_id)
            if len(info) > 0:
                for m in info:
                    # print(m.like_count)
                    m.like_count = m.like_count + 1
                    m.save()
                    # print(m.like_count)
                self.add_like_comment(user=user, comment_id=comment_id)
                return {
                    "code": "20000801",
                    "message": "点赞成功"
                }
            else:
                return {
                    "code": "20000899",
                    "message": "评论不存在"
                }
        else:
            info = comment_info.objects(comment_id=comment_id)
            if len(info) > 0:
                for m in info:
                    m.like_count = m.like_count - 1
                    m.save()
                    # print(m.like_count)
                self.minus_like_comment(user=user, comment_id=comment_id)
                return {
                    "code": "20000802",
                    "message": "取消点赞成功"
                }
            else:
                return {
                    "code": "20000899",
                    "message": "评论不存在"
                }

    @set_c_type(like_info)
    def get_like_count(self, comment_id):
        info = like_info.objects(comment_id=comment_id)
        total = len(info)
        return total


# helper = gridfs_controller()
# helper.download_count("dd708064-5a0b-11eb-897d-5e434c47df09")
