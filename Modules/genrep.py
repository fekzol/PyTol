#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May  8 19:45:48 2019

@author: zoli
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import fitz, io, os

cwd = os.getcwd()

class GenReport(object):
    def __init__(self, name, parameters, worst_case, rss, stacklist, dia1, dia2, pic, auth, date, remark, file_name):
        self.name = name
        self.parameters = parameters
        self.worst_case = worst_case
        self.rss = rss
        self.stacklist = stacklist
        self.dia1 = dia1
        self.dia2 = dia2
        self.pic = pic
        self.auth = auth
        self.date = date
        self.remark = remark
        self.file_name = file_name
        
    def report(self, n):
        c = canvas.Canvas(n, pagesize=A4)
        c.setTitle ("PyTol Tolerance Stack-up Report")
        c.setAuthor(self.auth)
        c.setLineWidth(.3)
        c.setFont('Helvetica', 16)
 
        c.drawString(20*mm,280*mm,'Tolerance stack-up report for:')
        c.drawString(20*mm, 274*mm, unicode(self.name))

        c.setFont('Helvetica', 12)
        c.drawString(20*mm, 265*mm, 'Report parameters:')
        param_table = Table(self.parameters,
                                 colWidths = [45*mm] * 4)
        w, h = param_table.wrapOn(c, 0, 0)
        param_table.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                         ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                         ('FONT', (0,0), (-1,-1), 'Helvetica' , 12),
                                         ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                         ('BACKGROUND',(0,0),(-1,-2),colors.lavender)
                                         ]))
        param_table.drawOn(c, 20*mm, 250*mm)
        
        c.drawString(20*mm, 245*mm, 'Results:')
        worst_case_table = Table(self.worst_case,
                                 colWidths=(25*mm, 18*mm))
        w, h = worst_case_table.wrapOn(c, 0, 0)
        worst_case_table.setStyle(TableStyle([#('SPAN',(0,0),(1,0)),
                                              ('BOX', (0,0), (1,0), 0.25, colors.black),
                                              ('BOX', (0,1), (-1,-1), 0.25, colors.black),
                                              ('GRID', (0,1), (-1,-1), 0.25, colors.black),
                                              ('FONT', (0,0), (-1,-1), 'Helvetica' , 12),
                                              ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                              ('BACKGROUND',(0,0),(1,0),colors.lavender),
                                              ]))
        worst_case_table.drawOn(c, 20*mm, 218*mm)
        
        rss_table = Table(self.rss,
                          colWidths=(25*mm, 18*mm, 25*mm, 18*mm))
        w, h = rss_table.wrapOn(c, 0, 0)
        rss_table.setStyle(TableStyle([#('SPAN',(0,0),(1,0)),
                                      ('BOX', (0,0), (3,0), 0.25, colors.black),
                                      ('BOX', (0,1), (-1,-1), 0.25, colors.black),
                                      ('GRID', (0,1), (-1,-1), 0.25, colors.black),
                                      ('FONT', (0,0), (-1,-1), 'Helvetica' , 12),
                                      ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                      ('BACKGROUND',(0,0),(3,0),colors.lavender),
                                 ]))
        rss_table.drawOn(c, 66*mm, 218*mm)
        
        c.drawString(20*mm, 212*mm, 'Stack-up dimensions:')
        l = len(self.stacklist)
        emptyrow = ["", "", "", "", "", "", "", "", ""]
        if l < 15:
            for i in range(16-l):
                self.stacklist.append(emptyrow)
        stack_table = Table(self.stacklist,
                            colWidths=(8*mm, 10*mm, 80*mm, 16*mm, 12*mm, 12*mm, 17*mm, 17*mm, 10*mm),
                            rowHeights=5*mm)
        w, h = stack_table.wrapOn(c, 0, 0)
        stack_table.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                         ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                         ('FONT', (0,0), (-1,-1), 'Helvetica' , 10),
                                         ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                         ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                         ('BACKGROUND',(0,0),(-1,0),colors.lavender)
                                         ]))
        t_length = len(self.stacklist)
        pos_y = 210 - 5 * t_length
        stack_table.drawOn(c, 20*mm, pos_y*mm)
        
        image = ImageReader(self.dia1)
        c.drawImage(image, 147*mm, 72*mm, width=55*mm, height=55*mm)
        c.rect(147*mm,72*mm,55*mm,55*mm, fill=False)

        image = ImageReader(self.dia2)
        c.drawImage(image, 147*mm, 14*mm, width=55*mm, height=55*mm)
        c.rect(147*mm,14*mm,55*mm,55*mm, fill=False)
        
        image = ImageReader(self.pic)
        c.drawImage(image, 25*mm, 50*mm, width=101.8*mm, height=77*mm, preserveAspectRatio=True, mask='auto')
        
        c.drawString(20*mm, 45*mm, "Remarks:")
        remark_lines = []
        remark_lines.append(self.remark.split("\n"))        
        textobject = c.beginText(25*mm, 40*mm)
        for line in remark_lines[0]:
            textobject.textLine(unicode(line))
        c.drawText(textobject)
        
        c.setFont('Helvetica', 10)
        c.drawString(20*mm, 6*mm, "Rev. date:")
        c.drawString(38*mm, 6*mm, self.date)
        c.drawString(60*mm, 6*mm, "Author:")
        c.drawString(73*mm, 6*mm, self.auth)
        
        imagePath =cwd + "/Resources/pytol_logo_01.png"
        im = Image(imagePath, width=15*mm, height=5*mm)
        im.drawOn(c,180*mm,5*mm)
        c.setFont('Helvetica', 8)
        c.drawString(196*mm, 6*mm, 'V0.01')
 
        return c
        
    def pdf(self):
        pdf_name = unicode(self.file_name)
        return self.report(pdf_name)
    
    def pixmap(self):
        buffer = io.BytesIO()
        pdf = self.report(buffer)
        pdf.save()
        mat = fitz.Matrix(5, 5)
        doc = fitz.open("pdf", buffer)
        page = doc.loadPage(0)
        pix = page.getPixmap(matrix = mat, colorspace = fitz.csRGB)        
        buffer.close()
        return pix
        