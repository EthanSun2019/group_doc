import json
import requests
from controller import document_controller



class cluster_object():
    # send req from other machine
    def req_from_other_node(self, url, method, headers, data):
        result = requests.request(method=method, url=url, headers=headers, data=data)
        json_result = json.loads(result.text)
        return json_result

    def join_cluster(self, master,data):
        helper=document_controller.host_controller()
        helper.add_host_db(ip=master,host_name="master",status=1,is_local=2)
        self.req_from_other_node(
            url="http://"+master+":10018/nodes/",
            method="post",
            headers="",
            data=data
        )


    def get_class_from_master(self):
        pass

    def get_users_from_master(self):
        pass

    def get_hosts_from_master(self):
        pass

    def get_public_documents_from_nodes(self):
        pass

    



