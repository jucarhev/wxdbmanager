# -*- coding: utf-8 -*- 

import wx
import wx.xrc
import wx.aui
import sys, os
import re
import wx.adv

from controller import Controller

class main ( wx.Frame ):
	""" Principal class """

	controller = Controller()

	List_tables = []

	is_connect = False
	database_old_selected = ''
	item_selected = None
	
	def __init__( self, parent ):

		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = (0,0), size = wx.Size( 500,300 ) )

		path = os.path.abspath("./icons/wxdbmanager_32x32.png")
		icon = wx.Icon(path, wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)

		self.check_connection()

	def gui(self):		
		self.m_toolBar1 = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY ) 
		self.Connection_tool = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons/025-settings-1.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		self.Console_tool = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons/021-code.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		self.Users_tool = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons/012-user.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		self.Settings_tool = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons/015-settings.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 

		self.m_toolBar1.Realize() 
		
		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.tree = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE )
		bSizer1.Add( self.tree, 1, wx.ALL|wx.EXPAND, 5 )

		self.add_items_tree()

		self.notebook = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE )
		self.m_panel1 = wx.Panel( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		
		self.notebook.AddPage( about_panel(self.notebook), u"WxDBManager")
		
		bSizer1.Add( self.notebook, 5, wx.EXPAND |wx.ALL, 5  )
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		self.SetSize((800,600))
		self.SetTitle("WxDBManager")
		self.Show()

		self.Bind(wx.EVT_TOOL, self.conection_manager, self.Connection_tool)
		self.Bind(wx.EVT_TOOL, self.console, self.Console_tool)
		

		self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.notebook_)

		#self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.sert)

	def sert(self, evt):
		print( "==========================> double click " )

	def notebook_(self, evt):
		n = self.notebook.GetPageCount()
		if n == 0:
			self.notebook.AddPage( about_panel(self.notebook), u"WxDBManager")

	def check_connection(self):
		print("# Verificanco conexion")
		m = self.controller.check_conn()
		if m == 1:
			#wx.MessageBox("ok", 'Info',wx.OK | wx.ICON_INFORMATION)
			print("Ok")
			self.is_connect = True
			self.gui()
		else:
			wx.MessageBox(str(m), 'Info',wx.OK | wx.ICON_INFORMATION)
			self.conection_manager()
			self.check_connection()

	def conection_manager(self, evt=''):
		NewBD = Dialog_Connection(self)
		NewBD.ShowModal()
		NewBD.Destroy()

	def console(self, evt):
		self.notebook.AddPage( console_panel(self.notebook), u"Console")

	def add_items_tree(self):
		root = self.tree.AddRoot('Databases')
		self.tree.Expand(root)
		self.get_databases_list(self.tree,root)

	def get_databases_list(self,tree,root):
		self.items_database_list = {}

		image_list = wx.ImageList(16, 16)
		img_database = image_list.Add(wx.Image("icons/database.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
		self.img_table    = image_list.Add(wx.Image("icons/table.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())

		tree.AssignImageList(image_list)

		if self.is_connect == True:
			rows = self.controller.get_databases()
			for row in rows:
				item = tree.AppendItem(root, row[0])
				self.items_database_list[row[0]]=(item)
				# Agregando imagen a los items				
				tree.SetPyData(item, None)
				tree.SetItemImage(item, img_database, wx.TreeItemIcon_Normal)
				self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, tree)
				#self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnSelChanged, tree)

	def OnSelChanged(self,event):
		#print(self.database_old_selected)
		items =  event.GetItem()
		db_nodo = self.tree.GetItemText(items)
		self.item_selected = db_nodo

		if db_nodo != 'Databases':
			if self.check_is_database(items) == 1:
				self.database_active = db_nodo
				if self.database_old_selected == '':
					self.database_old_selected = db_nodo
					self.object_item = self.items_database_list.get(db_nodo)
				else:
					self.database_old_selected = db_nodo
					self.tree.DeleteChildren(self.object_item)
					self.object_item = self.items_database_list.get(db_nodo)

				if self.database_active != '':
					self.add_tables_nodo(self.items_database_list.get(db_nodo), self.tree.GetItemText(items))
				self.option_menu = ['New Table', 'Drop DB']
			else:
				self.table_active = db_nodo
				self.option_menu = ['Select','Drop Table','Describe']
		else:
			self.option_menu = ['New DB']

		self.popupmenu = wx.Menu()
		for text in self.option_menu:
			item = self.popupmenu.Append(-1, text)
			self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
		self.tree.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

	def check_is_database(self,db):
		for value in self.items_database_list.values():
			if value == db:
				return 1
		
	def add_tables_nodo(self,root,db_name):
		n = len(self.List_tables)
		if n == 0:
			pass
		else:
			self.List_tables = []

		rows = self.controller.get_tables(self.database_active)
		for row in rows:
			w = self.tree.AppendItem(root,str(row[0]))
			self.List_tables.append(row[0])

			self.tree.SetPyData(w, None)
			self.tree.SetItemImage(w, self.img_table, wx.TreeItemIcon_Normal)
	
	def OnShowPopup(self, event):
		pos = event.GetPosition()
		pos = self.ScreenToClient(pos)
		self.PopupMenu(self.popupmenu, pos)

	def OnPopupItemSelected(self, event):
		item = self.popupmenu.GetLabel(event.GetId())

		if item == 'Select':
			self.notebook.AddPage( select_table_panel(self.notebook, self.database_active, self.table_active), u"Select "+ self.table_active)
		
		elif item == 'New DB':
			NewBD = new_database_dialog(self)
			NewBD.ShowModal()
			NewBD.Destroy()
			self.tree.DeleteAllItems()
			self.add_items_tree()
		
		elif item == 'Drop DB':
			dlg = wx.MessageDialog(None, "Do you want to delete this database?",'Delete',wx.YES_NO | wx.ICON_QUESTION)
			result = dlg.ShowModal()

			if result == wx.ID_YES:
				self.controller.Database_Name=''
				e = self.controller.drop_database(self.database_active)
				print(e)
			else:
				print("No pressed")
			
			self.tree.DeleteAllItems()
			self.add_items_tree()

		elif item == 'Drop Table':
			print( self.item_selected )
			
			dlg = wx.MessageDialog(None, "Do you want to delete this database?",'Delete',wx.YES_NO | wx.ICON_QUESTION)
			result = dlg.ShowModal()

			if result == wx.ID_YES:
				n = self.controller.execute_sql("DROP TABLE " + self.item_selected , self.database_active)
				if n == None:
					wx.MessageBox("Table delete", 'Info',wx.OK | wx.ICON_INFORMATION)
				else:
					wx.MessageBox(str(n), 'Info',wx.OK | wx.ICON_INFORMATION)
			
			self.tree.DeleteAllItems()
			self.add_items_tree()
			

		elif item == 'New Table':
			NewBD = new_table_dialog(self, self.database_active)
			NewBD.ShowModal()
			NewBD.Destroy()

			self.tree.DeleteChildren(self.items_database_list.get(self.database_active))
			self.add_tables_nodo(self.items_database_list.get(self.database_active), self.database_active)

		elif item == 'Describe':
			self.notebook.AddPage( describe_table_panel(self.notebook, self.database_active, self.table_active), u"Describe "+ self.table_active)

class Dialog_Connection ( wx.Dialog ):

	controller = Controller()
	is_save = False

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Administrator", pos = wx.DefaultPosition, size = wx.Size( 300,220 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Conecction", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		self.m_staticText1.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		bSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

		self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"HostName:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )

		gSizer1.Add( self.m_staticText2, 0, wx.ALL, 5 )

		self.txtHostname = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.txtHostname, 0, wx.ALL, 5 )

		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"UserName:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )

		gSizer1.Add( self.m_staticText3, 0, wx.ALL, 5 )

		self.txtUsername = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.txtUsername, 0, wx.ALL, 5 )

		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Password:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )

		gSizer1.Add( self.m_staticText4, 0, wx.ALL, 5 )

		self.txtPassword = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.txtPassword, 0, wx.ALL, 5 )

		bSizer1.Add( gSizer1, 1, wx.EXPAND, 5 )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.btnSave = wx.Button( self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.btnSave, 0, wx.ALL, 5 )

		self.btnTest = wx.Button( self, wx.ID_ANY, u"Test", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.btnTest, 0, wx.ALL, 5 )


		bSizer1.Add( bSizer2, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

		self.Bind(wx.EVT_BUTTON, self.Save, self.btnSave)
		self.Bind(wx.EVT_BUTTON, self.Test, self.btnTest)

	def Save(self, evt):
		self.controller.Host_Name = self.txtHostname.GetValue()
		self.controller.User_Name = self.txtUsername.GetValue()
		self.controller.Password = self.txtPassword.GetValue()

		self.controller.write_json_connection()
		self.is_save = True

	def Test(self, evt):
		if self.is_save == False:
			wx.MessageBox("Save data" , 'Info',wx.OK | wx.ICON_INFORMATION)
		else:
			r = self.controller.check_conn()
			if r == 1:
				wx.MessageBox("Success" , 'Info',wx.OK | wx.ICON_INFORMATION)
			else:
				wx.MessageBox(str(r) , 'Info',wx.OK | wx.ICON_INFORMATION)

class new_database_dialog ( wx.Dialog ):
	controller = Controller()

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New Database", pos = wx.DefaultPosition, size = wx.Size( 261,142 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.lbl1 = wx.StaticText( self, wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl1.Wrap( -1 )
		bSizer5.Add( self.lbl1, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		self.txtDatabase = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,-1 ), 0 )
		bSizer5.Add( self.txtDatabase, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		bSizer4.Add( bSizer5, 0, wx.EXPAND, 5 )
		
		self.btnCreate = wx.Button( self, wx.ID_ANY, u"Create", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.btnCreate, 0, wx.ALL, 5 )
		
		self.SetSizer( bSizer4 )
		self.Layout()
		
		self.Centre( wx.BOTH )

		self.btnCreate.Bind(wx.EVT_BUTTON,self.create_database)

	def create_database(self, evt):
		db = self.txtDatabase.GetValue()
		n = self.controller.create_new_database(db)
		if n == '':
			print("s")
		else:
			wx.MessageBox(str(n), 'Info',wx.OK | wx.ICON_INFORMATION)

class new_table_dialog ( wx.Dialog ):

	table_name = ''
	controller = Controller()
	
	def __init__( self, parent , db):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New table", pos = wx.DefaultPosition, size = wx.Size( 600,254 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		gSizer2 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.lbl1 = wx.StaticText( self, wx.ID_ANY, u"Field name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl1.Wrap( -1 )
		gSizer2.Add( self.lbl1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.txtName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.txtName, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.lbl2 = wx.StaticText( self, wx.ID_ANY, u"long", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl2.Wrap( -1 )
		gSizer2.Add( self.lbl2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.spinLong = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 255, 1 )
		gSizer2.Add( self.spinLong, 0, wx.ALL, 5 )
		
		self.lbl3 = wx.StaticText( self, wx.ID_ANY, u"type", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl3.Wrap( -1 )
		gSizer2.Add( self.lbl3, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		cboTypeChoices = [ u"varchar", u"integer", u"boolean", u"date" ]
		self.cboType = wx.ComboBox( self, wx.ID_ANY, u"varchar", wx.DefaultPosition, wx.DefaultSize, cboTypeChoices, 0 )
		gSizer2.Add( self.cboType, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.lbl4 = wx.StaticText( self, wx.ID_ANY, u"Default:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lbl4.Wrap( -1 )
		gSizer2.Add( self.lbl4, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.txtDefault = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.txtDefault, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.cbxRequired = wx.CheckBox( self, wx.ID_ANY, u"Not null", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.cbxRequired, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.cbxPrimary = wx.CheckBox( self, wx.ID_ANY, u"Primary", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.cbxPrimary, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.btnAdd = wx.Button( self, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.btnAdd, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		
		bSizer7.Add( gSizer2, 1, wx.EXPAND, 5 )
		
		
		bSizer3.Add( bSizer7, 1, wx.EXPAND, 5 )
		
		bSizer8 = wx.BoxSizer( wx.VERTICAL )
		
		self.txtText = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.TE_MULTILINE )
		bSizer8.Add( self.txtText, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.btnGenerate = wx.Button( self, wx.ID_ANY, u"Generar", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer8.Add( self.btnGenerate, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
		
		
		bSizer3.Add( bSizer8, 2, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer3 )
		self.Layout()

		self.btnAdd.Bind(wx.EVT_BUTTON,self.add_to_textbox)
		self.btnGenerate.Bind(wx.EVT_BUTTON,self.generate_code_table)

		self.table_name_check()
		self.db = db

	def table_name_check(self):
		while self.table_name == '':
			dlg = wx.TextEntryDialog(self, 'Table', 'Enter table name')
			dlg.ShowModal()
			self.table_name = dlg.GetValue()

		self.txtText.SetValue("create table "+self.table_name+'(\n')

	def add_to_textbox(self, evt):
		name = self.txtName.GetValue()
		value = self.spinLong.GetValue()
		typef = self.cboType.GetValue()
		required = self.cbxRequired.GetValue()
		primary = self.cbxPrimary.GetValue()
		default = self.txtDefault.GetValue()

		r,p,d = '', '',''
		if required == True:
			r = 'not null'
		if primary == True:
			p = 'auto_increment primary key'

		if default != '':
			if default.find('&i'):
				d = ' default '+default+ ' '
				d = d.replace('&i', '')
			elif default.find('&s'):
				d = " default '"+default+ "' "
				d = d.replace('&s', '')

		if typef=='date':
			self.txtText.AppendText(name +' '+ typef+ ' ' + r +' '+ p + d +',\n')
		else:
			self.txtText.AppendText(name +' '+ typef+'('+str(value)+') '+ r +' '+ p + d +',\n')

		self.txtName.SetValue('')
		self.spinLong.SetValue(1)
		self.cbxRequired.SetValue(False)
		self.cbxPrimary.SetValue(False)
		self.txtDefault.SetValue('')

	def generate_code_table(self, evt):
		text = self.txtText.GetValue()
		text = text[:-1]
		text = text[:-1]
		text = text + ')Engine=innodb;'
		self.controller.Database_Name= self.db
		r = self.controller.create_new_table(text,self.db)
		if r == None:
			wx.MessageBox("Table create", 'Info',wx.OK | wx.ICON_INFORMATION)
			self.Close()
		else:
			wx.MessageBox(str(r) , 'Info',wx.OK | wx.ICON_INFORMATION)

class add_new_column ( wx.Dialog ):
	controller = Controller()

	def __init__( self, parent, table, db ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Add new column", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		self.table = table
		self.db = db 

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Field Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		gSizer1.Add( self.m_staticText1, 0, wx.ALL, 5 )

		self.txtFieldName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.txtFieldName, 0, wx.ALL, 5 )

		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Type", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )

		gSizer1.Add( self.m_staticText3, 0, wx.ALL, 5 )

		cboTypeChoices =  [ u"varchar", u"integer", u"boolean", u"date" ]
		self.cboType = wx.ComboBox( self, wx.ID_ANY, 'varchar', wx.DefaultPosition, wx.DefaultSize, cboTypeChoices, 0 )
		gSizer1.Add( self.cboType, 0, wx.ALL, 5 )

		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Long", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )

		gSizer1.Add( self.m_staticText4, 0, wx.ALL, 5 )

		self.spinLong = wx.SpinCtrl( self, wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 255, 10 )
		gSizer1.Add( self.spinLong, 0, wx.ALL, 5 )

		self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Default", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )

		gSizer1.Add( self.m_staticText5, 0, wx.ALL, 5 )

		self.txtDefault = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.txtDefault, 0, wx.ALL, 5 )

		self.checknull = wx.CheckBox( self, wx.ID_ANY, u"Not Null", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.checknull, 0, wx.ALL, 5 )

		self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )

		gSizer1.Add( self.m_staticText7, 0, wx.ALL, 5 )

		cboAfterChoices = [ u"After", u"Before", u"After" ]
		self.cboAfter = wx.ComboBox( self, wx.ID_ANY, u"After", wx.DefaultPosition, wx.DefaultSize, cboAfterChoices, 0 )
		self.cboAfter.SetSelection( 0 )
		gSizer1.Add( self.cboAfter, 0, wx.ALL, 5 )

		self.columns_from_table()
		
		self.cboFields = wx.ComboBox( self, wx.ID_ANY, self.cboFieldsChoices[0] , wx.DefaultPosition, wx.DefaultSize, self.cboFieldsChoices, 0 )
		gSizer1.Add( self.cboFields, 0, wx.ALL, 5 )

		self.btnAdd = wx.Button( self, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.btnAdd, 0, wx.ALL, 5 )


		bSizer1.Add( gSizer1, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()
		bSizer1.Fit( self )

		self.Centre( wx.BOTH )

		self.Bind(wx.EVT_BUTTON, self.addcolumns ,self.btnAdd )

	def addcolumns(self, evt):
		if self.checknull.GetValue() == True:
			null = ' Not null '
		else:
			null = ''

		sql = 'ALTER TABLE '+self.table+' ADD COLUMN '+self.txtFieldName.GetValue()
		sql = sql +' '+self.cboType.GetValue()+'('+str(self.spinLong.GetValue())+') ' + ' '+ null
		sql =sql +self.cboAfter.GetValue()+' '+self.cboFields.GetValue()+';'
		print(sql)

		n = self.controller.execute_sql(sql, self.db)
		if n == None:
			wx.MessageBox("Column create", 'Info',wx.OK | wx.ICON_INFORMATION)
			self.Close()
		else:
			wx.MessageBox(str(n), 'Info',wx.OK | wx.ICON_INFORMATION)

	def columns_from_table(self):
		rows = self.controller.get_columns_from_table(self.table, self.db)
		self.cboFieldsChoices = []
		for row in rows:
			self.cboFieldsChoices.append(row[0])
		
		print(self.cboFieldsChoices)

class edit_column ( wx.Dialog ):
	controller = Controller()

	def __init__( self, parent, table, db ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Edit column", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		self.table = table
		self.db = db 

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Field Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		gSizer1.Add( self.m_staticText1, 0, wx.ALL, 5 )

		self.columns_from_table()
		self.cboColumns = wx.ComboBox( self, wx.ID_ANY, self.cboFieldsChoices[0], wx.DefaultPosition, wx.DefaultSize, self.cboFieldsChoices, 0 )
		gSizer1.Add( self.cboColumns, 0, wx.ALL, 5 )

		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Type", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )

		gSizer1.Add( self.m_staticText3, 0, wx.ALL, 5 )

		cboTypeChoices =  [ u"varchar", u"integer", u"boolean", u"date" ]
		self.cboType = wx.ComboBox( self, wx.ID_ANY, 'varchar', wx.DefaultPosition, wx.DefaultSize, cboTypeChoices, 0 )
		gSizer1.Add( self.cboType, 0, wx.ALL, 5 )

		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Long", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )

		gSizer1.Add( self.m_staticText4, 0, wx.ALL, 5 )

		self.spinLong = wx.SpinCtrl( self, wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 255, 10 )
		gSizer1.Add( self.spinLong, 0, wx.ALL, 5 )

		self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Default", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText5.Wrap( -1 )

		gSizer1.Add( self.m_staticText5, 0, wx.ALL, 5 )

		self.txtDefault = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.txtDefault, 0, wx.ALL, 5 )

		self.checknull = wx.CheckBox( self, wx.ID_ANY, u"Not Null", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.checknull, 0, wx.ALL, 5 )

		self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )

		gSizer1.Add( self.m_staticText7, 0, wx.ALL, 5 )

		cboAfterChoices = [ u"Before", u"After" ]
		self.cboAfter = wx.ComboBox( self, wx.ID_ANY, u"After", wx.DefaultPosition, wx.DefaultSize, cboAfterChoices, 0 )
		self.cboAfter.SetSelection( 0 )
		gSizer1.Add( self.cboAfter, 0, wx.ALL, 5 )
		
		test = []
		self.cboFields = wx.ComboBox( self, wx.ID_ANY, '' , wx.DefaultPosition, wx.DefaultSize, test , 0 )
		gSizer1.Add( self.cboFields, 0, wx.ALL, 5 )

		self.btnAdd = wx.Button( self, wx.ID_ANY, u"Edit", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.btnAdd, 0, wx.ALL, 5 )

		bSizer1.Add( gSizer1, 1, wx.EXPAND, 5 )

		self.SetSizer( bSizer1 )
		self.Layout()
		bSizer1.Fit( self )

		self.Centre( wx.BOTH )

		self.Bind(wx.EVT_BUTTON, self.addcolumns ,self.btnAdd )

		self.Bind(wx.EVT_COMBOBOX, self.datafield, self.cboColumns )

	def columns_from_table(self,column=''):
		rows = self.controller.get_columns_from_table(self.table, self.db)
		self.cboFieldsChoices = []
		
		if column == '':
			for row in rows:
				self.cboFieldsChoices.append(row[0])
		else:
			for row in rows:
				if row[0] == column:
					pass
				else:
					self.cboFieldsChoices.append(row[0])
	
	def addcolumns(self, evt):
		if self.checknull.GetValue() == True:
			null = ' Not null '
		else:
			null = ''

		sql = 'ALTER TABLE '+self.table+' ADD COLUMN '+self.txtFieldName.GetValue()
		sql = sql +' '+self.cboType.GetValue()+'('+str(self.spinLong.GetValue())+') ' + ' '+ null
		sql =sql +self.cboAfter.GetValue()+' '+self.cboFields.GetValue()+';'
		print(sql)

		n = self.controller.execute_sql(sql, self.db)
		if n == None:
			wx.MessageBox("Column create", 'Info',wx.OK | wx.ICON_INFORMATION)
			self.Close()
		else:
			wx.MessageBox(str(n), 'Info',wx.OK | wx.ICON_INFORMATION)

	def datafield(self, evt):
		self.checknull.SetValue(False)

		rows = self.controller.get_columns_from_table(self.table, self.db)
		#int(filter(str.isdigit, str1))
		for row in rows:
			if row[0] == self.cboColumns.GetValue():
				if row[2] == 'NO':
					self.checknull.SetValue(True)
				elif row[2] == 'YES': 
					self.checknull.SetValue(False)

				array = row[1].split('(')
				self.cboType.SetValue(array[0])

				array2 = str(array[1]).split(')')

				self.spinLong.SetValue(int(array2[0]))

				if row[4] != None:
					self.txtDefault.SetValue(str(row[4]))

				self.columns_from_table(row[0])
				self.cboFields.SetItems(self.cboFieldsChoices)

class remove_column ( wx.Dialog ):
	controller = Controller()
	def __init__(self, parent, db, table):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Remove column", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		self.table = table
		self.db = db

		gSizer2 = wx.GridSizer( 0, 2, 0, 0 )

		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"Column:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )

		gSizer2.Add( self.m_staticText8, 0, wx.ALL, 5 )

		self.columns_from_table()
		self.cboColumn = wx.ComboBox( self, wx.ID_ANY, self.cboFieldsChoices[1], wx.DefaultPosition, wx.DefaultSize, self.cboFieldsChoices, 0 )
		gSizer2.Add( self.cboColumn, 0, wx.ALL, 5 )

		self.btnRemove = wx.Button( self, wx.ID_ANY, u"Remove", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.btnRemove, 0, wx.ALL, 5 )


		self.SetSizer( gSizer2 )
		self.Layout()
		gSizer2.Fit( self )

		self.Centre( wx.BOTH )

		self.Bind(wx.EVT_BUTTON, self.del_column ,self.btnRemove )

	def del_column(self, evt):
		sql = 'ALTER TABLE '+self.table+' DROP COLUMN '+self.cboColumn.GetValue()+';'
		
		n = self.controller.execute_sql(sql, self.db)
		
		if n == None:
			wx.MessageBox("Column delete", 'Info',wx.OK | wx.ICON_INFORMATION)
			self.Close()
		else:
			wx.MessageBox(str(n), 'Info',wx.OK | wx.ICON_INFORMATION)

	def columns_from_table(self):
		rows = self.controller.get_columns_from_table(self.table, self.db)
		self.cboFieldsChoices = []
		for row in rows:
			self.cboFieldsChoices.append(row[0])

class Add_rows_dialog ( wx.Dialog ):

	controller = Controller()

	def __init__( self, parent, table, db ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Add rows", pos = wx.DefaultPosition, size = wx.Size( 451,258 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		self.table = table
		self.db = db

		self.values = []
		self.function()

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_scrolledWindow1 = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.m_scrolledWindow1.SetScrollRate( 5, 5 )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

		# ________________________________
		for key in self.keys:
			lbl = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, key , wx.DefaultPosition, wx.DefaultSize, 0 )
			lbl.Wrap( -1 )

			gSizer1.Add( lbl, 0, wx.ALL, 5 )

			txt = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
			gSizer1.Add( txt, 0, wx.ALL, 5 )
			
			self.values.append( txt )

		# ________________________________

		bSizer2.Add( gSizer1, 1, wx.EXPAND, 5 )

		self.m_panel2 = wx.Panel( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

		btnSave = wx.Button( self.m_panel2, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( btnSave, 0, wx.ALL, 5 )


		self.m_panel2.SetSizer( bSizer4 )
		self.m_panel2.Layout()
		bSizer4.Fit( self.m_panel2 )
		bSizer2.Add( self.m_panel2, 0, wx.EXPAND |wx.ALL, 5 )


		self.m_scrolledWindow1.SetSizer( bSizer2 )
		self.m_scrolledWindow1.Layout()
		bSizer2.Fit( self.m_scrolledWindow1 )
		bSizer1.Add( self.m_scrolledWindow1, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Bind(wx.EVT_BUTTON, self.save_data ,btnSave )

	def function(self):
		self.columns = self.controller.get_columns_from_table(self.table, self.db)

		self.keys = []

		for row in self.columns:
			self.keys.append(row[0])

		self.nums = len(self.keys)

	def save_data(self, evt):
		sql = 'insert into '+ self.table+'('
		
		for x in self.keys:
			sql = sql + x + ','
		sql = sql.rstrip(',') + ') values('

		for raw in range(0,self.nums):
			e = self.validacion(raw)
			if e == False:
				if self.values[raw].GetValue() == '':
					sql = sql + '0,'
				else:
					sql = sql + self.values[raw].GetValue() + ','
			else:
				sql = sql + '"' + self.values[raw].GetValue() + '"' +','

		sql = sql.rstrip(',') + ');'

		print( sql )
		n = self.controller.execute_sql(sql, self.db)
		
		if n == None:
			wx.MessageBox("Sucess", 'Info',wx.OK | wx.ICON_INFORMATION)
			self.Close()
		else:
			wx.MessageBox(str(n), 'Info',wx.OK | wx.ICON_INFORMATION)

	def validacion(self, campo=''):
		print(self.columns[campo][1])

		if str(self.columns[campo][1]).upper().count('INT') == 1:
			return False
		elif str(self.columns[campo][1]).upper().count('INTEGER') == 1:
			return False
		elif str(self.columns[campo][1]).upper().count('SMALLINT') == 1:
			return False
		elif str(self.columns[campo][1]).upper().count('TINYINT') == 1:
			return False
		else:
			return True

class Edit_rows_dialog ( wx.Dialog ):

	controller = Controller()

	def __init__( self, parent, table, db, array ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Add rows", pos = wx.DefaultPosition, size = wx.Size( 451,258 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		self.table = table
		self.db = db
		self.array = array

		self.values = []
		self.set_data_to_field()

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_scrolledWindow1 = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.m_scrolledWindow1.SetScrollRate( 5, 5 )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )

		gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

		x = 0

		# ________________________________
		for key in self.keys:
			lbl = wx.StaticText( self.m_scrolledWindow1, wx.ID_ANY, key , wx.DefaultPosition, wx.DefaultSize, 0 )
			lbl.Wrap( -1 )

			gSizer1.Add( lbl, 0, wx.ALL, 5 )

			if self.Primary_key == key:
				txt = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
			else:
				txt = wx.TextCtrl( self.m_scrolledWindow1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )

			gSizer1.Add( txt, 0, wx.ALL, 5 )

			txt.SetValue(array[x])

			x = x + 1
			
			self.values.append( txt )

		# ________________________________

		bSizer2.Add( gSizer1, 1, wx.EXPAND, 5 )

		self.m_panel2 = wx.Panel( self.m_scrolledWindow1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

		btnSave = wx.Button( self.m_panel2, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( btnSave, 0, wx.ALL, 5 )


		self.m_panel2.SetSizer( bSizer4 )
		self.m_panel2.Layout()
		bSizer4.Fit( self.m_panel2 )
		bSizer2.Add( self.m_panel2, 0, wx.EXPAND |wx.ALL, 5 )


		self.m_scrolledWindow1.SetSizer( bSizer2 )
		self.m_scrolledWindow1.Layout()
		bSizer2.Fit( self.m_scrolledWindow1 )
		bSizer1.Add( self.m_scrolledWindow1, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Bind(wx.EVT_BUTTON, self.update_data ,btnSave )

	def set_data_to_field(self):
		self.columns = self.controller.get_columns_from_table(self.table, self.db)

		self.keys = []
		y = 0
		for x in self.columns:
			self.keys.append( x[0] )
			if x[3] == 'PRI':
				self.Primary_key = x[0]
				self.id_value = self.array[y]

			if self.validacion(y) == False:
				self.type_key = False

			y = y + 1

		self.nums = len(self.keys)

	def validacion(self, campo=''):
		if str(self.columns[campo][1]).upper().count('INT') == 1:
			return False
		elif str(self.columns[campo][1]).upper().count('INTEGER') == 1:
			return False
		elif str(self.columns[campo][1]).upper().count('SMALLINT') == 1:
			return False
		elif str(self.columns[campo][1]).upper().count('TINYINT') == 1:
			return False
		else:
			return True

	def update_data(self, evt):
		sql = "update " + self.table + " set "
		
		it = 0
		for i in self.columns:
			if i[0] == self.Primary_key:
				it = it + 1
			else:
				if self.validacion(it) == True:
					sql = sql + ' ' + i[0] + '= "' + self.values[it].GetValue() + '" ,'
				else:
					sql = sql + ' ' + i[0] + '= ' + self.values[it].GetValue() + ' ,'

				it = it + 1

		sql = sql.rstrip(",")
		if self.type_key == False:
			sql = sql + " where " + self.Primary_key + "=" + str(self.id_value)
		else:
			sql = sql + " where " + self.Primary_key + '="' + str(self.id_value) + '"'

		print("_------------_")
		print(sql)
		n = self.controller.execute_sql(sql, self.db)
		print(n)
		
		if n == None:
			wx.MessageBox("Sucess", 'Info',wx.OK | wx.ICON_INFORMATION)
			self.Close()
		else:
			wx.MessageBox(str(n), 'Info',wx.OK | wx.ICON_INFORMATION)

class select_table_panel( wx.Panel ):
	"""docstring for select_table_panel"""

	controller = Controller()
	array_delete = []

	def __init__(self, parent, db, table):
		wx.Panel.__init__ ( self, parent=parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )

		self.table = table
		self.db = db

		bSizer12 = wx.BoxSizer( wx.VERTICAL )

		self.tool2 = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
		self.tool_add_row = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/row_add.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add", wx.EmptyString, None ) 
		self.tool_row_remove = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/row_remove.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Row remove", wx.EmptyString, None )
		self.tool_edit_row = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/row_edit.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Row edit", wx.EmptyString, None ) 
		self.tool2.AddSeparator()
		self.tool_column_add = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/column_add.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add new column", wx.EmptyString, None )
		self.tool_column_edit = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/column_edit.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Column edit", wx.EmptyString, None ) 
		self.tool_column_remove = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/column_remove.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Column remove", wx.EmptyString, None ) 
		self.tool2.AddSeparator() 
		self.tool_truncate = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/vaciar.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Truncate table", wx.EmptyString, None ) 
		self.tool_refresh = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons/refresh.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Truncate table", wx.EmptyString, None ) 
		
		self.tool2.Realize()
		
		bSizer12.Add( self.tool2, 0, wx.EXPAND, 5 )

		self.lista=wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		bSizer12.Add(self.lista, 1, wx.EXPAND)
		self.SetSizer( bSizer12 )
		self.Layout()

		self.list_data()

		self.Bind(wx.EVT_TOOL, self.truncate, self.tool_truncate)
		self.Bind(wx.EVT_TOOL, self.column_add ,self.tool_column_add )
		self.Bind(wx.EVT_TOOL, self.column_remove ,self.tool_column_remove )
		self.Bind(wx.EVT_TOOL, self.column_edit , self.tool_column_edit )

		self.Bind(wx.EVT_TOOL, self.edit_row , self.tool_edit_row )
		self.Bind(wx.EVT_TOOL, self.add_row , self.tool_add_row )
		self.Bind(wx.EVT_TOOL, self.delete_row , self.tool_row_remove)

		self.Bind(wx.EVT_TOOL, self.refresh_table, self.tool_refresh )

		self.Bind(wx.EVT_LIST_ITEM_SELECTED ,self.click, self.lista)

	def click(self,event):
		#print( "----------------" )

		x = 0
		for xy in self.columns:
			print(self.lista.GetItemText(event.GetIndex(),x))
			self.array_delete.append( self.lista.GetItemText(event.GetIndex(),x) )
			x = x + 1



		#self.lista.DeleteItem(event.GetIndex())
		#print( "----------------" )

	def refresh_table(self, evt):
		self.lista.ClearAll()
		self.list_data()

	def delete_row(self, evt):
		#self.columns
		y = 0
		sql = 'DELETE FROM ' + self.table + ' WHERE '
		for x in self.columns:
			if self.validacion(y) == False:
				sql = sql + str(self.columns[y][0]) + '=' +  str(self.array_delete[y]) + ' AND '
			else:
				sql = sql + str(self.columns[y][0]) + '="' +  str(self.array_delete[y]) + '" AND '
			y=y+1

		sql = sql.rstrip(' AND ') + ';'
		# DELETE FROM test2 WHERE id=3 AND name="Jose" AND email="jose@gmail.com" AND country="Mexico" AND direction="Buss";
		# DELETE FROM test1 WHERE id=4 AND name="Martin";
		print( sql )

		r = self.controller.execute_sql(sql , self.db)
		if r == None:
			wx.MessageBox("Eliminado", 'Info',wx.OK | wx.ICON_INFORMATION)
			self.Close()
		else:
			wx.MessageBox(str(r), 'Info',wx.OK | wx.ICON_INFORMATION)

		self.lista.ClearAll()
		self.list_data()

	def validacion(self, campo=''):
		if str(self.columns[campo][1]).upper().count('INT') == 1:
			return False
		elif str(self.columns[campo][1]).upper().count('INTEGER') == 1:
			return False
		elif str(self.columns[campo][1]).upper().count('SMALLINT') == 1:
			return False
		elif str(self.columns[campo][1]).upper().count('TINYINT') == 1:
			return False
		else:
			return True

	def list_data(self):
		rows = self.controller.get_columns_from_table(self.table, self.db)
		self.columns = rows
		c = 0
		for row in rows:
			if c == 0:
				self.primera_columna_db = str(row[0])
			self.lista.InsertColumn(c, row[0])
			c = c+1

		rows = ''
		rows = self.controller.get_data(self.table,self.db)

		arreglo = []
		for row in rows:
			arreglo.append(row)

		for ar in arreglo:
			index = self.lista.InsertStringItem(sys.maxsize, str(ar[0]))
			for er in range(1,c):
				self.lista.SetStringItem(index, er, str(ar[er]))

	def add_row(self, event):
		NewBD = Add_rows_dialog(self, self.table, self.db)
		NewBD.ShowModal()
		NewBD.Destroy()

		self.lista.ClearAll()
		self.list_data()

	def edit_row(self, evt):
		NewBD = Edit_rows_dialog(self, self.table, self.db, self.array_delete)
		NewBD.ShowModal()
		NewBD.Destroy()

		self.lista.ClearAll()
		self.list_data()

	def truncate(self, evt):
		r = self.controller.execute_sql("truncate table "+ self.table , self.db)
		if r == None:
			wx.MessageBox("Truncate", 'Info',wx.OK | wx.ICON_INFORMATION)
			self.Close()
		else:
			wx.MessageBox(str(r), 'Info',wx.OK | wx.ICON_INFORMATION)

	def column_remove(self, evt):
		NewBD = remove_column(self, self.db, self.table)
		NewBD.ShowModal()
		NewBD.Destroy()

		self.lista.ClearAll()
		self.list_data()

	def column_add(self, evt):
		NewBD = add_new_column(self, self.table, self.db)
		NewBD.ShowModal()
		NewBD.Destroy()

		self.lista.ClearAll()
		self.list_data()

	def column_edit(self, evt):
		NewBD = edit_column(self, self.table, self.db)
		NewBD.ShowModal()
		NewBD.Destroy()

		self.lista.ClearAll()
		self.list_data()

class describe_table_panel( wx.Panel ):
	controller = Controller()

	def __init__(self, parent, db, table):
		wx.Panel.__init__ ( self, parent=parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )

		self.table = table
		self.db = db

		bSizer12 = wx.BoxSizer( wx.VERTICAL )
		id=wx.NewId()
		self.lista=wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		bSizer12.Add(self.lista, 1, wx.EXPAND)
		self.SetSizer( bSizer12 )
		self.Layout()

		self.list_data()

	def list_data(self):
		self.lista.InsertColumn(0, "Field")
		self.lista.InsertColumn(1, "Type")
		self.lista.InsertColumn(2, "Null")
		self.lista.InsertColumn(3, "Key")
		self.lista.InsertColumn(4, "Default")
		self.lista.InsertColumn(5, "Extra")

		rows = self.controller.get_columns_from_table(self.table, self.db)
		print(rows)
		#print(len(rows))
		
		for row in rows:
			index = self.lista.InsertStringItem(sys.maxsize, str(row[0]))
			for er in range(1,len(rows)):
				self.lista.SetStringItem(index, er, str(row[er]))

class about_panel( wx.Panel ):
	controller = Controller()

	def __init__(self, parent ):
		wx.Panel.__init__ ( self, parent=parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )

		bSizer15 = wx.BoxSizer( wx.VERTICAL )

		self.m_scrolledWindow2 = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.m_scrolledWindow2.SetScrollRate( 5, 5 )
		bSizer16 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText21 = wx.StaticText( self.m_scrolledWindow2, wx.ID_ANY, u"WXDBManager", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
		self.m_staticText21.Wrap( -1 )

		self.m_staticText21.SetFont( wx.Font( 20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Arial Black" ) )

		bSizer16.Add( self.m_staticText21, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_bitmap2 = wx.StaticBitmap( self.m_scrolledWindow2, wx.ID_ANY, wx.Bitmap( u"icons/wxdbmanager_232x232.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer16.Add( self.m_bitmap2, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_staticText22 = wx.StaticText( self.m_scrolledWindow2, wx.ID_ANY, u"Un administrador de base de datos para mysql\ndiseñado con wxpython y conector mysql.", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
		self.m_staticText22.Wrap( -1 )

		bSizer16.Add( self.m_staticText22, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_staticText23 = wx.StaticText( self.m_scrolledWindow2, wx.ID_ANY, u"Version: 1.0", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
		self.m_staticText23.Wrap( -1 )

		self.m_staticText23.SetFont( wx.Font( 12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Arial" ) )

		bSizer16.Add( self.m_staticText23, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_hyperlink4 = wx.adv.HyperlinkCtrl( self.m_scrolledWindow2, wx.ID_ANY, u"Repositorio", u"https://github.com/jucarhev/wxdbmanager", wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_ALIGN_CENTRE|wx.adv.HL_DEFAULT_STYLE )
		bSizer16.Add( self.m_hyperlink4, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		bSizer17 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_bitmap3 = wx.StaticBitmap( self.m_scrolledWindow2, wx.ID_ANY, wx.Bitmap( u"icons/024-github.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.m_bitmap3, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_hyperlink1 = wx.adv.HyperlinkCtrl( self.m_scrolledWindow2, wx.ID_ANY, u"Github", u"https://github.com/", wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
		bSizer17.Add( self.m_hyperlink1, 0, wx.ALL, 5 )

		self.m_bitmap4 = wx.StaticBitmap( self.m_scrolledWindow2, wx.ID_ANY, wx.Bitmap( u"icons/022-mysql.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.m_bitmap4, 0, wx.ALL, 5 )

		self.m_hyperlink2 = wx.adv.HyperlinkCtrl( self.m_scrolledWindow2, wx.ID_ANY, u"MySQL", u"https://www.mysql.com/", wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
		bSizer17.Add( self.m_hyperlink2, 0, wx.ALL, 5 )

		self.m_bitmap5 = wx.StaticBitmap( self.m_scrolledWindow2, wx.ID_ANY, wx.Bitmap( u"icons/023-python.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.m_bitmap5, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_hyperlink3 = wx.adv.HyperlinkCtrl( self.m_scrolledWindow2, wx.ID_ANY, u"Python", u"https://www.python.org/", wx.DefaultPosition, wx.DefaultSize, wx.adv.HL_DEFAULT_STYLE )
		bSizer17.Add( self.m_hyperlink3, 0, wx.ALL, 5 )


		bSizer16.Add( bSizer17, 0, wx.ALL|wx.EXPAND, 5 )


		self.m_scrolledWindow2.SetSizer( bSizer16 )
		self.m_scrolledWindow2.Layout()
		bSizer16.Fit( self.m_scrolledWindow2 )
		bSizer15.Add( self.m_scrolledWindow2, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer15 )
		self.Layout()

class console_panel( wx.Panel ):

	controller = Controller()

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer16 = wx.BoxSizer( wx.VERTICAL )

		self.m_toolBar1 = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
		self.m_tool1 = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons/play-button.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_tool2 = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons/broom.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.m_toolBar1.Realize()

		bSizer16.Add( self.m_toolBar1, 0, wx.EXPAND, 5 )

		self.m_textCtrl14 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		bSizer16.Add( self.m_textCtrl14, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_listCtrl1 = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		bSizer16.Add( self.m_listCtrl1, 0, wx.ALL|wx.EXPAND, 5 )

		self.showMessage = wx.StaticText( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.showMessage.Wrap( -1 )

		bSizer16.Add( self.showMessage, 0, wx.ALL, 5 )


		self.SetSizer( bSizer16 )
		self.Layout()

		self.Bind(wx.EVT_TOOL, self.get_query, self.m_tool1)
		self.Bind(wx.EVT_TOOL, self.clean, self.m_tool2)

	def get_query(self, evt):
		sql =  self.m_textCtrl14.GetValue()
		self.controller.variable_connection()
		database = ''

		array = sql.split(';')
		if array[0].upper().count("USE") == 1:
			array2 = str(array[0]).split(' ')
			database = array2[1]
		
		for row in array:
			if str(row).upper().count("SHOW") == 1 or str(row).upper().count("SELECT") == 1:
				self.get_list_data(database, row)
			else:
				print(row)
				n = self.controller.execute_sql(row,database)

				if n == None:
					self.showMessage.SetLabel("Sucess")
				else:
					self.showMessage.SetLabel(str(n))

	def get_list_data(self, database, row):
		if row.upper().count("SHOW TABLES") == 1:
			self.m_listCtrl1.ClearAll()
			self.m_listCtrl1.InsertColumn(0, "Tables")
			self.print_data(1, row, database)
		if row.upper().count("SHOW COLUMNS FROM ") == 1:
			self.m_listCtrl1.ClearAll()
			self.list_data1(row, database)
		elif row.upper().count("SHOW DATABASES") == 1 or row.upper().count("SHOW SCHEMAS") == 1:
			self.m_listCtrl1.ClearAll()
			self.m_listCtrl1.InsertColumn(0, "Databases")
			self.print_data(1, row, database)
		elif row.upper().count("SELECT * FROM ") == 1:
			sql = row.split(' ')
			if sql[1] == '*':
				self.select( row, database )
			else:
				self.select( row, database, False )
		elif check(row) == 1:
			print(row)
		else:
			self.select( row, database, False )

	def check(self, row):
		datos = [ 'CREATE', 'UPDATE', 'DELETE', 'INSERT', 'ALTER', 'DELIMITER', 'CHECK', 'LOAD' ]
		for x in datos:
			if row.upper().count(x) == 1:
				return 1


	def print_data(self, c, row, database):
		rows2 = ''
		rows2 = self.controller.return_data(row, database)
		#print(rows2)

		try:
			arreglo = []
			for row in rows2:
				arreglo.append(row)

			for ar in arreglo:
				index = self.m_listCtrl1.InsertStringItem(sys.maxsize, str(ar[0]))
				for er in range(1,c):
					self.m_listCtrl1.SetStringItem(index, er, str(ar[er]))
		except Exception as e:
			print( rows2 )
			self.showMessage.SetLabel( str(rows2) )
		
	def list_data1(self, row, database):
		rows = row.split(' ')
		table = rows[3]

		self.m_listCtrl1.InsertColumn(0, "Field")
		self.m_listCtrl1.InsertColumn(1, "Type")
		self.m_listCtrl1.InsertColumn(2, "Null")
		self.m_listCtrl1.InsertColumn(3, "Key")
		self.m_listCtrl1.InsertColumn(4, "Default")
		self.m_listCtrl1.InsertColumn(5, "Extra")

		rows = self.controller.get_columns_from_table(table, database)
		
		for row in rows:
			index = self.m_listCtrl1.InsertStringItem(sys.maxsize, str(row[0]))
			for er in range(1,len(rows)):
				self.m_listCtrl1.SetStringItem(index, er, str(row[er]))

	def select(self, sql, database, columns=True ):
		self.m_listCtrl1.ClearAll()
		table = ''
		try:
			if columns == True:
				array = sql.split(' ')
				table = array[3] 
				self.list_data(table, database )
			else:
				self.lista_data2(sql, database )


		except Exception as e:
			raise e

	def list_data(self, table, db):
		rows = self.controller.get_columns_from_table(table, db)
		self.columns = rows
		c = 0
		for row in rows:
			if c == 0:
				self.primera_columna_db = str(row[0])
			self.m_listCtrl1.InsertColumn(c, row[0])
			c = c+1

		rows = ''
		rows = self.controller.get_data(table,db)

		arreglo = []
		for row in rows:
			arreglo.append(row)

		for ar in arreglo:
			index = self.m_listCtrl1.InsertStringItem(sys.maxsize, str(ar[0]))
			for er in range(1,c):
				self.m_listCtrl1.SetStringItem(index, er, str(ar[er]))

	def lista_data2(self, sql, database):
		rows = self.controller.return_data(sql, database)
		sql = sql.replace( "select ",'SELECT ').replace( 'SELECT ', '')
		sql = sql.replace( " from ",' FROM ').replace( ' FROM ', '_____')

		array = sql.split('_____')

		c = 0
		for x in array[0].split(','):
			self.m_listCtrl1.InsertColumn(c, x)
			c = c + 1

		arreglo = []
		for row in rows:
			arreglo.append(row)

		for ar in arreglo:
			index = self.m_listCtrl1.InsertStringItem(sys.maxsize, str(ar[0]))
			for er in range(1,c):
				self.m_listCtrl1.SetStringItem(index, er, str(ar[er]))

	def clean(self, evt):
		self.m_listCtrl1.ClearAll()
		self.m_textCtrl14.SetValue('')

app = wx.App()
main(None)
app.MainLoop()