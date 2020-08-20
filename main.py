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

		path = os.path.abspath("./img/logo_db.png")
		icon = wx.Icon(path, wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)

		self.check_connection()
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menubar1.Append( self.m_menu1, u"File" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		self.m_toolBar1 = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY ) 
		self.Connection_tool = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"img/db.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
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
		img_database = image_list.Add(wx.Image("img/database.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())
		self.img_table    = image_list.Add(wx.Image("img/table.png", wx.BITMAP_TYPE_PNG).Scale(16,16).ConvertToBitmap())

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
		items =  event.GetItem()
		db_nodo = self.tree.GetItemText(items)

		if db_nodo != 'Databases':
			if self.check_is_database(items) == 1:
				self.database_active = db_nodo
				#print(db_nodo)
				if self.database_old_selected == '':
					self.database_old_selected = db_nodo
					self.object_item = self.items_database_list.get(db_nodo)
				else:
					self.database_old_selected = db_nodo
					self.tree.DeleteChildren(self.object_item)
					self.object_item = self.items_database_list.get(db_nodo)

				if self.database_active != '':
					self.add_tables_nodo(self.items_database_list.get(db_nodo), self.tree.GetItemText(items))
					#print(self.List_tables)
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
		print("=============> OnPopupItemSelected")
		item = self.popupmenu.GetLabel(event.GetId())

		if item == 'Select':
			self.notebook.AddPage( select_table_panel(self.notebook, self.database_active, self.table_active), u"Select Table")



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

class select_table_panel(wx.Panel):
	"""docstring for select_table_panel"""

	controller = Controller()

	def __init__(self, parent, db, table):
		wx.Panel.__init__ ( self, parent=parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )

		self.table = table
		self.db = db
		bSizer12 = wx.BoxSizer( wx.VERTICAL )

		self.tool2 = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
		self.tool_add_row = self.tool2.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"img/png/002-anadir.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Add", wx.EmptyString, None ) 
		
		self.tool2.Realize()
		
		bSizer12.Add( self.tool2, 0, wx.EXPAND, 5 )

		id=wx.NewId()
		self.lista=wx.ListCtrl(self,id,style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		bSizer12.Add(self.lista, 1, wx.EXPAND)
		self.SetSizer( bSizer12 )
		self.Layout()

app = wx.App()
main(None)
app.MainLoop()
