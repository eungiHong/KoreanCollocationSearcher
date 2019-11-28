import os
import re
import fnmatch
import Tools
from konlpy.tag import Kkma
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client["myCol"]

collection = db["collocations"]

post = {"morpheme": "먹다",
        "pos": "VV",
        "collocations": ["먹/VV + 을/ETM + 것/NNB", "애/NNG + 를/JKO + 먹/VV", "점심/NNG + 을/JKO + 먹/VV"]
        }

posts = db.posts
post_id = posts.insert_one(post).inserted_id
print(post_id)
