# from mongoengine import *
#
# from controller.user_controller import user_info
#
# connect(db='group_docs', host="192.168.196.29", port=27017, username="groupdoc", password="admin@123")
#
# myuser = user_info.objects()
#
# for info in myuser:
#     print(info.user_name)

def wrapper(func):  # 装饰器函数，func为被装饰函数
    def inner(*args, **kwargs):
        """被装饰函数前需要添加的内容"""
        print("hello")
        ret = func(*args, **kwargs)  # 被装饰函数
        """被装饰函数后需要添加的内容"""
        return ret

    return inner


@wrapper
def fun():
    print('你好')

fun()