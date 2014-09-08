# encoding=utf-8
import logging
from pymongo import MongoClient


class Mirror:
    def __init__(self, configure):
        mirror_type = configure.get('localmirror', None)
        if mirror_type == 'mongo':
            pass
        else:
            logging.critical("无效的本地镜像配置: {}".format(mirror_type))
