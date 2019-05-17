#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 14 18:00:57 2019

@author: zoli
"""

import sys, os
from PyQt4 import QtGui, QtCore
from Modules import database

cwd = os.getcwd()

class MainWindow(QtGui.QMainWindow):
   
    def __init__(self):
        super(MainWindow, self).__init__()
                
        self.setFixedSize(400, 170)
        self.setWindowTitle("Database update utility")
        self.center()
        
        self.labelask = QtGui.QLabel(self)
        self.labelask.resize(300, 27)
        self.labelask.move(50, 20)
        self.labelask.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.labelask.setText("Please select a database for update!")
        
        self.btnopen = QtGui.QPushButton(self)
        self.btnopen.setIcon(QtGui.QIcon(cwd+"/Resources/document-open-7.png"))
        self.btnopen.resize(50, 30)
        self.btnopen.move(30, 70)
        self.btnopen.clicked.connect(self.open_db)
        
        self.db = QtGui.QLineEdit(self)
        self.db.resize(280, 30)
        self.db.move(90,70)
        self.db.setText("")
        self.db.setReadOnly(True)
        
        self.btnupdate = QtGui.QPushButton("Update",self)
        self.btnupdate.resize(50, 30)
        self.btnupdate.move(260, 120)
        self.btnupdate.clicked.connect(self.update)
        self.btnupdate.setEnabled(False)
        
        self.btnclose = QtGui.QPushButton("Close",self)
        self.btnclose.resize(50, 30)
        self.btnclose.move(320, 120)
        self.btnclose.clicked.connect(self.close)
        
        self.show()
        
        
    def center(self):
        frameGm = self.frameGeometry()
        x_coord = (QtGui.QDesktopWidget().availableGeometry().width() - frameGm.width())/2
        self.move(x_coord, 300)
        
    def open_db(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                 'Open File', 
                                                 cwd+"/DB/", 
                                                 "Database Files (*.db)")
        if filename:
            self.db.setText(filename)
            self.file_name = str(filename)
            self.btnupdate.setEnabled(True)
            
    def update(self):
        stacks_columns_new = ['stack_id',
                              'stack_name',
                              'stack_tolp',
                              'stack_tolm',
                              'confidence',
                              'author',
                              'date',
                              'image_data',
                              'image_file',
                              'rem',
                              'rev_comment']
        self.create("stacks", stacks_columns_new)


    def create(self, table, columns_new):
        columns = database.get_columns(self.file_name, table)
        if len(columns) < len(columns_new):
            for i in range(len(columns), len(columns_new)):
                print columns_new[i]
                database.create_column(self.file_name, table, columns_new[i], "text")
        print "Database %s update succesfully!" %self.file_name
    
    def close(self):
        sys.exit()
        
        
app = QtGui.QApplication(sys.argv)
app.setStyle('Plastique') #Clearlook, cleanlooks, Plastique, Windows
GUI = MainWindow()
sys.exit(app.exec_())