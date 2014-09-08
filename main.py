# encoding=utf-8
import json
import logging
import sys
from interface import Shell
from upstream import Upstream


def config():
    logging.basicConfig(filename="interviewer.log", level='NOTSET')
    logger = logging.getLogger('Configurator')
    try:
        logger.info("读取配置")
        fp = open('config.json')
        configure = json.load(fp)
        fp.close()
        logger.info("配置本地缓存")
        logger.info("配置上游")
        upstream = Upstream(configure)
        shell = Shell(configure, upstream)
        return shell
    except:
        logger.critical('自动配置失败')
        exit(-1)


def main():
    shell = config()
    shell.cmdloop()


if __name__ == '__main__':
    main()
