#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 20:51:25 2019

@author: zoli
"""    

import sys, os, pyqtgraph, PIL, io, cStringIO
import pyqtgraph.exporters as exp
from PyQt4 import QtGui, QtCore
from Modules import database, system_vars, stackup_functions, global_vars, genrep

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


def find_sid(name, namelist):
    lenght = len(namelist)
    for i in range(lenght):
        if name == namelist[i][1].decode('unicode-escape'):
            return int(namelist[i][0])

def resize_img(img_path, width, heigth):
    img = PIL.Image.open(img_path)
    img.thumbnail((width, heigth), PIL.Image.ANTIALIAS)
    stream = io.BytesIO()
    img.save(stream, format="PNG")
    return stream
                

class MainWindow(QtGui.QMainWindow):
    rowData = []
    rowDataS = []
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setFixedSize(1500, 1000)
        self.setWindowTitle("PyTol - Tolerance Stack-Up")
        self.setWindowIcon(QtGui.QIcon("../PyTol/Resources/bell_curve_icon_128.png"))
        self.center()
        self.statusBar()
        
# Toolbar
        
        aboutAction = QtGui.QAction(QtGui.QIcon("../PyTol/Resources/help-about-3.png"),"About", self)
        aboutAction.setStatusTip('About')
        aboutAction.setShortcut("F1")
        aboutAction.triggered.connect(self.about)
        
        openAction = QtGui.QAction(QtGui.QIcon("../PyTol/Resources/document-open-7.png"),"Open", self)
        openAction.setIconText("Open")
        openAction.setShortcut("Ctrl+O")
        openAction.setStatusTip('Open database')
        openAction.triggered.connect(self.file_open)
        
        newAction = QtGui.QAction(QtGui.QIcon("../PyTol/Resources/document-new-7.png"),"New", self)
        newAction.setIconText("New")
        newAction.setShortcut("Ctrl+N")
        newAction.setStatusTip('New database')
        newAction.triggered.connect(self.file_new)
        
        self.printAction = QtGui.QAction(QtGui.QIcon("../PyTol/Resources/document-print-2.png"),"New", self)
        self.printAction.setIconText("Print")
        self.printAction.setShortcut("Ctrl+P")
        self.printAction.setStatusTip('Print document')
        self.printAction.triggered.connect(self.print_report)
        self.printAction.setEnabled(False)
        
        self.pdfAction = QtGui.QAction(QtGui.QIcon("../PyTol/Resources/acroread-2.png"),"New", self)
        self.pdfAction.setIconText("Save Pdf")
        #pdfAction.setShortcut("Ctrl+Shift+N")
        self.pdfAction.setStatusTip('Create pdf')
        self.pdfAction.triggered.connect(self.save_report)
        self.pdfAction.setEnabled(False)
        
        
        self.toolbar = QtGui.QToolBar(self)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.toolbar.setIconSize(QtCore.QSize(20, 20))
        self.toolbar.setMovable(False)
        self.toolbar.resize(1500,50)
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(newAction)
        self.toolbar.addAction(self.printAction)
        self.toolbar.addAction(self.pdfAction)
        self.toolbar.addAction(aboutAction)

        
# Window elements for List
        
        self.btnNewComp = QtGui.QPushButton("New comp", self)
        self.btnNewComp.resize(90, 27)
        self.btnNewComp.move(20, 50)
        self.btnNewComp.setIcon(QtGui.QIcon("../PyTol/Resources/brick-add.png"))
        self.btnNewComp.clicked.connect(self.add_new_comp)
        self.btnNewComp.setEnabled(False)
        
        self.btnEditComp = QtGui.QPushButton("Ren. comp", self)
        self.btnEditComp.resize(90, 27)
        self.btnEditComp.move(115, 50)
        self.btnEditComp.setIcon(QtGui.QIcon("../PyTol/Resources/brick-edit.png"))
        self.btnEditComp.clicked.connect(self.edit_part)
        self.btnEditComp.setEnabled(False)
        
        self.btnNewDim = QtGui.QPushButton("New dim", self)
        self.btnNewDim.resize(90, 27)
        self.btnNewDim.move(510, 50)
        self.btnNewDim.setIcon(QtGui.QIcon("../PyTol/Resources/table-add.png"))
        self.btnNewDim.clicked.connect(self.add_new_dim)
        self.btnNewDim.setEnabled(False)
        
        self.btnEditDim = QtGui.QPushButton("Edit dim", self)
        self.btnEditDim.resize(90, 27)
        self.btnEditDim.move(605, 50)
        self.btnEditDim.setIcon(QtGui.QIcon("../PyTol/Resources/table-edit.png"))
        self.btnEditDim.clicked.connect(self.edit_dim)
        self.btnEditDim.setEnabled(False)
        
        self.cmbPartList = QtGui.QComboBox(self)
        self.cmbPartList.resize(675, 27)
        self.cmbPartList.move(20, 80)
        self.cmbPartList.activated[str].connect(self.part_change)
        
        tbl1Headers = ["Dim_ID",
                      "Description",
                      "Nom.",
                      "+Tol.",
                      "-Tol.",
                      "Comment"]
        self.tblDimList = QtGui.QTableWidget(self)
        self.tblDimList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblDimList.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblDimList.resize(675, 330)
        self.tblDimList.move(20, 115)
        self.tblDimList.setRowCount(0)
        self.tblDimList.setColumnCount(6)
        self.tblDimList.setHorizontalHeaderLabels(tbl1Headers)
        self.tblDimList.setColumnHidden(0, True)
        self.tblDimList.setColumnWidth(1, 300)
        self.tblDimList.setColumnWidth(2, 50)
        self.tblDimList.setColumnWidth(3, 50)
        self.tblDimList.setColumnWidth(4, 50)
        self.tblDimList.horizontalHeader().setStretchLastSection(True)
        self.tblDimList.cellClicked.connect(self.cellClick)
        
# Window elements for stack    
        
        self.btnNewStack = QtGui.QPushButton("New stack", self)
        self.btnNewStack.resize(90, 27)
        self.btnNewStack.move(805, 50)
        self.btnNewStack.setIcon(QtGui.QIcon("../PyTol/Resources/database-add.png"))
        self.btnNewStack.clicked.connect(self.add_new_stack)
        self.btnNewStack.setEnabled(False)
        
        self.btnEditStack = QtGui.QPushButton("Edit stack", self)
        self.btnEditStack.resize(90, 27)
        self.btnEditStack.move(900, 50)
        self.btnEditStack.setIcon(QtGui.QIcon("../PyTol/Resources/database-edit.png"))
        self.btnEditStack.clicked.connect(self.edit_stack)
        self.btnEditStack.setEnabled(False)
        
        self.btnDelStack = QtGui.QPushButton("Del stack", self)
        self.btnDelStack.resize(90, 27)
        self.btnDelStack.move(995, 50)
        self.btnDelStack.setIcon(QtGui.QIcon("../PyTol/Resources/database-delete.png"))
        self.btnDelStack.clicked.connect(self.del_stack)
        self.btnDelStack.setEnabled(False)
        
        self.btnEdStackDim = QtGui.QPushButton("Edit entry", self)
        self.btnEdStackDim.resize(90, 27)
        self.btnEdStackDim.move(1090, 50)
        self.btnEdStackDim.setIcon(QtGui.QIcon("../PyTol/Resources/table-edit.png"))
        self.btnEdStackDim.clicked.connect(self.edit_stack_entry)
        self.btnEdStackDim.setEnabled(False)
        
        self.btnMoveToStack = QtGui.QPushButton(self)
        self.btnMoveToStack.resize(30, 30)
        self.btnMoveToStack.move(735, 230)
        self.btnMoveToStack.setIcon(QtGui.QIcon("../PyTol/Resources/arrow-right-double.png"))
        self.btnMoveToStack.clicked.connect(self.move_to_stack)
        self.btnMoveToStack.setEnabled(False)
        
        self.btnRemoveFromStack = QtGui.QPushButton(self)
        self.btnRemoveFromStack.resize(30, 30)
        self.btnRemoveFromStack.move(735, 270)
        self.btnRemoveFromStack.setIcon(QtGui.QIcon("../PyTol/Resources/arrow-left-double.png"))
        self.btnRemoveFromStack.clicked.connect(self.remove_from_stack)
        self.btnRemoveFromStack.setEnabled(False)
        
        self.cmbStackList = QtGui.QComboBox(self)
        self.cmbStackList.resize(675, 27)
        self.cmbStackList.move(805, 80)
        self.cmbStackList.activated[str].connect(self.stack_change)
        
        tbl2Headers = ["Dim_ID",
                      "Coef.",
                      "Description",
                      "Nom.",
                      "+Tol.",
                      "-Tol.",
                      "Dim. Max",
                      "Dim. Min",
                      "Dist."]
        self.tblStackDimList = QtGui.QTableWidget(self)
        self.tblStackDimList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblStackDimList.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblStackDimList.resize(675, 330)
        self.tblStackDimList.move(805, 115)
        self.tblStackDimList.setRowCount(0)
        self.tblStackDimList.setColumnCount(9)
        self.tblStackDimList.setHorizontalHeaderLabels(tbl2Headers)
        self.tblStackDimList.setColumnHidden(0, True)
        self.tblStackDimList.setColumnWidth(1, 35)
        self.tblStackDimList.setColumnWidth(2, 300)
        self.tblStackDimList.setColumnWidth(3, 45)
        self.tblStackDimList.setColumnWidth(4, 45)
        self.tblStackDimList.setColumnWidth(5, 45)
        self.tblStackDimList.setColumnWidth(6, 62)
        self.tblStackDimList.setColumnWidth(7, 62)
        self.tblStackDimList.horizontalHeader().setStretchLastSection(True)
        self.tblStackDimList.cellClicked.connect(self.cellClickS)
        
#Window elements for results        
        
        self.setStyleSheet("QGroupBox\n"
                           "{\n"
                           "     border: 1px solid gray;\n"
                           "    margin-top: 0.5em;\n"
                           "}\n"
                           "\n"
                           "QGroupBox::title {\n"
                           "    top: -8px;\n"
                           "    left: 10px;\n"
                           "}")
        
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.resize(675,510)
        self.groupBox.move(805,460)
        self.groupBox.setTitle("Results")
        self.labelnom = QtGui.QLabel(self.groupBox)
        self.labelnom.resize(100, 27)
        self.labelnom.move(20,20)
        self.labelnom.setText("Nominal:")
        self.nominal = QtGui.QLineEdit(self.groupBox)
        self.nominal.resize(50,27)
        self.nominal.move(75,20)
        self.nominal.setReadOnly(True)
        self.labeltolp = QtGui.QLabel(self.groupBox)
        self.labeltolp.resize(100, 27)
        self.labeltolp.move(150,20)
        self.labeltolp.setText("Upper deviation:")
        self.tolp = QtGui.QLineEdit(self.groupBox)
        self.tolp.resize(50,27)
        self.tolp.move(250,20)
        self.tolp.setReadOnly(True)
        self.labeltolm = QtGui.QLabel(self.groupBox)
        self.labeltolm.resize(100, 27)
        self.labeltolm.move(320,20)
        self.labeltolm.setText("Lower deviation:")
        self.tolm = QtGui.QLineEdit(self.groupBox)
        self.tolm.resize(50,27)
        self.tolm.move(420,20)
        self.tolm.setReadOnly(True)
        self.labelconf = QtGui.QLabel(self.groupBox)
        self.labelconf.resize(110, 27)
        self.labelconf.move(495,20)
        self.labelconf.setText("Confidence interval:")
        self.conf = QtGui.QLineEdit(self.groupBox)
        self.conf.resize(50,27)
        self.conf.move(610,20)
        self.conf.setReadOnly(True)
        self.labeldate = QtGui.QLabel(self.groupBox)
        self.labeldate.resize(55, 27)
        self.labeldate.move(20,485)
        self.labeldate.setText("Rev. date:")
        self.labelrevdate = QtGui.QLabel(self.groupBox)
        self.labelrevdate.resize(70, 27)
        self.labelrevdate.move(80,485)
        self.labelauth = QtGui.QLabel(self.groupBox)
        self.labelauth.resize(50, 27)
        self.labelauth.move(160,485)
        self.labelauth.setText("Author:")
        self.authname = QtGui.QLabel(self.groupBox)
        self.authname.resize(200, 27)
        self.authname.move(210,485)
        
        self.groupBox1 = QtGui.QGroupBox(self.groupBox)
        self.groupBox1.resize(200,120)
        self.groupBox1.move(20,50)
        self.groupBox1.setTitle("Worst Case")
        self.labelmaxdim = QtGui.QLabel(self.groupBox1)
        self.labelmaxdim.resize(120, 27)
        self.labelmaxdim.move(10,20)
        self.labelmaxdim.setText("Maximum dimension:")
        self.maxdim = QtGui.QLineEdit(self.groupBox1)
        self.maxdim.resize(50, 27)
        self.maxdim.move(135,20)
        self.maxdim.setReadOnly(True)
        self.labelmindim = QtGui.QLabel(self.groupBox1)
        self.labelmindim.resize(120, 27)
        self.labelmindim.move(10,50)
        self.labelmindim.setText("Minimum dimension:")
        self.mindim = QtGui.QLineEdit(self.groupBox1)
        self.mindim.resize(50, 27)
        self.mindim.move(135,50)
        self.mindim.setReadOnly(True)
        self.labelendtol = QtGui.QLabel(self.groupBox1)
        self.labelendtol.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelendtol.resize(120, 27)
        self.labelendtol.move(10,80)
        self.labelendtol.setText("Tolerance end dim:")
        self.endtol = QtGui.QLineEdit(self.groupBox1)
        self.endtol.resize(50, 27)
        self.endtol.move(135,80)
        self.endtol.setReadOnly(True)
        
        self.groupBox2 = QtGui.QGroupBox(self.groupBox)
        self.groupBox2.resize(425,120)
        self.groupBox2.move(230,50)
        self.groupBox2.setTitle("RSS")
        self.labelmaxdimrss = QtGui.QLabel(self.groupBox2)
        self.labelmaxdimrss.resize(120, 27)
        self.labelmaxdimrss.move(10,20)
        self.labelmaxdimrss.setText("Maximum dimension:")
        self.maxdimrss = QtGui.QLineEdit(self.groupBox2)
        self.maxdimrss.resize(50, 27)
        self.maxdimrss.move(135,20)
        self.maxdimrss.setReadOnly(True)
        self.labelmindimrss = QtGui.QLabel(self.groupBox2)
        self.labelmindimrss.resize(120, 27)
        self.labelmindimrss.move(10,50)
        self.labelmindimrss.setText("Minimum dimension:")
        self.mindimrss = QtGui.QLineEdit(self.groupBox2)
        self.mindimrss.resize(50, 27)
        self.mindimrss.move(135,50)
        self.mindimrss.setReadOnly(True)
        self.labelendtolrss = QtGui.QLabel(self.groupBox2)
        self.labelendtolrss.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelendtolrss.resize(120, 27)
        self.labelendtolrss.move(10,80)
        self.labelendtolrss.setText("Tolerance end dim:")
        self.endtolrss = QtGui.QLineEdit(self.groupBox2)
        self.endtolrss.resize(50, 27)
        self.endtolrss.move(135,80)
        self.endtolrss.setReadOnly(True)
        self.labelmean = QtGui.QLabel(self.groupBox2)
        self.labelmean.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelmean.resize(60, 27)
        self.labelmean.move(190,20)
        self.labelmean.setText("Mean:")
        self.mean = QtGui.QLineEdit(self.groupBox2)
        self.mean.resize(50, 27)
        self.mean.move(255,20)
        self.mean.setReadOnly(True)
        self.labelvariance = QtGui.QLabel(self.groupBox2)
        self.labelvariance.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelvariance.resize(60, 27)
        self.labelvariance.move(190,50)
        self.labelvariance.setText("Variance:")
        self.variance = QtGui.QLineEdit(self.groupBox2)
        self.variance.resize(50, 27)
        self.variance.move(255,50)
        self.variance.setReadOnly(True)
        self.labelpercentage = QtGui.QLabel(self.groupBox2)
        self.labelpercentage.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelpercentage.resize(60, 27)
        self.labelpercentage.move(190,80)
        self.labelpercentage.setText("Percent %:")
        self.percentage = QtGui.QLineEdit(self.groupBox2)
        self.percentage.resize(50, 27)
        self.percentage.move(255,80)
        self.percentage.setReadOnly(True)
        
#Diagrams

        pyqtgraph.setConfigOption('background', 'w')
        pyqtgraph.setConfigOption('antialias', True)
        self.diagram1 = pyqtgraph.PlotWidget(self.groupBox, title="Distribution")
        self.diagram1.resize(315, 300)
        self.diagram1.move(20, 185)
        self.diagram1.hideAxis("left")
        self.diagram1.getAxis("bottom").setGrid(150)
        self.diagram1.getAxis("bottom").setHeight(15)
        #self.diagram1.getViewBox().enableAutoRange('y', 0.5)
        #self.diagram1.getViewBox().translateBy(x=0.1, y=0)
        #self.labeldiagram1 = QtGui.QLabel(self.groupBox)
        #self.labeldiagram1.resize(70,27)
        #self.labeldiagram1.move(25, 190)
        #self.labeldiagram1.setText("Distribution")
        #self.labeldiagram1_1 = QtGui.QLabel(self.groupBox)
        #self.labeldiagram1_1.resize(70,14)
        #self.labeldiagram1_1.move(25, 205)
        #self.labeldiagram1_1.setText("Worst case")
        #self.labeldiagram1_1.setAutoFillBackground(True)
        
        self.diagram2 = pyqtgraph.PlotWidget(self.groupBox, title="Contribution")
        self.diagram2.resize(315, 300)
        self.diagram2.move(340, 185)
        self.diagram2.getAxis("bottom").setHeight(15)
        self.diagram2.getAxis("left").setWidth(20)
        self.diagram2.getAxis("left").setGrid(150)
        #self.diagram2.hideAxis("bottom")
        #self.labeldiagram2 = QtGui.QLabel(self.groupBox)
        #self.labeldiagram2.resize(70,27)
        #self.labeldiagram2.move(365, 190)
        #self.labeldiagram2.setText("Contribution")
        
# image

        self.picturelabel = QtGui.QLabel(self)
        self.picturelabel.resize(675,510)
        self.picturelabel.move(20,460)
        self.picturelabel.setStyleSheet("border: 1px solid black")
        self.picturelabel.setPixmap(QtGui.QPixmap("../PyTol/Resources/pytol_logo.png"))
        self.picturelabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        #self.picturelabel.setScaledContents(True)
        self.btnaddpic = QtGui.QPushButton(self)
        self.btnaddpic.resize(30, 30)
        self.btnaddpic.move(700, 460)
        self.btnaddpic.setIcon(QtGui.QIcon("../PyTol/Resources/picture-add.png"))
        self.btnaddpic.clicked.connect(self.add_picture)
        self.btnaddpic.setEnabled(False)
        self.btndelpic = QtGui.QPushButton(self)
        self.btndelpic.resize(30, 30)
        self.btndelpic.move(700, 495)
        self.btndelpic.setIcon(QtGui.QIcon("../PyTol/Resources/picture-delete.png"))
        self.btndelpic.clicked.connect(self.delete_picture)
        self.btndelpic.setEnabled(False)
   
        self.show()
        
    
    def test(self):
        exporter = exp.ImageExporter(self.diagram1.getPlotItem())
        exporter.parameters()['width'] = 300
        img = exporter.export(toBytes=True)
        pixmap = QtGui.QPixmap.fromImage(img)
        self.picturelabel.setPixmap(pixmap)
        
    def closeEvent(self, event): 
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            if global_vars.db_file != "":
                database.clean(global_vars.db_file)
            event.accept()
        else:
            event.ignore()
        
        
    def center(self):
        frameGm = self.frameGeometry()
        x_coord = (QtGui.QDesktopWidget().availableGeometry().width() - frameGm.width())/2
        self.move(x_coord, 0)
   

    def file_open(self):
        global_vars.dimList = []
        file_name = QtGui.QFileDialog.getOpenFileName(self,
                                                 'Open File', 
                                                 os.getcwd()+"/DB/", 
                                                 "Database Files (*.db)")
        if file_name:
            self.clear_form()
            #print str(file_name)
            self.setStatusTip("Connected to Database: "+str(file_name))
            global_vars.db_file = str(file_name)
            database.open_db(global_vars.db_file)
            if global_vars.partList != []:
                self.pop_partlist(global_vars.partList, global_vars.partList[0][1])
                global_vars.curPart =self.cmbPartList.currentText()
            if global_vars.dimList != []:
                self.pop_table(global_vars.dimList)
            if global_vars.stackList != []:
                self.pop_stacklist(global_vars.stackList, global_vars.stackList[0][1])
                self.set_picture(global_vars.stackList[0][0])
                #self.pop_stack_table(global_vars.stackDimList)
            self.check_status()

        
    def file_new(self):
        file_name = QtGui.QFileDialog.getSaveFileName(self,
                                                      'New File',
                                                      os.getcwd()+"/DB/untitled.db", 
                                                      "Database Files (*.db)")
        test = str(file_name)[-3:].lower()
        if test != ".db":
            file_name += ".db"
        if file_name:
            self.clear_form()
            self.setStatusTip("Connected to Database: "+str(file_name))
            global_vars.db_file = str(file_name)
            database.create_database(global_vars.db_file)
            database.add_tables(global_vars.db_file)
            self.check_status()
            
    def about(self):
        aboutdialog =  aboutDialog()
        aboutdialog.exec_()
            
        
    def pop_table(self, dimensions):
        rowcount = len(dimensions)
        self.tblDimList.setRowCount(rowcount)
        row = 0
        for r in range(rowcount):
            col = 0
            for c in range(7):
                cellinfo = QtGui.QTableWidgetItem(dimensions[r][c].decode('unicode-escape'))
                self.tblDimList.setItem(row, col, cellinfo)
                col +=1
            row +=1
            
    def pop_stack_table(self, stack):
        rowcount = len(stack)
        self.tblStackDimList.setRowCount(rowcount)
        row = 0
        stacklist = []
        self.diagram1.clear()
        self.diagram2.clear()
        for r in range(rowcount):
            rowlist = []
            dimdata = database.get_dim_data(global_vars.db_file, stack[r][3])
            self.tblStackDimList.setItem(row, 0, QtGui.QTableWidgetItem(stack[r][0]))
            self.tblStackDimList.setItem(row, 1, QtGui.QTableWidgetItem(stack[r][1]))
            self.tblStackDimList.setItem(row, 2, QtGui.QTableWidgetItem(dimdata[0][1].decode('unicode-escape')))
            self.tblStackDimList.setItem(row, 3, QtGui.QTableWidgetItem(dimdata[0][2]))
            self.tblStackDimList.setItem(row, 4, QtGui.QTableWidgetItem(dimdata[0][3]))
            self.tblStackDimList.setItem(row, 5, QtGui.QTableWidgetItem(dimdata[0][4]))
            self.tblStackDimList.setItem(row, 8, QtGui.QTableWidgetItem(stack[r][2]))
            if float(stack[r][1]) > 0:
                dimmax = (float(dimdata[0][2]) + float(dimdata[0][3]))*float(stack[r][1])
                dimmin = (float(dimdata[0][2]) + float(dimdata[0][4]))*float(stack[r][1])
            else:
                dimmax = (float(dimdata[0][2]) + float(dimdata[0][4]))*float(stack[r][1])
                dimmin = (float(dimdata[0][2]) + float(dimdata[0][3]))*float(stack[r][1])
            self.tblStackDimList.setItem(row, 6, QtGui.QTableWidgetItem(str(dimmax)))
            self.tblStackDimList.setItem(row, 7, QtGui.QTableWidgetItem(str(dimmin)))
            for c in range(1,9):
                rowlist.append(self.tblStackDimList.item(r,c).text())
            stacklist.append(rowlist)
            row +=1
        if rowcount >= 1:
            results = stackup_functions.TolStack(stacklist, self.tolp.text(), self.tolm.text(), self.conf.text())
            self.nominal.setText(str(results.nominal()))        
            self.maxdim.setText(str(results.worst_case_max()))
            self.mindim.setText(str(results.worst_case_min()))
            self.endtol.setText(str(results.tol_closing_dim()))
            self.mean.setText(str(results.stack_mean()))
            self.variance.setText(str(results.stack_variance())[0:6])
            self.endtolrss.setText(str(results.tol_end_dim())[0:6])
            self.maxdimrss.setText(str(results.max_dim())[0:6])
            self.mindimrss.setText(str(results.min_dim())[0:6])
            self.percentage.setText(str(results.percentage())[0:6])
            chartdata = results.chart_data()
            color_good = pyqtgraph.mkColor(153, 189, 86)
            color_bad = pyqtgraph.mkColor(183, 76, 83)
            color_worst_case = pyqtgraph.mkColor(91, 126, 186, 150)
            color_tolerance = pyqtgraph.mkColor(70, 192, 167, 150)
            color_barchart = pyqtgraph.mkColor(91, 126, 186, 255)
            #brush_worst = pyqtgraph.mkBrush(91, 126, 186, 150)
            
            self.diagram1.addLegend(size=(80, 30),offset=(3,3), bkgnd=(255, 255, 255, 0))
            self.diagram1.plot(chartdata[0],
                               chartdata[1],
                               pen=color_good,
                               fillLevel=0,
                               fillBrush=color_good)
            self.diagram1.plot(chartdata[2],
                               chartdata[3],
                               pen=color_bad,
                               fillLevel=0,
                               fillBrush=color_bad)
            self.diagram1.addLine(x=chartdata[2][len(chartdata[2])-1], pen=pyqtgraph.mkPen(color='r'))
            self.diagram1.plot(chartdata[4],
                               chartdata[5],
                               pen=color_bad,
                               fillLevel=0,
                               fillBrush=color_bad)
            self.diagram1.addLine(x=chartdata[4][len(chartdata[4])-1], pen=pyqtgraph.mkPen(color='r'))
            self.diagram1.plot(chartdata[6],
                               chartdata[7],
                               pen=pyqtgraph.mkPen(color='k', width=3))
            self.diagram1.plot(chartdata[8],
                               chartdata[9],
                               pen=pyqtgraph.mkPen(color=color_worst_case, width=1),
                               name="Worst",
                               fillLevel=chartdata[9][0]-.2,#chartdata[11][0]+.2,
                               fillBrush=color_worst_case)  
            self.diagram1.plot(chartdata[10],
                               chartdata[11],
                               pen=pyqtgraph.mkPen(color=color_tolerance, width=1),
                               name="RSS",
                               fillLevel=chartdata[11][0]-.2,
                               fillBrush=color_tolerance)
            
                
            x_axis_bargraph = [i for i in range(1, len(results.bar_chart_data())+1)]
            self.diagram2.addItem(pyqtgraph.BarGraphItem(x=x_axis_bargraph,
                                                         height=results.bar_chart_data(),
                                                         width=.6,
                                                         brush=color_barchart))
        
           
        else:
            self.maxdim.clear()
            self.mindim.clear()
            self.endtol.clear()
            self.maxdimrss.clear()
            self.mindimrss.clear()
            self.endtolrss.clear()
            self.mean.clear()
            self.variance.clear()
            self.percentage.clear()
            
            
        
        
    def pop_partlist(self, parts, cp):
        self.cmbPartList.clear()
        length = len(parts)
        for i in range(length):
            self.cmbPartList.addItem(parts[i][1].decode('unicode-escape'))
        index = self.cmbPartList.findText(cp, QtCore.Qt.MatchFixedString)
        self.cmbPartList.setCurrentIndex(index)
        
    def pop_stacklist(self, stacks, curstack):
        self.cmbStackList.clear()
        length = len(stacks)
        for i in range(length):
            self.cmbStackList.addItem(stacks[i][1].decode('unicode-escape'))
        index = self.cmbStackList.findText(curstack, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cmbStackList.setCurrentIndex(index)
            self.tolp.setText(stacks[index][2])
            self.tolm.setText(global_vars.stackList[index][3])
            self.conf.setText(global_vars.stackList[index][4])
            author = global_vars.stackList[index][5].decode('unicode-escape')
            if author.count("&") > 0:
                author = author.replace("&", ",")
            self.authname.setText(author)
            self.labelrevdate.setText(global_vars.stackList[index][6])
            self.pop_stack_table(global_vars.stackDimList)
            
        else:
            print "No Current Stack"
    
    def part_change(self, text):
        global_vars.curPart = unicode(text)
        part_id = find_sid(global_vars.curPart, global_vars.partList)
        global_vars.dimList = []
        database.get_dimensions(global_vars.db_file, part_id)
        self.tblDimList.clearSelection()
        self.rowData = []
        self.pop_table(global_vars.dimList)
        
    def stack_change(self, text):
        global_vars.curStack = unicode(text)
        global_vars.stackDimList = []
        key_current_stack = find_sid(global_vars.curStack, global_vars.stackList)
        database.get_stack_dimensions(global_vars.db_file, key_current_stack)
        self.set_picture(key_current_stack)        
        index = self.cmbStackList.findText(global_vars.curStack, QtCore.Qt.MatchFixedString)
        self.rowDataS = -1
        self.tblStackDimList.clearSelection()
        if index >= 0:
            self.cmbStackList.setCurrentIndex(index)
            self.tolp.setText(global_vars.stackList[index][2])
            self.tolm.setText(global_vars.stackList[index][3])
            self.conf.setText(global_vars.stackList[index][4])
            author = global_vars.stackList[index][5].decode('unicode-escape')
            if author.count("&") > 0:
                author = author.replace("&", ",")
            self.authname.setText(author)
            self.labelrevdate.setText(global_vars.stackList[index][6])
            self.pop_stack_table(global_vars.stackDimList)
        else:
            print "No Current Stack"
    
        
    def add_new_comp(self):
        addCompDialog =  EditCompDialog()
        addCompDialog.setWindowTitle("New component")
        addCompDialog.labelNewComp.setText("Component name:")
        addCompDialog.checklabel.setText("n")
        addCompDialog.exec_()
        global_vars.curPart = addCompDialog.newComp.text()
        partid = find_sid(global_vars.curPart, global_vars.partList)
        if partid is not None:
            self.pop_partlist(global_vars.partList, global_vars.partList[partid-1][1].decode('unicode-escape'))
            emptyDimlist = []
            self.pop_table(emptyDimlist)
        self.check_status()
        
    def add_new_stack(self):
        addStackDialog = AddStackDialog()
        addStackDialog.checklabel.setText("n")
        addStackDialog.exec_()
        key_new_stack = find_sid(addStackDialog.newStack.text(), global_vars.stackList)
        if key_new_stack is not None:
            self.pop_stacklist(global_vars.stackList, addStackDialog.newStack.text())
            emptyStacklist = []
            self.pop_stack_table(emptyStacklist)
            self.picturelabel.setPixmap(QtGui.QPixmap("../PyTol/Resources/pytol_logo.png"))
        self.check_status()
        
    def add_new_dim(self):
        global_vars.curPart =self.cmbPartList.currentText()
        addDimDialog = AddDimDialog()
        addDimDialog.labelcheck.setText("n")
        addDimDialog.exec_()
        self.pop_table(global_vars.dimList)
        self.check_status()
        
    def cellClick(self, row, col):
        self.rowData = []
        for i in range(6):
            try:
                self.rowData.append(unicode(self.tblDimList.item(row, i).text()))
            except:
                self.rowData.append("")
            
    
    def edit_dim(self):      
        #global_vars.curPart =self.cmbPartList.currentText()
        if self.rowData != []:
            editDimDialog = AddDimDialog()
            editDimDialog.newDimName.setText(self.rowData[1])
            editDimDialog.newDimNom.setText(self.rowData[2])
            editDimDialog.newDimTolP.setText(self.rowData[3])
            editDimDialog.newDimTolM.setText(self.rowData[4])
            editDimDialog.newDimComm.setText(self.rowData[5])
            editDimDialog.dimID = int(self.rowData[0])
            editDimDialog.labelcheck.setText("e")
            editDimDialog.setWindowTitle("Edit dimension")
            editDimDialog.exec_()
            self.pop_table(global_vars.dimList)
            self.pop_stack_table(global_vars.stackDimList)
            self.tblDimList.clearSelection()
            self.rowData = []
        else:
            mb = QtGui.QMessageBox ("Table error","Please select a dimension to edit!",QtGui.QMessageBox.Warning,QtGui.QMessageBox.Ok,0,0)
            mb.exec_()
        
    def edit_part(self):
        global_vars.curPart =unicode(self.cmbPartList.currentText())
        partid = find_sid(global_vars.curPart, global_vars.partList)
        editCompDialog = EditCompDialog()
        editCompDialog.newComp.setText(global_vars.curPart)
        editCompDialog.setWindowTitle("Rename component")
        editCompDialog.labelNewComp.setText("Component name:")
        editCompDialog.checklabel.setText("e")
        editCompDialog.exec_()
        self.pop_partlist(global_vars.partList, global_vars.partList[partid-1][1].decode('unicode-escape'))
        
    def edit_stack(self):
        global_vars.curStack =self.cmbStackList.currentText()
        editStackDialog = AddStackDialog()
        editStackDialog.setWindowTitle("Edit stack parameters")
        editStackDialog.checklabel.setText("e")
        editStackDialog.newStack.setText(global_vars.curStack)
        editStackDialog.CloseTolP.setText(self.tolp.text())
        editStackDialog.CloseTolM.setText(self.tolm.text())
        editStackDialog.Confidence.setText(self.conf.text())
        editStackDialog.Author.setText(self.authname.text())
        editStackDialog.RevDate.setText(self.labelrevdate.text())
        editStackDialog.exec_()
        curStack = editStackDialog.newStack.text()
        self.pop_stacklist(global_vars.stackList, curStack)

    def del_stack(self):
        global_vars.curStack =self.cmbStackList.currentText()
        key_current_stack = find_sid(global_vars.curStack, global_vars.stackList)
        rowcount = self.tblStackDimList.rowCount()
        for i in range(rowcount):
            entry_id = int(self.tblStackDimList.item(i, 0).text())
            database.delete_stack_entry(global_vars.db_file, entry_id, key_current_stack)
        database.delete_stack(global_vars.db_file, key_current_stack)
        if global_vars.stackList !=[]:
            self.pop_stacklist(global_vars.stackList, global_vars.stackList[0][1])
            global_vars.curStack =self.cmbStackList.currentText()
            key_current_stack = find_sid(global_vars.curStack, global_vars.stackList)
            database.get_stack_dimensions(global_vars.db_file, key_current_stack)
            self.set_picture(key_current_stack)
            self.pop_stack_table(global_vars.stackDimList)
        else:
            global_vars.stackDimList = []
            self.cmbStackList.clear()
            self.pop_stack_table(global_vars.stackDimList)
            self.btnMoveToStack.setEnabled(False)
            self.btnRemoveFromStack.setEnabled(False)
            self.btnDelStack.setEnabled(False)
            self.btnEditStack.setEnabled(False)
            self.btnEdStackDim.setEnabled(False)
            self.printAction.setEnabled(False)
            self.pdfAction.setEnabled(False)
            self.nominal.clear()
            self.tolp.clear()
            self.tolm.clear()
            self.conf.clear()
            self.authname.clear()
            self.labelrevdate.clear()
        
        
    def move_to_stack(self):
        if self.rowData != []:
            global_vars.curStack = self.cmbStackList.currentText()
            moveToStackDialog = MoveToStackDialog(self.rowData[0], "n")
            moveToStackDialog.exec_()
            self.pop_stack_table(global_vars.stackDimList)
            self.tblDimList.clearSelection()
            self.rowData = []
        else:
            mb = QtGui.QMessageBox ("Error","Please select a dimension first!",
                                    QtGui.QMessageBox.Warning,QtGui.QMessageBox.Ok,
                                    0,0)
            mb.exec_()
            
            
    def edit_stack_entry(self):
        if self.rowDataS != []:
            global_vars.curStack = self.cmbStackList.currentText()
            edit_entry = MoveToStackDialog(self.rowDataS[0], "e")
            edit_entry.setWindowTitle("Edit stack informations")
            edit_entry.coef.setText(str(self.rowDataS[1]))
            if str(self.rowDataS[8]) == "N":
                edit_entry.dist.setCurrentIndex(0)
            elif str(self.rowDataS[8]) == "T":
                edit_entry.dist.setCurrentIndex(1)
            else:
                edit_entry.dist.setCurrentIndex(2)
            edit_entry.exec_()
            self.pop_stack_table(global_vars.stackDimList)
            self.tblStackDimList.clearSelection()
            self.rowDataS = []
        else:
            mb = QtGui.QMessageBox ("Error","Please select a stack entry first!",
                                    QtGui.QMessageBox.Warning,QtGui.QMessageBox.Ok,
                                    0,0)
            mb.exec_()
           
        
    def cellClickS(self, row):
        self.rowDataS = []
        for i in range (9):
            self.rowDataS.append(self.tblStackDimList.item(row, i).text())
    
    def remove_from_stack(self):
        if self.rowDataS != []:
            global_vars.curStack = self.cmbStackList.currentText()
            key_current_stack = find_sid(global_vars.curStack, global_vars.stackList)
            database.delete_stack_entry(global_vars.db_file, int(self.rowDataS[0]), key_current_stack)
            self.pop_stack_table(global_vars.stackDimList)
            self.tblStackDimList.clearSelection()
        else:
           mb = QtGui.QMessageBox ("Error","Please select a stack entry first!",
                                    QtGui.QMessageBox.Warning,QtGui.QMessageBox.Ok,
                                    0,0)
           mb.exec_() 
 
    def add_picture(self):
        fname = QtGui.QFileDialog.getOpenFileName(self,
                                                  "Open file",
                                                  os.getcwd(),
                                                  "Image Files (*.png *.jpg *.gif)")
        if fname:
            image = resize_img(str(fname), 675, 510)
            imagedata = image.getvalue()
            name = QtCore.QFileInfo(fname).fileName()
            curStack = self.cmbStackList.currentText()
            database.insert_image(global_vars.db_file,
                                  find_sid(curStack, global_vars.stackList),
                                  imagedata,
                                  name)
            self.set_picture(find_sid(curStack, global_vars.stackList))

    def set_picture(self, stackid):
            db_image = database.extract_image(global_vars.db_file, stackid)
            if db_image:
                qimg = QtGui.QImage.fromData(db_image)
                pixmap = QtGui.QPixmap.fromImage(qimg)
                self.picturelabel.setPixmap(pixmap)
            else:
                self.picturelabel.setPixmap(QtGui.QPixmap("../PyTol/Resources/pytol_logo.png"))

    def delete_picture(self):
        self.picturelabel.setPixmap(QtGui.QPixmap("../PyTol/Resources/pytol_logo.png"))
        curStack = self.cmbStackList.currentText()
        find_sid(curStack, global_vars.stackList)
        imagedata = io.BytesIO().getvalue()
        database.insert_image(global_vars.db_file,
                                  find_sid(curStack, global_vars.stackList),
                                  imagedata,
                                  "no_image")
        
    def generate_stacklist(self):
        stack =[]
        header = ["Nr.", "Coef.", "Description", "Nominal", "Tol.+", "Tol.-", "Max dim.", "Min dim.", "Dist."]
        stack.append(header)
        rowcount = self.tblStackDimList.rowCount()
        for r in range(rowcount):
            rowlist = [r+1]
            for c in range (1,9):
                celltext = unicode(self.tblStackDimList.item(r,c).text())
                if len(celltext) > 44:
                    celltext = celltext[0:44:]
                    celltext = celltext + "..."
                rowlist.append(celltext)
            stack.append(rowlist)
        return stack

            
    def generate_stack_param(self):
        stack_param = []
        header = ["Nominal", "Upper tolerance", "Lower tolerance", "Confidence"]
        stack_param.append(header)
        values = []
        values.append(self.nominal.text())
        values.append(self.tolp.text())
        values.append(self.tolm.text())
        values.append(self.conf.text())
        stack_param.append(values)
        return stack_param
    
    
    def generate_results_worst_case(self):
        worst_case = []
        worst_case.append(["Worst case", ""])
        worst_case.append(["Max dim.", self.maxdim.text()])
        worst_case.append(["Min dim.", self.mindim.text()])
        worst_case.append(["Tolerance", self.endtol.text()])
        return worst_case
    
    def generate_results_rss(self):
        rss = []
        rss.append(["RSS", "", "", ""])
        rss.append(["Max dim.", self.maxdimrss.text(), "Mean", self.mean.text()])
        rss.append(["Min dim.", self.mindimrss.text(), "Variance", self.variance.text()])
        rss.append(["Tolerance", self.endtolrss.text(), "Percent", self.percentage.text()])
        return rss
    
    def generate_diagram(self, source):
        exporter = exp.ImageExporter(source.getPlotItem())
        exporter.parameters()['width'] = 300
        img = exporter.export(toBytes=True)
        
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.ReadWrite)
        
        img.save(buffer, "PNG")
        strio = cStringIO.StringIO()
        strio.write(buffer.data())
        buffer.close()
        strio.seek(0)
        pil_im = PIL.Image.open(strio)
        return pil_im
    
    def generate_picture(self):
        curStack = self.cmbStackList.currentText()
        stackid = find_sid(curStack, global_vars.stackList)
        db_image = database.extract_image(global_vars.db_file, stackid)
        try:
            img = PIL.Image.open(io.BytesIO(db_image))
        except:
            img = PIL.Image.open("../PyTol/Resources/pytol_logo.png")
        return img
    
    def save_report(self):
        file_name = QtGui.QFileDialog.getSaveFileName(self,
                                                      'Save File', 
                                                      os.getcwd() + "/untitled.pdf", 
                                                      "Pdf Files (*.pdf *.PDF)")
        if file_name:
            test = str(file_name)[-4:].lower()
            if test != ".pdf":
                file_name += ".pdf"
            rep = genrep.GenReport(self.cmbStackList.currentText(),
                                   self.generate_stack_param(),
                                   self.generate_results_worst_case(),
                                   self.generate_results_rss(),
                                   self.generate_stacklist(),
                                   self.generate_diagram(self.diagram1),
                                   self.generate_diagram(self.diagram2),
                                   self.generate_picture(),
                                   unicode(self.authname.text()),
                                   str(self.labelrevdate.text()),
                                   file_name)
            pdf=rep.pdf()
            pdf.save()
            
    def print_report(self):
        rep = genrep.GenReport(self.cmbStackList.currentText(),
                                   self.generate_stack_param(),
                                   self.generate_results_worst_case(),
                                   self.generate_results_rss(),
                                   self.generate_stacklist(),
                                   self.generate_diagram(self.diagram1),
                                   self.generate_diagram(self.diagram2),
                                   self.generate_picture(),
                                   unicode(self.authname.text()),
                                   str(self.labelrevdate.text()),
                                   "")
        pix = rep.pixmap()
        qimg = QtGui.QImage.fromData(pix.getPNGData())
        pixmap = QtGui.QPixmap.fromImage(qimg)
        printerobject = QtGui.QPrinter(0)
        printdialog = QtGui.QPrintDialog(printerobject)
        if printdialog.exec_() == QtGui.QDialog.Accepted:
             painter = QtGui.QPainter(printerobject)
             rect = painter.viewport()
             size = pixmap.size()
             size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
             painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
             painter.setWindow(pixmap.rect())
             painter.drawPixmap(0, 0, pixmap)
             del painter
        
        
    def check_status(self):
        if global_vars.db_file != "":
            self.btnNewComp.setEnabled(True)
        if global_vars.curPart != "":
            self.btnEditComp.setEnabled(True)
            self.btnNewDim.setEnabled(True)
        if global_vars.dimList != []:
            self.btnEditDim.setEnabled(True)
            self.btnNewStack.setEnabled(True)
        if global_vars.stackList != []:
            self.btnMoveToStack.setEnabled(True)
            self.btnRemoveFromStack.setEnabled(True)
            self.btnDelStack.setEnabled(True)
            self.btnEditStack.setEnabled(True)
            self.btnEdStackDim.setEnabled(True)
            self.btnaddpic.setEnabled(True)
            self.btndelpic.setEnabled(True)
            self.printAction.setEnabled(True)
            self.pdfAction.setEnabled(True)
    
    def clear_form(self):
        self.btnNewComp.setEnabled(False)
        self.btnEditComp.setEnabled(False)
        self.btnNewDim.setEnabled(False)
        self.btnEditDim.setEnabled(False)
        self.btnNewStack.setEnabled(False)
        self.btnEditStack.setEnabled(False)
        self.btnDelStack.setEnabled(False)
        self.btnEdStackDim.setEnabled(False)
        self.btnMoveToStack.setEnabled(False)
        self.btnRemoveFromStack.setEnabled(False)
        self.printAction.setEnabled(False)
        self.pdfAction.setEnabled(False)
        global_vars.curPart = ""
        global_vars.partList = []
        global_vars.dimList = []
        global_vars.db_file = ""
        global_vars.stackList = []
        global_vars.curStack = ""
        global_vars.stackDimList = []
        #self.endtolrss.setText("0.0")
        self.nominal.clear()
        self.tolp.clear()
        self.tolm.clear()
        self.conf.clear()
        #self.percentage.setText("0")
        self.authname.clear()
        self.labelrevdate.clear()
        self.cmbPartList.clear()
        self.pop_table(global_vars.dimList)
        self.cmbStackList.clear()
        self.pop_stack_table(global_vars.stackDimList)
        self.picturelabel.setPixmap(QtGui.QPixmap("../PyTol/Resources/pytol_logo.png"))
        
            

class AddStackDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setGeometry(800, 250, 450, 350)
        self.setWindowTitle("Add new stack")
        self.labelNewStack = QtGui.QLabel("New stack name:", self)
        self.labelNewStack.resize(150,27)
        self.labelNewStack.move(20,30)
        self.labelNewStack.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.newStack = QtGui.QLineEdit(self)
        self.newStack.resize(250, 27)
        self.newStack.move(180, 30)
        self.newStack.setText("")
        self.labelCloseTolP = QtGui.QLabel("Upper deviation:", self)
        self.labelCloseTolP.resize(150,27)
        self.labelCloseTolP.move(20,60)
        self.labelCloseTolP.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.CloseTolP = QtGui.QLineEdit(self)
        self.CloseTolP.resize(90, 27)
        self.CloseTolP.move(180, 60)
        self.CloseTolP.setText("")
        self.labelCloseTolM = QtGui.QLabel("Lower deviation:", self)
        self.labelCloseTolM.resize(150,27)
        self.labelCloseTolM.move(20,90)
        self.labelCloseTolM.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.CloseTolM = QtGui.QLineEdit(self)
        self.CloseTolM.resize(90, 27)
        self.CloseTolM.move(180, 90)
        self.CloseTolM.setText("")
        self.labelConfidence = QtGui.QLabel("Confidence interval:", self)
        self.labelConfidence.resize(150,27)
        self.labelConfidence.move(20,120)
        self.labelConfidence.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.Confidence = QtGui.QLineEdit(self)
        self.Confidence.resize(90, 27)
        self.Confidence.move(180, 120)
        self.Confidence.setText("")
        self.labelAuthor = QtGui.QLabel("Author:", self)
        self.labelAuthor.resize(150,27)
        self.labelAuthor.move(20,170)
        self.labelAuthor.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.Author = QtGui.QLineEdit(self)
        self.Author.resize(250, 27)
        self.Author.move(180, 170)
        self.Author.setText(system_vars.get_username())
        self.labelRevDate = QtGui.QLabel("Revision date:", self)
        self.labelRevDate.resize(150,27)
        self.labelRevDate.move(20,200)
        self.labelRevDate.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.RevDate = QtGui.QLineEdit(self)
        self.RevDate.resize(90, 27)
        self.RevDate.move(180, 200)
        self.RevDate.setText(system_vars.get_date())
        self.checklabel = QtGui.QLabel(self)
        self.checklabel.resize(30,27)
        self.checklabel.move(20,230)
        self.checklabel.hide()
        self.dialogBtn = QtGui.QDialogButtonBox(self)
        self.dialogBtn.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        self.dialogBtn.layout().setDirection(QtGui.QBoxLayout.RightToLeft)
        self.dialogBtn.move(250,300)
        self.dialogBtn.accepted.connect(self.add_stack)
        self.dialogBtn.rejected.connect(self.reject)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        reference_point = GUI.btnNewStack.mapToGlobal(GUI.btnNewStack.rect().topLeft())
        self.move(reference_point.x(), reference_point.y()+30)
        self.show()

        
    def add_stack(self):
        check = self.checklabel.text()
        stack_name = unicode(self.newStack.text())
        tolp = float(self.CloseTolP.text())
        tolm = float(self.CloseTolM.text())
        conf = int(self.Confidence.text())
        aut = unicode(self.Author.text())
        if aut.count(",") > 0:
            aut = aut.replace(",", "&")
        date = str(self.RevDate.text())
        if stack_name =="":
            mb = QtGui.QMessageBox ("Stack data","Please fill out all data!",
                                    QtGui.QMessageBox.Warning,QtGui.QMessageBox.Ok,
                                    0,0)
            mb.exec_()
        else:
            if check == "n":
                database.create_stack(global_vars.db_file, 
                                      stack_name, 
                                      tolp, 
                                      tolm, 
                                      conf, 
                                      aut, 
                                      date)
                self.close()
            elif check == "e":
                database.edit_stack(global_vars.db_file,
                                    stack_name,
                                    tolp,
                                    tolm,
                                    conf,
                                    aut,
                                    date,
                                    find_sid(global_vars.curStack, global_vars.stackList))
                self.close()
            
            

class AddDimDialog(QtGui.QDialog):
    dimID = 0
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setGeometry(150, 250, 370, 250)
        self.setWindowTitle("Add new dimension")
        
        self.labelNewDimName = QtGui.QLabel("Dimension name:", self)
        self.labelNewDimName.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelNewDimName.resize(130,27)
        self.labelNewDimName.move(00,30)
        self.newDimName = QtGui.QLineEdit(self)
        self.newDimName.resize(220, 27)
        self.newDimName.move(140, 30)
        
        self.labelNewDimNom = QtGui.QLabel("Dimension nominal:", self)
        self.labelNewDimNom.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelNewDimNom.resize(130,27)
        self.labelNewDimNom.move(00,60)
        self.newDimNom = QtGui.QLineEdit(self)
        self.newDimNom.resize(90, 27)
        self.newDimNom.move(140, 60)
        
        self.labelNewDimTolP = QtGui.QLabel("Upper Tolerance:", self)
        self.labelNewDimTolP.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelNewDimTolP.resize(130,27)
        self.labelNewDimTolP.move(00,90)
        self.newDimTolP = QtGui.QLineEdit(self)
        self.newDimTolP.resize(90, 27)
        self.newDimTolP.move(140, 90)
        
        self.labelNewDimTolM = QtGui.QLabel("Lower Tolerance:", self)
        self.labelNewDimTolM.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelNewDimTolM.resize(130,27)
        self.labelNewDimTolM.move(00,120)
        self.newDimTolM = QtGui.QLineEdit(self)
        self.newDimTolM.resize(90, 27)
        self.newDimTolM.move(140, 120)
        
        self.labelNewDimComm = QtGui.QLabel("Comment:", self)
        self.labelNewDimComm.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelNewDimComm.resize(130,27)
        self.labelNewDimComm.move(00,150)
        self.newDimComm = QtGui.QLineEdit(self)
        self.newDimComm.resize(220, 27)
        self.newDimComm.move(140, 150)
        self.newDimComm.setText("")
        
        self.labelcheck = QtGui.QLabel(self)
        self.labelcheck.resize(30,27)
        self.labelcheck.move(00,180)
        self.labelcheck.hide()
        
        self.dialogBtn = QtGui.QDialogButtonBox(self)
        self.dialogBtn.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        self.dialogBtn.layout().setDirection(QtGui.QBoxLayout.RightToLeft)
        self.dialogBtn.move(155,200)
        self.dialogBtn.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.add_dimension)
        self.dialogBtn.rejected.connect(self.reject)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        reference_point = GUI.btnNewDim.mapToGlobal(GUI.btnNewDim.rect().topLeft())
        self.move(reference_point.x()-200, reference_point.y()+30)
        self.show()

    def add_dimension(self):
        check = self.labelcheck.text()
        if check == "n":
            try:
                database.create_dim(global_vars.db_file, 
                                    unicode(self.newDimName.text()), 
                                    float(self.newDimNom.text()), 
                                    float(self.newDimTolP.text()),
                                    float(self.newDimTolM.text()),
                                    unicode(self.newDimComm.text()),
                                    find_sid(global_vars.curPart, global_vars.partList))
                self.close()
            except:
                mb = QtGui.QMessageBox ("Dimensions input",
                                        "Pleasy fill out with right data!",
                                        QtGui.QMessageBox.Warning,QtGui.QMessageBox.Ok,0,0)
                mb.exec_()
        elif check == "e":
            try:
                database.edit_dim(global_vars.db_file, 
                                  unicode(self.newDimName.text()), 
                                  float(self.newDimNom.text()), 
                                  float(self.newDimTolP.text()),
                                  float(self.newDimTolM.text()),
                                  unicode(self.newDimComm.text()),
                                  self.dimID,
                                  find_sid(global_vars.curPart, global_vars.partList))
                self.close()
            except:
                mb = QtGui.QMessageBox ("Dimensions input",
                                        "Pleasy fill out with right data!",
                                        QtGui.QMessageBox.Warning,QtGui.QMessageBox.Ok,0,0)
                mb.exec_()
            
        
class EditCompDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setGeometry(150, 250, 380, 150)
        self.labelNewComp = QtGui.QLabel(self)
        self.labelNewComp.resize(125,27)
        self.labelNewComp.move(20,30)
        self.labelNewComp.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.checklabel = QtGui.QLabel(self)
        self.checklabel.move(20,60)
        self.checklabel.hide()
        self.newComp = QtGui.QLineEdit(self)
        self.newComp.resize(200, 27)
        self.newComp.move(150, 30)
        self.newComp.setText("")
        self.dialogBtn = QtGui.QDialogButtonBox(self)
        self.dialogBtn.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        self.dialogBtn.layout().setDirection(QtGui.QBoxLayout.RightToLeft)
        self.dialogBtn.move(175,100)
        self.dialogBtn.accepted.connect(self.edit_prt)
        self.dialogBtn.rejected.connect(self.reject)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        reference_point = GUI.btnNewComp.mapToGlobal(GUI.btnNewComp.rect().topLeft())
        self.move(reference_point.x(), reference_point.y()+30)
        self.show()
        
    def edit_prt(self):
        check = self.checklabel.text()
        name = unicode(self.newComp.text())
        if name =="":
            mb = QtGui.QMessageBox ("Component number","Component name cannot be empty",QtGui.QMessageBox.Warning,QtGui.QMessageBox.Ok,0,0)
            mb.exec_()
        else:
            if check == "e":
                database.edit_part(global_vars.db_file,
                                   name,
                                   find_sid(global_vars.curPart, global_vars.partList))
                self.close()
            elif check == "n":
                database.create_part(global_vars.db_file, name)
                self.close()

class MoveToStackDialog(QtGui.QDialog):
     def __init__(self, rowID, check):
        self.rowID = rowID
        self.check = check
        QtGui.QWidget.__init__(self)
        self.setGeometry(600, 500, 200, 165)
        self.setWindowTitle("Input stack informations")
        self.labelCoef = QtGui.QLabel("Coefficient:", self)
        self.labelCoef.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelCoef.resize(70,27)
        self.labelCoef.move(20,30)
        self.coef = QtGui.QLineEdit(self)
        self.coef.resize(60, 27)
        self.coef.move(100, 30)
        self.labelDist = QtGui.QLabel("Distribution:", self)
        self.labelDist.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.labelDist.resize(70,27)
        self.labelDist.move(20,60)
        self.dist = QtGui.QComboBox(self)
        self.dist.resize(60, 27)
        self.dist.move(100, 60)
        distributions = ["N", "T", "R"]
        for i in distributions:
            self.dist.addItem(i)
        self.dist.setCurrentIndex(0)
        self.dialogBtn = QtGui.QDialogButtonBox(self)
        self.dialogBtn.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        self.dialogBtn.layout().setDirection(QtGui.QBoxLayout.RightToLeft)
        self.dialogBtn.move(15,120)
        self.dialogBtn.accepted.connect(self.move_to_stack)
        self.dialogBtn.rejected.connect(self.reject)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        reference_point = GUI.btnMoveToStack.mapToGlobal(GUI.btnMoveToStack.rect().topLeft())
        self.move(reference_point.x()-150, reference_point.y()+30)
        self.show()
        
        
        
     def move_to_stack(self):
        coef = str(self.coef.text())
        if coef == "" or self.rowID == None:
                mb = QtGui.QMessageBox ("Error","Please select a dimension and/or fill out the coefficient!",QtGui.QMessageBox.Warning,QtGui.QMessageBox.Ok,0,0)
                mb.exec_()
        else:
            if self.check == "n":
                database.move_to_stack(global_vars.db_file,
                                       coef,
                                       str(self.dist.currentText()),
                                       int(self.rowID),
                                       find_sid(global_vars.curStack, global_vars.stackList))
                self.close()
            elif self.check =="e":
                database.update_stack_entry(global_vars.db_file,
                                            find_sid(global_vars.curStack, global_vars.stackList),
                                            int(self.rowID),
                                            coef,
                                            str(self.dist.currentText()))
                self.close()

class aboutDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setGeometry(0, 0, 400, 500)
        self.setWindowTitle("About PyTol")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        windowGm = self.frameGeometry()
        parentGm = GUI.frameGeometry()
        x_coord = (parentGm.width() - windowGm.width())/2
        y_coord = (parentGm.height() - windowGm.height())/2
        self.move(x_coord, y_coord)
        self.dialogBtn = QtGui.QDialogButtonBox(self)
        self.dialogBtn.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.dialogBtn.move(305,460)
        self.dialogBtn.accepted.connect(self.reject)
        self.logolabel =  QtGui.QLabel(self)
        self.logolabel.resize(100,59)
        self.logolabel.move(150,0)
        self.logolabel.setPixmap(QtGui.QPixmap("../PyTol/Resources/pytol_logo.png"))
        self.logolabel.setScaledContents(True)
        self.textedit = QtGui.QTextBrowser(self)
        self.textedit.resize(350, 370)
        self.textedit.move(25, 55)
        self.textedit.setOpenExternalLinks(True)
        about = """<b>PyTol V0.01</b><br>
                    <br>
                    Tolerance stack-up calculator for mechanical engineers<br>
                    Copyright &copy; Zoltan Fekete<br>
                    Licensed under the terms of <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">GPLv3</a><br>
                    <br>
                    Created, developed and maintained by Zoltan Fekete.<br> 
                    For bug reports and requests please contact me under:<br> 
                    <a href="mailto:fekzol@gmail.com?Subject=PyTol" target="_top"> fekzol@gmail.com</a><br>
                    <br>
                    Many thanks to the developers of:<br>
                    <a href="https://www.python.org/">Python developers</a><br>
                    <a href="https://www.riverbankcomputing.com/software/pyqt/intro">PyQt</a><br>
                    <a href="https://sourceforge.net/projects/openiconlibrary/">Open Icon Library</a><br>
                    <a href="http://pyqtgraph.org/">PyQtGraph</a><br>
                    <a href="https://mupdf.com/">M&mu;PDF</a><br>
                    <a href="https://www.reportlab.com/">Reportlab</a><br>
                    <a href="https://sqlite.org/index.html">SQLite</a><br>
                    """
                    
        
        self.textedit.textCursor().insertHtml(about)
        
        
        
        
        self.show
        

global_vars.init()        
app = QtGui.QApplication(sys.argv)
app.setStyle('Plastique') #Clearlook, cleanlooks, Plastique, Windows
GUI = MainWindow()
sys.exit(app.exec_())
