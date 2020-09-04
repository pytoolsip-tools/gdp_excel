import os;

from function.base import *;

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__)); # 当前文件目录

CsharpGameDataParser = require(CURRENT_PATH, "CsharpGameDataParser", "CsharpGameDataParser");