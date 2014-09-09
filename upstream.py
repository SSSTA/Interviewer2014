# encoding=utf-8
"""
提供装满新人信息dict对象
"""

import logging
import copy
from pyquery import PyQuery

BASE = "http://sssta.sinaapp.com/index.php/Home/Fresh/"
URL = BASE + "interview?er={interviewer}&id={{id}}#"
COMMIT = BASE + "set?er={interviewer}&id={{id}}&level={{level}}&score={{score}}"
APPEND = BASE + "set?er={interviewer}&id={{id}}&append={{append}}"


class Upstream(object):
    def __init__(self, configure):
        self.logger = logging.getLogger("Upstream")
        self.logger.info("正在配置上游")
        upstream = configure.get('upstream', 'origin')
        self.logger.info("上游 = %s", upstream)
        self.interviewer = configure['interviewer']
        self.logger.info("面试官 = %s", self.interviewer)
        self.profiles = {}
        if upstream == 'origin':
            try:
                self.baseurl = URL.format(**configure)
                self.appendurl = APPEND.format(**configure)
                self.commiturl = COMMIT.format(**configure)
                self.logger.info("fetch-URL: %s", self.baseurl)
                self.logger.info("append-URL: %s", self.appendurl)
                self.logger.info("commit-URL: %s", self.commiturl)
            # 如果配置文件出现了奇怪的问题
            # 以至于无法配置base url
            except Exception as e:
                logging.error('Upstream无法解析的配置文件:\n%s\n当前配置:%s',
                              str(e) + e.__traceback__, str(configure))
                raise ValueError

    def fetch(self, uid):
        self.logger.info("寻找ID: {}".format(uid))
        if uid in self.profiles:
            self.logger.info("ID: {} - 缓存命中".format(uid))
            return self.profiles[uid]
        # 抓取信息
        self.logger.info("ID: {} - 缓存未命中".format(uid))
        try:
            doc = PyQuery(url=self.baseurl.format(id=uid))
            content = doc('.col-xs-12').children().children()
            _texts = content('p')
            _base_info = content('.lead').text().split(maxsplit=2)
            if len(_base_info) != 3:
                _base_info += [''] * (3 - len(_base_info))
            uid, name, sex = _base_info
            _contact = content('.col-sm-9')('div')[2] \
                .text_content().split(maxsplit=3)
            if len(_contact) != 4:
                _contact += [''] * (4 - len(_contact))
            tel, email, _, qq = _contact
            img = content('img')[0].get('src')
            describe = _texts[0].text
            dept = content('span')[4].text.strip()
            reason = _texts[1].text
            experience = _texts[2].text
            # 获取状态
            status = doc('#sidebar')('.list-group')
            js = doc('script')[2].text.split()
            c2, c3, c4 = js[7][1:-2], js[11][1:-2], js[27][1:-2]
            specials = status('.list-group-item')[5].text
        except Exception as e:
            self.logger.error("信息自动获取失败:{}".format(e))
            return None
        # 整合
        profile = {
            "profile": {
                "name": name.strip(),
                "id": uid,
                "sex": sex,
                "tel": tel.strip(),
                "email": email.strip(),
                "qq": qq.strip(),
                "img": img,
                "describe": describe,
            },
            "application": {
                "dept": dept,
                "reason": reason,
                "experience": experience,
            },
            "status": {
                "score-1": c2,
                "score-2": c3,
                "current": (c4, ["面试中", "已通过", '被否决']),
                "specials": specials,
            }
        }
        self.profiles[uid] = copy.deepcopy(profile)
        self.logger.info("抓取结果 {}".format(profile))
        return profile

    def commit(self, profile):
        uid = profile['profile']['id']
        new = profile['status']
        raw = self.profiles[uid]['status']
        hock = {
            "score-1": 2,
            "score-2": 3,
            "current": 4,
        }
        for key in raw:
            if new[key] != raw[key]:
                if key in hock:
                    PyQuery(self.commiturl.format(
                        id=uid,
                        level=hock[key],
                        score=new[key]))
                else:
                    PyQuery(url=self.appendurl.format(
                        id=uid,
                        append=new[key]))

