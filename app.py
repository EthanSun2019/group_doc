import json
import math
from functools import wraps
from urllib.parse import quote

from flask import Flask, jsonify, request, Response, abort

from controller import user_controller, document_controller

from utils import sdn_helper

import uuid

app = Flask(__name__)


def init_host_info():
    helper = document_controller.host_controller()
    host_info = helper.list_local_hosts()
    if len(host_info) == 0:
        local_ip = sdn_helper.get_local_ip()
        local_name = sdn_helper.get_host_name()
        helper.add_host_db(ip=local_ip, host_name=local_name, status=1, is_local=1)
        return local_ip
    else:
        self_host = helper.get_local_host_ip()
        return self_host


current_host = init_host_info()


# print(current_host)


def check_user_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_name = request.cookies.get("user_name")
        # print(user_name)
        token = request.cookies.get("token")
        if user_name == "游客" or user_name == None:
            helper = user_controller.user_controller()
            # real_token = helper.get_user_token(user_name=user_name)
            # if real_token == token:
            ret = func(*args, **kwargs)  # 被装饰函数
            return ret
        else:
            helper = user_controller.user_controller()
            real_token = helper.get_user_token(user_name=user_name)
            if real_token == token:
                ret = func(*args, **kwargs)  # 被装饰函数
                return ret
            else:
                return jsonify(
                    {
                        "code": "20000799",
                        "message": "access failed , token or username is not right."
                    }
                )
        # else:
        #     return jsonify(
        #         {
        #             "code": "20000799",
        #             "message": "access failed , no login in"
        #         }
        #     )

    return wrapper


def must_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_name = request.cookies.get("user_name")
        print(user_name)
        token = request.cookies.get("token")
        print(token)
        if user_name != None or token != None:
            helper = user_controller.user_controller()
            real_token = helper.get_user_token(user_name=user_name)
            if real_token == token:
                ret = func(*args, **kwargs)  # 被装饰函数
                return ret
            else:
                return jsonify(
                    {
                        "code": "20000799",
                        "message": "access failed , token or username is not right."
                    }
                )
        else:
            return jsonify(
                {
                    "code": "20000799",
                    "message": "access failed , no login in"
                }
            )

    return wrapper


