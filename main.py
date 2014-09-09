# encoding=utf-8
import json
import logging
import sys
from interface import Shell
from upstream import Upstream


def config_shell():
    logging.basicConfig(filename="interviewer.log", level='NOTSET')
    logger = logging.getLogger('Configurator')
    try:
        logger.info("读取配置")
        fp = open('config.json')
        configure = json.load(fp)
        fp.close()
        logger.info("正在配置Shell")
        upstream = Upstream(configure)
        shell = Shell(configure, upstream)
        return shell
    except:
        logger.critical('自动配置失败')
        exit(-1)


def main():
    logger = logging.getLogger("main")
    shell = config_shell()
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        logger.info("用户键盘中断, 正在退出")
    finally:
        shell.shutdown()


if __name__ == '__main__':
    main()
