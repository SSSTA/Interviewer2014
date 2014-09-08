# encoding=utf-8
from upstream import Upstream
from pymongo import MongoClient


def main():
    us = Upstream({"interviewer": "ROBOT"})
    db = MongoClient().sssta.raw
    for i in range(1,75):
        d = us.fetch(i)
        print(i, '\n', d)
        if isinstance(d, dict):
            db.insert(us.fetch(i))


if __name__ == '__main__':
    main()
