# -*- coding: utf-8 -*-
# @Author: zhangjin09
# @Date:   2020-08-31 16:47:42
# @Last Modified by:   zhangjin09
# @Last Modified time: 2020-08-31 16:47:42

from _Global import _GG;
from function.base import *;

def __getExposeData__():
	return {
		# "exposeDataName" : {},
	};

def __getExposeMethod__(DoType):
	return {
		# "defaultFun" : DoType.AddToRear,
	};

def __getDepends__():
	return [
		# {
		# 	"path" : "tempBehavior", 
		# 	"basePath" : _GG("g_CommonPath") + "behavior/",
		# },
	];

class CSharpBehavior(_GG("BaseBehavior")):
	def __init__(self):
		super(CSharpBehavior, self).__init__(__getDepends__(), __getExposeData__(), __getExposeMethod__, __file__);
		self._className_ = CSharpBehavior.__name__;
		pass;

	# 默认方法【obj为绑定该组件的对象，argList和argDict为可变参数，_retTuple为该组件的前个函数返回值】
	# def defaultFun(self, obj, *argList, _retTuple = None, **argDict):
	# 	_GG("Log").i(obj._className_);
	# 	pass;

	def parse(self, obj, tb, _retTuple = None):
		pass;
