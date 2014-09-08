# encoding=utf-8
"""
提供装满新人信息dict对象
"""

import logging
import copy
from pyquery import PyQuery

BASE = "http://sssta.sinaapp.com/index.php/Home/Fresh/"
URL = BASE + "interview?er={interviewer}&id={{id}}#"
COMMIT = BASE + "set?er={er}&id={id}&level={level}&score={score}"
APPEND = BASE + "set?er={er}&id={id}&append={append}"


class Upstream(object):
    def __init__(self, configure):
        upstream = configure.get('upstream', None)
        self.interviewer = configure['interviewer']
        self.logger = logging.getLogger("Upstream")
        self.profiles = {}
        if upstream == 'origin':
            try:
                self.baseurl = URL.format(**configure)
            # 如果配置文件出现了奇怪的问题
            # 以至于无法配置base url
            except:
                logging.error('Upstream无法解析的配置文件', **configure)
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
            uid, name, sex = content('.lead').text().split(maxsplit=2)
            tel, email, _, qq = content('.col-sm-9')('div')[2] \
                .text_content().split(maxsplit=3)
            img = content('img')[0].get('src')
            describe = _texts[0].text
            dept = content('span')[4].text.strip()
            reason = _texts[1].text
            experience = _texts[2].text
            # 获取状态
            status = doc('#sidebar')('.list-group')
            js = doc('script')[2].text.split()
            c2, c3, c4 = js[7][1:-2], js[11][1:-2], js[27][1:-2]
            specials = [s.text for s in status('.list-group-item')[5:]]
        except:
            self.logger.error("信息自动获取失败")
            return None
        # 整合
        profile = {
            "profile": {
                "name": name,
                "id": uid,
                "sex": sex,
                "tel": tel,
                "email": email,
                "qq": qq,
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
        uid = profile['profile']['uid']
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
                    PyQuery(url=COMMIT.format(er=self.interviewer,
                                              id=uid,
                                              level=hock[key],
                                              score=new[key]))
                else:
                    PyQuery(url=APPEND.format(er=self.interviewer,
                                              id=uid,
                                              append=new[key]))
