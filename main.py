# -*- coding: utf-8 -*- 

import wx
import wx.xrc
import wx.aui
import sys, os

from controller import Controller


class main ( wx.Frame ):
	""" Principal class """

	controller = Controller()

	List_tables = []

	is_connect = False
	database_old_selected = ''
	
	def __init__( self, parent ):

		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		path = os.path.abspath("./icons/wxdbmanager_32x32.png")
		icon = wx.Icon(path, wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)

		self.check_connection()
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menubar1.Append( self.m_menu1, u"File" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		self.m_toolBar1 = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY ) 
		self.Connection_tool = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons/025-settings-1.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.m_toolBar1.Realize() 
		
		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.tree = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE )
		bSizer1.Add( self.tree, 1, wx.ALL|wx.EXPAND, 5 )

		self.add_items_tree()

		self.notebook = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE )
		self.m_panel1 = wx.Panel( self.notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		
		bSizer1.Add( self.notebook, 5, wx.EXPAND |wx.ALL, 5  )
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		self.SetSize((800,600))
		self.SetTitle("WxDBManager")
		self.Show()

		self.Bind(wx.EVT_TOOL,self.conection_manager,self.Connection_tool)

	def check_connection(self):
		print("# Verificanco conexion")
		m = self.controller.check_conn()
		if m == 1:
			#wx.MessageBox("ok", 'Info',wx.OK | wx.ICON_INFORMATION)
			print("Ok")
			self.is_connect = True
		else:
			wx.MessageBox(str(m), 'Info',wx.OK | wx.ICON_INFORMATION)

	def conection_manager(self, evt):
		NewBD = Dialog_Connection(self)
		NewBD.ShowModal()
		NewBD.Destroy()

	# =====> TREE
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

	def OnSelChanged(self,event):
		#print(self.database_old_selected)
		items =  event.GetItem()
		db_nodo = self.tree.GetItemText(items)

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
				self.option_menu = ['Select','Edit','Truncate','Add','Drop Table','Describe']
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
			self.notebook.AddPage( select_table_panel(self.notebook, self.database_active, self.table_active), u"Select Table")
		
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
			pass

		elif item == 'New Table':
			NewBD = new_table_dialog(self, self.database_active)
			NewBD.ShowModal()
			NewBD.Destroy()

			self.tree.DeleteChildren(self.items_database_list.get(self.database_active))
			self.add_tables_nodo(self.items_database_list.get(self.database_active), self.database_active)

		elif item == 'Edit':
			pass

		elif item == 'Truncate':
			pass

		elif item == 'Describe':
			pass

		elif item == 'Add':
			pass

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

class select_table_panel(wx.Panel):
	"""docstring for select_table_panel"""

	controller = Controller()

	def __init__(self, parent, db, table):
		wx.Panel.__init__ ( self, parent=parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )

		self.table = table
		self.db = db

		bSizer12 = wx.BoxSizer( wx.VERTICAL )

		self.tool2 = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
		self.tool_add_row = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/row_add.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add", wx.EmptyString, None ) 
		self.f1 = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/row_remove.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add", wx.EmptyString, None )
		self.f4 = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/row_edit.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add", wx.EmptyString, None ) 
		self.tool2.AddSeparator()
		self.f2 = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/column_add.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add", wx.EmptyString, None )
		self.f3 = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/column_edit.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add", wx.EmptyString, None ) 
		self.f4 = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/column_remove.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add", wx.EmptyString, None ) 
		self.tool2.AddSeparator() 
		self.f4 = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons_db/icons_32x32_png/vaciar.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add", wx.EmptyString, None ) 
		
		self.tool2.Realize()
		
		bSizer12.Add( self.tool2, 0, wx.EXPAND, 5 )

		id=wx.NewId()
		self.lista=wx.ListCtrl(self,id,style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		bSizer12.Add(self.lista, 1, wx.EXPAND)
		self.SetSizer( bSizer12 )
		self.Layout()

		self.list_data()

		self.Bind(wx.EVT_TOOL, self.add_row, self.tool_add_row)

	def list_data(self):
		rows = self.controller.get_columns_from_table(self.table, self.db)
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
		pass

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

app = wx.App()
main(None)
app.MainLoop()
