# -*- coding: utf-8 -*-
# @Author: zhangjin09
# @Date:   2020-09-05 16:16:01
# @Last Modified by:   zhangjin09
# @Last Modified time: 2020-09-05 16:16:01

import wx;

from _Global import _GG;
from function.base import *;

descriptionConfig = [
	"【输入目录】存放需要导出的Excel文件夹路径。",
	"【输出目录】存放所导出代码的文件夹路径（如为空，则默认为输入目录）。”",
	"【导出格式】导出的代码格式。",
	"",
	"【以下为Excel表格格式要求】",
	"",
	"【Sheet】工作簿名称必须带有引文括号，且括号内必须为英文字符，如“测试表(TestTable)”。",
	"【注释】在需要注释行（即不导出该行数据）的第一个单元格中，开头添加“#”。",
	"【Export】第一行中，在需要导出列的单元格中，添加“*”，会导出该列对应的key，以加快在代码中查找该key对应的数据。",
	"【Key】从第一行开始，直到出现没被注释，且存在值不为空的行，作为所要导出的key。",
	"【类型】从Key所在行开始，直到出现没被注释，且存在值不为空的行，作为各列所要导出的数据类型。",
	"【数据】从类型所在行开始，出现没被注释，且存在值不为空的行，会导出该行的数据。",
];

class InstructionViewUI(wx.Panel):
	"""docstring for InstructionViewUI"""
	def __init__(self, parent, id = -1, curPath = "", viewCtr = None, params = {}):
		self.initParams(params);
		super(InstructionViewUI, self).__init__(parent, id, pos = self.__params["pos"], size = self.__params["size"], style = self.__params["style"]);
		self._className_ = InstructionViewUI.__name__;
		self._curPath = curPath;
		self.__viewCtr = viewCtr;

	def initParams(self, params):
		# 初始化参数
		self.__params = {
			"pos" : (0,0),
			"size" : (-1,-1),
			"style" : wx.BORDER_THEME,
		};
		for k,v in params.items():
			self.__params[k] = v;

	def getCtr(self):
		return self.__viewCtr;

	def initView(self):
		self.createControls(); # 创建控件
		self.initViewLayout(); # 初始化布局

	def createControls(self):
		# self.getCtr().createCtrByKey("key", self._curPath + "***View"); # , parent = self, params = {}
		self.createTitle();
		self.createDesc();
		pass;
		
	def initViewLayout(self):
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(self.__title, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 5);
		box.Add(self.__desc, flag = wx.ALIGN_CENTER|wx.TOP, border = 5);
		self.SetSizer(box);

	def updateView(self, data):
		pass;

	def createTitle(self):
		self.__title = wx.StaticText(self, label = "使用说明");
		self.__title.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
	
	def createDesc(self):
		self.__desc = wx.TextCtrl(self, size = (self.GetSize().x, max(600, self.GetSize().y)), style = wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH);
		for desc in descriptionConfig:
			self.__desc.AppendText(f"*{desc}\n");
