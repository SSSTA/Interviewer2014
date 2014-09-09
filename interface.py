# encoding=utf-8
import logging
import subprocess
import json
import os
import cmd
from pymongo import MongoClient


class Shell(cmd.Cmd):
    prompt = "===> "

    def __init__(self, configure, upstream):
        super().__init__()
        self.current_profile = None
        self.responsibility = configure['responsibility']
        self.indent = configure.get('indent', 4)
        self.editor = configure.get('editor', 'vim')
        self.md5 = configure.get('md5', 'md5sum')
        self.tmp = configure.get('tmp', '/dev/shm')
        self.logger = logging.getLogger('Interaction')
        self.upstream = upstream
        self.current_uid = 0
        self.connect = MongoClient()
        self.mirror = self.connect.sssta.fresh
        # 初始状态为无更改已提交
        self.current_committed = True

    def file_md5(self, path: str):
        if os.path.exists(path):
            status, val = subprocess.getstatusoutput(
                ' '.join([self.md5, path]))
            if status:
                raise IOError
            else:
                return val.split()[0]

    def swap_to_file(self, profile):
        try:
            uid = profile['profile']['id']
            path = os.path.join(self.tmp, 'uid{}.json'.format(uid))
            fp = open(path, 'w')
            json.dump(profile, fp, indent=self.indent,
                      ensure_ascii=False,
                      sort_keys=True)
            fp.close()
            return path
        except:
            pass

    def handle(self, profile):
        path = self.swap_to_file(profile)
        raw_md5 = self.file_md5(path)
        subprocess.call([self.editor, path])
        new_md5 = self.file_md5(path)
        if new_md5 == raw_md5:
            print(self.editor + "已关闭, 文件未修改")
        else:
            self.current_committed = False
            print("文件已修改, 正在读回")
            try:
                fp = open(path)
                new_profile = json.load(fp)
                self.current_profile = new_profile
            except:
                self.logger.error("更改后文件读回失败")
                print("读取失败: 修改已抛弃")
            finally:
                fp.close()

    def shutdown(self):
        self.connect.close()


    def do_pull(self, arg):
        self.current_profile = self.upstream.fetch(self.current_uid)

    def do_pl(self, arg):
        self.do_pull(None)

    def do_v(self, arg):
        self.handle(self.current_profile)

    def do_checkout(self, uid):
        self.do_co(uid)

    def do_co(self, uid=None):
        if not self.current_committed:
            print("当前修改未提交!")
            return
        old_uid = self.current_uid
        if uid == '':
            self.current_uid += 1
        else:
            self.current_uid = int(uid)
        print("正在抓取")
        try:
            self.do_pull(None)
            print("\t当前工作于 UID:", self.current_uid)
            self.prompt = "{:3d}>".format(self.current_uid)
        except:
            print("读取失败")
            self.current_uid = old_uid

    def do_pwd(self, arg):
        print("\t当前工作于 UID:", self.current_uid)

    def do_commit(self, args):
        if not self.current_committed:
            self.mirror.insert(self.current_profile)
            print("UID:", self.current_uid, "已提交")
            print("COUNT", self.mirror.count())
            self.current_committed = True
        else:
            print("Nothing to commit")

    def do_score(self, arg):
        try:
            score = int(arg)
            if score < 0:
                score = 0
            if score > 5:
                score = 5
        except:
            print("无法理解的数值")
            return
        self.current_profile['status']['score-%d' % self.responsibility] = score
        self.current_committed = False

    def do_append(self, arg):
        self.current_profile['status']['specials'] += ('\n' + arg)
        self.current_committed = False

    def do_push(self, arg):
        self.do_pwd(None)
        self.upstream.commit(self.current_profile)
        print("已推送")