def page_view_add(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        doc_id = str(request.args.get("doc_id"))
        helper = document_controller.document_controller()
        helper.page_view_add(doc_id)
        ret = func(*args, **kwargs)  # 被装饰函数
        return ret

    return wrapper


def get_public_classes(offset, page_index):
    helper = document_controller.document_controller()
    class_info = helper.list_public_class()
    result = []
    count_class = len(class_info)
    if len(class_info) == 0:
        result = []
    else:
        begin_index = int(offset) * (int(page_index) - 1)
        end_index = int(offset) * (int(page_index))
        finale_list = class_info[begin_index:end_index]
        # print(finale_list)
        if len(finale_list) > 0:
            for info in finale_list:
                result.append({
                    "class_name": info.class_name,
                    "author": info.author,
                    "host": info.host,
                    "explain": info.explain,
                    "is_published": info.is_published,
                    "create_time": info.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "update_time": info.update_time.strftime("%Y-%m-%d %H:%M:%S")
                })
    return {
        "result": result,
        "total": count_class
    }


def get_all_classes(offset, page_index):
    helper = document_controller.document_controller()
    if request.method == "GET":
        class_info = helper.list_local_class()
        result = []
        count_result = len(class_info)
        if count_result == 0:
            result = []
        else:
            begin_index = int(offset) * (int(page_index) - 1)
            end_index = int(offset) * (int(page_index))
            finale_list = class_info[begin_index:end_index]
            for info in finale_list:
                result.append({
                    "class_name": info.class_name,
                    "author": info.author,
                    "host": info.host,
                    "update_time": info.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_published": info.is_published
                })
        return {
            "result": result,
            "total": count_result
        }

def get_my_classes(offset, page_index,user_name):
    helper = document_controller.document_controller()
    if request.method == "GET":
        class_info = helper.list_my_class(user_name)
        result = []
        count_result = len(class_info)
        if count_result == 0:
            result = []
        else:
            begin_index = int(offset) * (int(page_index) - 1)
            end_index = int(offset) * (int(page_index))
            finale_list = class_info[begin_index:end_index]
            for info in finale_list:
                result.append({
                    "class_name": info.class_name,
                    "author": info.author,
                    "host": info.host,
                    "update_time": info.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_published": info.is_published
                })
        return {
            "result": result,
            "total": count_result
        }

def get_documents(offset, page_index, class_name, is_published):
    helper = document_controller.document_controller()
    grid_helper = document_controller.gridfs_controller()
    comment_helper = document_controller.comment_controller()
    if request.method == "GET":
        document_info = helper.filter_document_by_class_name(class_name=class_name, is_published=is_published)
        if is_published == 1:
            file_is_published = "是"
        else:
            file_is_published = "否"
        file_infos = grid_helper.filter_file_by_class_name(class_name=class_name, is_published=file_is_published)
        result = []
        count_of_files = file_infos.count()
        print(count_of_files)
        count_of_documents = len(document_info)
        print(count_of_documents)
        if count_of_documents > 0:
            for info in document_info:
                comment_count = comment_helper.count_of_comments(doc_id=info["doc_id"])
                pub = ""
                doc_type = ""
                if info["is_published"] == 1:
                    pub = "是"
                else:
                    pub = "否"
                print(info["doc_type"])
                if info["doc_type"] == "1":
                    doc_type = "在线文档"
                result.append({
                    "doc_id": info["doc_id"],
                    "title": info["title"],
                    "author": info["author"],
                    "host": info["host"],
                    "class_name": info["class_name"],
                    "doc_type": doc_type,
                    "is_published": pub,
                    "comment_count": comment_count,
                    "page_view": info["page_view"],
                    "download": info["download"],
                    "data": info["data"],
                    "update_time": info["update_time"].strftime("%Y-%m-%d %H:%M:%S")
                })
        if count_of_files > 0:
            for info in file_infos:
                comment_count = comment_helper.count_of_comments(doc_id=info["file_id"])
                result.append({
                    "doc_id": info["file_id"],
                    "title": info["file_name"],
                    "author": info["author"],
                    "host": info["url"],
                    "class_name": info["class_name"],
                    "doc_type": info["file_type"],
                    "is_published": info["is_published"],
                    "comment_count": comment_count,
                    "page_view": 0,
                    "download": info["download"],
                    "data": info['remark'],
                    "update_time": info["uploadDate"].strftime("%Y-%m-%d %H:%M:%S")
                })
        all_count = count_of_files + count_of_documents
        begin_index = int(offset) * (int(page_index) - 1)
        end_index = int(offset) * (int(page_index))
        final_result = result[begin_index:end_index]
        return {
            "result": final_result,
            "total": all_count
        }


def filter_document_by_class_name_no_public(offset, page_index, class_name, author):
    helper = document_controller.document_controller()
    grid_helper = document_controller.gridfs_controller()
    comment_helper = document_controller.comment_controller()
    if request.method == "GET":
        document_info = helper.filter_document_by_class_name_no_public(class_name=class_name, author=author)
        file_infos = grid_helper.filter_file_by_class_name_no_public(class_name=class_name, author=author)
        result = []
        count_of_files = len(file_infos)
        print(count_of_files)
        count_of_documents = len(document_info)
        print(count_of_documents)
        if count_of_documents > 0:
            for info in document_info:
                comment_count = comment_helper.count_of_comments(doc_id=info["doc_id"])
                pub = ""
                doc_type = ""
                if info["is_published"] == 1:
                    pub = "是"
                else:
                    pub = "否"
                print(info["doc_type"])
                if info["doc_type"] == "1":
                    doc_type = "在线文档"
                result.append({
                    "doc_id": info["doc_id"],
                    "title": info["title"],
                    "author": info["author"],
                    "host": info["host"],
                    "class_name": info["class_name"],
                    "doc_type": doc_type,
                    "is_published": pub,
                    "comment_count": comment_count,
                    "page_view": info["page_view"],
                    "download": info["download"],
                    "data": info["data"],
                    "update_time": info["update_time"].strftime("%Y-%m-%d %H:%M:%S")
                })
        if count_of_files > 0:
            for info in file_infos:
                comment_count = comment_helper.count_of_comments(doc_id=info["file_id"])
                result.append({
                    "doc_id": info["file_id"],
                    "title": info["file_name"],
                    "author": info["author"],
                    "host": info["url"],
                    "class_name": info["class_name"],
                    "doc_type": info["file_type"],
                    "is_published": info["is_published"],
                    "comment_count": comment_count,
                    "page_view": 0,
                    "download": info["download"],
                    "data": info['remark'],
                    "update_time": info["uploadDate"].strftime("%Y-%m-%d %H:%M:%S")
                })
        all_count = count_of_files + count_of_documents
        begin_index = int(offset) * (int(page_index) - 1)
        end_index = int(offset) * (int(page_index))
        final_result = result[begin_index:end_index]
        return {
            "result": final_result,
            "total": all_count
        }


def filter_document_by_name(offset, page_index, doc_name, author):
    helper = document_controller.document_controller()
    grid_helper = document_controller.gridfs_controller()
    comment_helper = document_controller.comment_controller()
    if request.method == "GET":
        document_info = helper.filter_document_by_docname(doc_name=doc_name, author=author)
        file_infos = grid_helper.filter_file_like_name(file_name=doc_name, author=author)
        result = []
        count_of_files = len(file_infos)
        print(count_of_files)
        count_of_documents = len(document_info)
        print(count_of_documents)
        if count_of_documents > 0:
            for info in document_info:
                comment_count = comment_helper.count_of_comments(doc_id=info["doc_id"])
                pub = ""
                doc_type = ""
                if info["is_published"] == 1:
                    pub = "是"
                else:
                    pub = "否"
                if info["doc_type"] == "1":
                    doc_type = "在线文档"
                result.append({
                    "doc_id": info["doc_id"],
                    "title": info["title"],
                    "author": info["author"],
                    "host": info["host"],
                    "class_name": info["class_name"],
                    "doc_type": doc_type,
                    "is_published": pub,
                    "comment_count": comment_count,
                    "page_view": info["page_view"],
                    "download": info["download"],
                    "data": info["data"],
                    "update_time": info["update_time"].strftime("%Y-%m-%d %H:%M:%S")
                })
        if count_of_files > 0:
            for info in file_infos:
                comment_count = comment_helper.count_of_comments(doc_id=info["file_id"])
                result.append({
                    "doc_id": info["file_id"],
                    "title": info["file_name"],
                    "author": info["author"],
                    "host": info["url"],
                    "class_name": info["class_name"],
                    "doc_type": info["file_type"],
                    "is_published": info["is_published"],
                    "comment_count": comment_count,
                    "page_view": 0,
                    "download": info["download"],
                    "data": info['remark'],
                    "update_time": info["uploadDate"].strftime("%Y-%m-%d %H:%M:%S")
                })
        all_count = count_of_files + count_of_documents
        begin_index = int(offset) * (int(page_index) - 1)
        end_index = int(offset) * (int(page_index))
        final_result = result[begin_index:end_index]
        return {
            "result": final_result,
            "total": all_count
        }


def get_comments_by_docid(offset, page_index, doc_id, current_user):
    helper = document_controller.comment_controller()
    if request.method == "GET":
        info = helper.list_comments(doc_id=doc_id, current_user=current_user)
        result = []
        count_result = len(info)
        if count_result == 0:
            result = []
        else:
            begin_index = int(offset) * (int(page_index) - 1)
            end_index = int(offset) * (int(page_index))
            final = info[begin_index:end_index]
            for my in final:
                result.append({
                    "floor": my["floor"],
                    "doc_id": my["doc_id"],
                    "user": my["user"],
                    "comment": my["comment"],
                    "time": my["create_time"],
                    "comment_id": my["comment_id"],
                    "like_count": my["like_count"],
                    "bool_like": my["bool_like"]
                })
        return {
            "result": result,
            "total": count_result
        }


@app.route('/classes/names', methods=["GET"], strict_slashes=False)
def get_all_class_name():
    helper = document_controller.document_controller()
    class_info = helper.list_local_class()
    result = []
    for info in class_info:
        result.append({"value": info.class_name, "label": info.class_name})
    return jsonify(
        {
            "result": result
        }
    )


@app.route('/classes/mine', methods=["GET"], strict_slashes=False)
def get_my_class_name():
    if request.method == "GET":
        user_name = request.args.get("author")
        # token = request.cookies.get("token")
        offset = int(request.args.get("offset"))
        page_index = int(request.args.get("pageIndex"))
        result = get_my_classes(offset, page_index,user_name)
        return jsonify(
            {
                "result": result["result"],
                "total": result["total"]
            }
        )


@app.route('/classes', methods=["POST", "GET", "DELETE"], strict_slashes=False)
@check_user_token
def do_classes():
    helper = document_controller.document_controller()
    if request.method == "GET":
        user_name = request.cookies.get("user_name")
        # token = request.cookies.get("token")
        offset = int(request.args.get("offset"))
        page_index = int(request.args.get("pageIndex"))
        if user_name == None or user_name == '游客':
            result = get_public_classes(offset, page_index)
        else:
            result = get_all_classes(offset, page_index)
        return jsonify(
            {
                "result": result["result"],
                "total": result["total"]
            }
        )
    elif request.method == "POST":
        # data = request.get_data()
        # json_data = json.loads(data)
        author = request.cookies.get("user_name")
        # author = request.form.get("author")
        class_name = request.form.get('name')
        host = document_controller.host_controller().get_local_host_ip()

        is_published = request.form.get('is_published')
        explain = request.form.get('explain')
        print(class_name, host, author, is_published, explain)
        result = helper.add_local_class(
            class_name=class_name,
            host=host,
            author=author,
            is_published=is_published,
            explain=explain
        )
        return jsonify(
            {
                "code": result["code"],
                "message": result["message"]
            }
        )
    elif request.method == "DELETE":
        data = request.get_data()
        json_data = json.loads(data)
        class_name = json_data['name']
        author = request.cookies.get("user_name")
        # author = json_data['author']
        result = helper.delete_local_class(class_name=class_name, author=author)
        return jsonify(
            {
                "code": result["code"],
                "message": result["message"]
            }
        )


@app.route('/classes/search/', methods=["POST", "GET"])
@check_user_token
def search_class_info():
    helper = document_controller.document_controller()
    if request.method == "POST":
        class_info = helper.list_local_class()
        data = request.get_data()
        json_data = json.loads(data)
        offset = json_data['offset']
        page_index = json_data['pageIndex']
        begin_index = int(offset) * (int(page_index) - 1)
        end_index = int(offset) * (int(page_index))
        finale_list = class_info[begin_index:end_index]
        result = []
        count_result = len(class_info)
        if count_result == 0:
            result = []
        else:
            for info in finale_list:
                result.append({
                    "class_name": info.class_name,
                    "author": info.author,
                    "host": info.host,
                    "update_time": info.update_time,
                    "is_published": info.is_published
                })
        return jsonify(
            {
                "reuslt": result,
                "total": count_result,
                "offset": int(offset),
                "pageTotal": math.ceil(int(count_result) / int(offset))
            }
        )


@app.route('/')
@check_user_token
def hello_world():
    return "hello world"


@app.route('/user/register/', methods=["POST", ])
def register():
    data = request.get_data()
    json_data = json.loads(data)
    username = json_data['username']
    password = json_data['password']
    user_email = json_data['email']
    user_c = user_controller.user_controller()
    result = user_c.register(user_name=username, user_password=password, user_email=user_email)
    final_result = {
        "code": result["result"]["resultCode"],
        "message": result["result"]["resultMessage"]

    }
    return jsonify(final_result)


@app.route('/user/login/', methods=["POST", ])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user_c = user_controller.user_controller()
    result = user_c.login(user_name=username, user_password=password)
    final_result = {
        "code": result["result"]["resultCode"],
        "message": result["result"]["resultMessage"],
        "result": {
            "username": result["userInfo"]["username"],
            "token": result["userInfo"]["token"]
        }
    }
    return jsonify(final_result)


@app.route('/users/')
@check_user_token
def get_all_users():
    if request.method == "GET":
        helper = user_controller.user_controller()
        user_infos = helper.local_user_info()
        result = []
        count_result = len(user_infos)
        if count_result == 0:
            result = []
        else:
            for info in user_infos:
                result.append({
                    "user_name": info.user_name,
                    "user_from": info.user_from,
                    "user_email": info.user_email,
                    "update_time": info.update_time
                })
        # return result
        return jsonify(
            {
                "result": result,
                "total": count_result
            }
        )


@app.route('/user/detail')
# @check_user_token
def get_user_info():
    if request.method == "GET":
        user_name = request.cookies.get("user_name")
        helper = user_controller.user_controller()
        user_infos = helper.get_user_info("admin")
        return jsonify(user_infos)


@app.route('/users/public/')
def get_cluster_users():
    if request.method == "GET":
        helper = user_controller.user_controller()
        user_infos = helper.local_user_info()
        result = []
        count_result = len(user_infos)
        if count_result == 0:
            result = []
        else:
            for info in user_infos:
                result.append({
                    "user_name": info.user_name,
                    "user_from": info.user_from,
                    "user_email": info.user_email,
                    "update_time": info.update_time
                })
        # return result
        return jsonify(
            {
                "result": result,
                "total": count_result
            }
        )


@app.route('/users/delete/')
@must_login
def all_users_delete():
    if request.method == "GET":
        help = user_controller.user_controller()
        help.user_info_delete()
        return jsonify(
            {
                "result": "ok"
            }
        )


@app.route('/users/<user_name>')
@must_login
def user_delete_by_name(user_name):
    if request.method == "GET":
        help = user_controller.user_controller()
        result = help.user_info_delete()
        return jsonify(
            {
                "code": result["result"]["resultCode"],
                "message": result["result"]["resultMessage"]
            }
        )


@app.route('/documents/', methods=["POST", "GET"], strict_slashes=False)
@check_user_token
def do_documents():
    # cookie 待前端发布后修改
    user_name = "admin"
    token = "123"
    # user_name = request.cookies.get("user_name")
    # token = request.cookies.get("token")
    if user_name == None or token == None:
        if request.method == "GET":
            offset = int(request.args.get("offset"))
            page_index = int(request.args.get("pageIndex"))
            class_name = str(request.args.get("class_name"))
            result = get_documents(offset=offset, page_index=page_index,
                                   is_published=1, class_name=class_name)

            return jsonify(
                {
                    "code": "20000401",
                    "message": "获取所有文档信息成功",
                    "result": result["result"],
                    "total": result["total"]
                }
            )
        if request.method == "POST":
            return jsonify(
                {
                    "code": "20000499",
                    "message": "新增公用文档信息失败，TOKEN不存在",
                }
            )
    else:
        if request.method == "GET":
            offset = int(request.args.get("offset"))
            page_index = int(request.args.get("pageIndex"))
            class_name = str(request.args.get("class_name"))
            result = filter_document_by_class_name_no_public(offset=offset,
                                                             page_index=page_index,
                                                             class_name=class_name,
                                                             author=user_name
                                                             )
            # result = get_documents(offset=offset, page_index=page_index, is_published=0)
            return jsonify(
                {
                    "code": "20000401",
                    "message": "获取公用文档信息成功",
                    "result": result["result"],
                    "total": result["total"]
                }
            )
        elif request.method == "POST":
            # data = request.get_data()
            # json_data = json.loads(data)
            title = request.form.get('name')
            author = user_name
            # author = request.form.get('author')
            class_name = request.form.get('class_name')
            host = document_controller.host_controller().get_local_host_ip()
            # host = json_data['host']
            data = request.form.get('opinions')
            doc_type = request.form.get('doc_type')
            is_published = request.form.get('is_published')
            user_c = document_controller.document_controller()
            result = user_c.add_local_document(
                title=title,
                author=author,
                class_name=class_name,
                host=host,
                data=data,
                doc_type=doc_type,
                is_published=is_published,
            )
            return jsonify(
                {
                    "code": result["code"],
                    "message": result["message"]
                }
            )


@app.route('/document', methods=["GET"], strict_slashes=False)
@page_view_add
def get_document_by_docid():
    helper = document_controller.document_controller()
    # user_name = request.cookies.get("user_name")
    # token = request.cookies.get("token")
    # if user_name != None and token != None:
    if request.method == "GET":
        doc_id = str(request.args.get("doc_id"))
        # host = str(request.args.get("host"))
        result = helper.filter_document_by_docid(doc_id=doc_id)
        return jsonify(
            {
                "code": "20000401",
                "message": "获取文档详情成功",
                "result": {
                    "doc_id": result[0]["doc_id"],
                    "title": result[0]["title"],
                    "author": result[0]["author"],
                    "class_name": result[0]["class_name"],
                    "host": result[0]["host"],
                    "data": result[0]["data"],
                    "doc_type": result[0]["doc_type"],
                    "is_published": result[0]["is_published"],
                    "page_view": result[0]["page_view"],
                    "comment_count": result[0]["comment_count"],
                    "create_time": result[0]["create_time"].strftime("%Y-%m-%d %H:%M:%S"),
                }
            }
        )


@app.route('/documents/search', methods=["GET"], strict_slashes=False)
def get_document_by_docname():
    author = request.cookies.get("user_name")
    # token = request.cookies.get("token")
    # author = "admin"
    # if user_name != None and token != None:
    if request.method == "GET":
        offset = int(request.args.get("offset"))
        page_index = int(request.args.get("pageIndex"))
        doc_name = str(request.args.get("keyword"))
        print(doc_name)
        result = filter_document_by_name(offset=offset, page_index=page_index, doc_name=doc_name, author=author)
        return jsonify(
            {
                "code": "20000401",
                "message": "搜索成功,一共搜索了%s个结果" % result["total"],
                "result": result["result"],
                'total': result["total"]

            }
        )


@app.route('/comments', methods=["POST", "GET"], strict_slashes=False)
@check_user_token
def do_comments():
    author = request.cookies.get("user_name")
    if request.method == "GET":
        offset = int(request.args.get("offset"))
        page_index = int(request.args.get("pageIndex"))
        doc_id = str(request.args.get("doc_id"))
        current_user = author
        result = get_comments_by_docid(offset=offset, page_index=page_index, doc_id=doc_id, current_user=current_user)
        return {
            "code": "20000800",
            "message": "获取评论列表成功",
            "result": result["result"],
            "total": result["total"]
        }
    elif request.method == "POST":
        helper = document_controller.comment_controller()
        # data = `a()
        # print(data)
        # json_data = json.loads(data.decode("utf-8"))
        # print(json_data)
        doc_id = request.form.get("doc_id")
        comment = request.form.get("comment")
        # user = request.form.get("user")
        user = author
        result = helper.add_comment(doc_id=doc_id, comment=comment, user=user)
        return jsonify(
            {
                "code": result["code"],
                "message": result["message"],
            }
        )


@app.route('/documents/public', methods=["GET", ])
def get_public_documnet():
    if request.method == "GET":
        user_c = document_controller.document_controller()
        info = user_c.get_public_document()
        files = []
        if info.count() > 0:
            for file in info:
                files.append(
                    {
                        "doc_id": file["doc_id"],
                        "title": file["title"],
                        "author": file["author"],
                        "host": file["host"],
                        "class_name": file["class_name"],
                        "doc_type": file["doc_type"],
                        "is_published": file["is_published"],
                        "data": file["data"],
                        "update_time": file["update_time"].strftime("%Y-%m-%d %H:%M:%S")
                    }
                )

        return jsonify(
            {
                "code": "20000401",
                "message": "获取文档信息成功",
                "result": files
            }
        )


@app.route('/files/download/<uuid>', methods=["POST", "GET"], strict_slashes=False)
def file_download(uuid):
    helper = document_controller.gridfs_controller()
    if request.method == "GET":
        file, file_name = helper.downLoadFile(
            file_id=uuid
        )
        if file is not None:
            helper.download_count(file_id=uuid)
            # response.headers['Content-Type'] = 'application/octet-stream'
            # response.headers['Content-Disposition'] = 'attachment;filename={0};filename*={0}'.format(quote("常用命令.txt"))
            response = Response(file, content_type='application/octet-stream;')
            response.headers["Content-disposition"] = 'attachment; filename=%s' % quote(file_name)
            return response
        else:
            file_data = {
                "code": "20000699",
                "result": "文件不存在无法下载"
            }
            return jsonify(file_data)


#
# @app.route('/files/view/<uuid>', methods=["POST", "GET"], strict_slashes=False)
# def file_preview(uuid):
#     helper = document_controller.gridfs_controller()
#     if request.method == "GET":
#         file, file_name = helper.downLoadFile(
#             file_id=uuid
#         )
#         if file is not None:
#             return file
#         else:
#             file_data = {
#                 "code": "20000699",
#                 "result": "文件不存在无法下载"
#             }
#             return jsonify(file_data)
@app.route('/files/upload', methods=["POST", "GET"], strict_slashes=False)
# @must_login
def file_upload():
    ## 测试用户
    author = request.cookies.get("user_name")
    file_id = str(uuid.uuid1())
    url = "http://" + current_host + ":10018/files/download/" + file_id,
    helper = document_controller.gridfs_controller()
    if request.method == "POST":
        # data = request.get_data()
        # json_data = json.loads(data)
        file_data = request.files.get("file_data")
        file_name = request.form.get("file_name")
        file_type = request.form.get("file_type")
        class_name = request.form.get("class_name")
        author = author
        is_published = request.form.get("is_published")
        remark = request.form.get("remark")
        result = helper.upLoadFile(
            file_id=file_id,
            file_data=file_data,
            file_name=file_name,
            url=url,
            class_name=class_name,
            host=current_host,
            author=author,
            is_published=is_published,
            file_type=file_type,
            remark=remark
        )

        return jsonify(
            {
                "code": result["code"],
                "message": result["message"],
            }
        )


@app.route('/files/', methods=["POST", "GET"], strict_slashes=False)
@check_user_token
def get_all_files():
    helper = document_controller.gridfs_controller()
    if request.method == "GET":
        result = helper.get_infos()
        return jsonify(
            {
                "code": "20000601",
                "message": "获取文件信息成功",
                "result": result
            }
        )


@app.route('/files/public/', methods=["POST", "GET"], strict_slashes=False)
def get_public_files():
    helper = document_controller.gridfs_controller()
    if request.method == "GET":
        result = helper.get_public_infos()
        return jsonify(
            {
                "code": "20000601",
                "message": "获取文件信息成功",
                "result": result
            }
        )


@app.route('/comments/like/', methods=["POST"], strict_slashes=False)
def like_or_not_like():
    helper = document_controller.comment_controller()
    author = request.cookies.get("user_name")
    if request.method == "POST":
        comment_id = request.form.get("comment_id")
        user = author
        # user = request.form.get("user")
        if str(user) == '' or str(user) == '游客' or str(user) == None:
            result = {
                "code": 20000899,
                "message": "请先登录,再点赞"

            }
        else:
            result = helper.like_action(
                comment_id=int(comment_id),
                user=user
            )
        return jsonify(
            {
                "code": result["code"],
                "message": result["message"]
            }
        )


@app.route('/documents/download/', methods=["POST"], strict_slashes=False)
def down_load_count_add():
    helper = document_controller.document_controller()
    author = request.cookies.get("user_name")
    if request.method == "POST":
        doc_id = request.form.get("doc_id")
        user = author
        if str(user) == '' or str(user) == '游客' or str(user) == None:
            result = {
                "code": 20000999,
                "message": "请先登录,在下载"

            }
        else:
            helper.download_add(doc_id=doc_id)
            result = {
                "code": 20000900,
                "message": "下载成功"

            }
        return jsonify(
            {
                "code": result["code"],
                "message": result["message"]
            }
        )


# add comment

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10018)
