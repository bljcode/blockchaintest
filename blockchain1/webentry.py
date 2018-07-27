import hashlib
import json
from uuid import uuid4
from .chain import Blockchain
from flask import Flask
#
app = Flask(__name__)
#虚拟一个地址
node_identifier = str(uuid4()).replace('-','')

blockchain1 =Blockchain()









