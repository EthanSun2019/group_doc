import pymongo
from gridfs import GridFS


class gridfs_helper(object):
    def __init__(self, db, db_url):
        self.db = db
        self.db_url = db_url

    def connect_db(self):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        return db

    # 上传文件
    def upLoadFile(self, file_name, collection, data_link, host, author):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        filter_condition = {"filename": file_name, "url": data_link, "host": host, "author": author}
        gridfs_col = GridFS(db, collection=collection)
        file_ = "0"
        query = {"filename": "", "author": ""}
        query["filename"] = file_name
        query["author"] = author
        if gridfs_col.exists(query):
            return {"result": "file is exist"}
        else:
            try:
                with open(file_name, 'rb') as file_r:
                    file_data = file_r.read()
                    file_ = gridfs_col.put(data=file_data, **filter_condition)  # 上传到gridfs
            except:
                file_ = {"result": "upload file is not exist"}

        return file_
        # 按文件名获取文档

    def downLoadFile(self, file_name, collection, out_name, ver, author):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        gridfs_col = GridFS(db, collection=collection)
        try:
            file_data = gridfs_col.get_version(filename=file_name, version=ver, author=author).read()
            with open(out_name, 'wb') as file_w:
                file_w.write(file_data)
        except:
            return {"result": "file not exsits,download fail"}

    # 获取所有文件信息
    def get_collection_infos(self, coll_name):
        client = pymongo.MongoClient(self.db_url)
        db = client[self.db]
        coll = db[coll_name]
        all_list = coll.find()
        return all_list

    def insert_one_file(self, coll_name, document):
        db = self.connect_db()
        coll = db[coll_name]
        doc_count = coll.count_documents({"name": document["name"]})
        if doc_count == 0:
            coll.insert_one(document=document)
            return {"result": True, "info": str(document) + " insert sucess"}
        else:
            return {"result": False, "info": "doc class name is exsits"}


#
# test = MongoGridFS(db="gdocs", db_url="mongodb://localhost:27017")
# a = test.insert_one_document("gtype", document={"name": "AnsibleBook",
#                                                 "user": "admin",
#                                                 "remark": "Kubernetes文档",
#                                                 "time": datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")})

# list = test.get_collection_infos(coll_name="gtype")
# for str in list:
#     print(str)

