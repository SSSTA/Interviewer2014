# encoding=utf-8
import logging
import subprocess
import json
import os
import cmd


class Shell(cmd.Cmd):
    prompt = "===> "

    def __init__(self, configure, upstream):
        super().__init__()
        self.current_profile = None
        self.indent = configure.get('indent', 4)
        self.editor = configure.get('editor', 'vim')
        self.md5 = configure.get('md5', 'md5sum')
        self.tmp = configure.get('tmp', '/dev/shm')
        self.logger = logging.getLogger('Interaction')
        self.upstream = upstream
        self.current_uid = 0

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
            print("文件已修改, 请注意提交")

    def do_fetch(self, arg):
        self.current_profile = self.upstream.fetch(self.current_uid)

    def do_view(self, arg):
        self.handle(self.current_profile)

    def do_checkout(self, uid):
        self.do_co(uid)

    def do_co(self, uid=None):
        if uid == '':
            self.current_uid += 1
        else:
            self.current_uid = int(uid)
        print("\t当前工作于 UID:", self.current_uid)
        self.prompt = "{:3d}>".format(self.current_uid)
