#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May  1 18:33:08 2019

@author: zoli
"""
from scipy.stats import norm

def calc_nominal(coef, dim):
    nominal = 0.0
    length = len(coef)
    for i in range(length):
        nominal += float(coef[i]) * float(dim[i])
    return nominal

def contribution(factor, conf, dist, tol, tol_total):
    cont = factor ** 2 *(conf / dist) ** 2 * (tol / tol_total) ** 2 * 100
    return cont

class TolStack(object):
    def __init__(self, stack, tolp, tolm, confidence):
        self.stack = stack
        self.tolp = tolp
        self.tolm = tolm
        self.confidence = confidence
        
    def nominal(self):
        nominal = 0.0
        length = len(self.stack)
        for i in range(length):
            nominal += float(self.stack[i][0]) * float(self.stack[i][2])
        return nominal
    
    def worst_case_max(self):
        worst_max = 0.0
        length = len(self.stack)
        for i in range (length):
            worst_max += float(self.stack[i][5])
        return worst_max
    
    def worst_case_min(self):
        worst_min = 0.0
        length = len(self.stack)
        for i in range (length):
            worst_min += float(self.stack[i][6])
        return worst_min
    
    def tol_closing_dim(self):
        tol = self.worst_case_max() - self.worst_case_min()
        return tol
    
    def stack_mean(self):
        mean = (self.worst_case_max()+self.worst_case_min()) / 2
        return mean
    
    def stack_variance(self):
        """variance = 0.0
        length = len(self.stack)
        for i in range(length):
            dist = str(self.stack[i][7])
            tol = abs(float(self.stack[i][3]) - float(self.stack[i][4]))
            if dist == "N":
                sigma = tol / 6
            elif dist == "T":
                sigma = tol / (2 * ((6 / (1 + (2.0 / 3) ** 2)) ** (1/2.0)))
            elif dist == "R":
                sigma = tol / (2 * 3.0 ** (1/2.0))
            variance += sigma ** 2 * float(self.stack[i][0]) ** 2
        variance = variance ** (1/2.0)"""
        variance =  self.tol_end_dim() / int(self.confidence)
        return variance
    
    def tol_end_dim(self):
        #tol = self.stack_variance() * int(self.confidence)
        
        tol = 0.0
        length = len(self.stack)
        tr = 2 * ((6 / (1 + (2.0 / 3) ** 2)) ** (1/2.0))
        re = 2 * 3.0 ** (1/2.0)
        no = 6
        for i in range(length):
            dist = str(self.stack[i][7])
            t = abs(float(self.stack[i][3]) - float(self.stack[i][4]))
            if dist == "N":
                t2 = t
            elif dist == "T":
                t2 = t * no / tr
            elif dist == "R":
                t2 = t * no / re
            tol += (t2 ** 2) * (float(self.stack[i][0])) ** 2
        tol = tol ** (1/2.0)
        return tol
    
    def min_dim(self):
        dim = self.stack_mean() - self.tol_end_dim()/2
        return dim
        
    def max_dim(self):
        dim = self.stack_mean() + self.tol_end_dim()/2
        return dim

    def percentage(self):
        try:
            percentage_plus = norm.cdf(float(self.tolp) / self.stack_variance()) * 100
            #print percentage_plus
            percentage_minus = norm.cdf(float(self.tolm) / self.stack_variance()) * 100
            #print percentage_minus
            percentage_total = percentage_plus - percentage_minus
            if percentage_total >= 99.999:
                percentage_total = 100
            return percentage_total
        except:
            print "Oops! Division by zero! check variance!"
            percentage_total = "?"
            return percentage_total
    
    def chart_data(self):
        
# whole curve
        """x_axis = []
        y_norm_distr = []
        interv = [i/100.0 for i in range((int(self.confidence) / 2 + 1) * -100, 
                                         ((int(self.confidence) / 2 + 1) * 100) + 10,
                                         10)]
        for i in interv:
            x_axis.append(self.stack_mean() + i*self.stack_variance())  
        
        for i in x_axis:
            y_norm_distr.append(norm.pdf(i, loc=self.stack_mean(), scale=self.stack_variance()))"""
            
        y_norm_distr_out_left = []
        x_axis1 = []
        i = -int(self.confidence) / 2 - 1
        while i < float(self.tolm) / self.stack_variance():
            x_axis1.append(self.stack_mean()+i*self.stack_variance())
            i += 0.05
        x_axis1.append(self.stack_mean()+float(self.tolm))
        for i in x_axis1:
            y_norm_distr_out_left.append(norm.pdf(i, loc=self.stack_mean(), scale=self.stack_variance()))
            
        y_norm_distr_out_right = []
        x_axis2 = []
        i = int(self.confidence) / 2 + 1
        while i > float(self.tolp) / self.stack_variance():
            x_axis2.append(self.stack_mean()+i*self.stack_variance())
            i -= 0.05
        x_axis2.append(self.stack_mean()+float(self.tolp))
        for i in x_axis2:
            y_norm_distr_out_right.append(norm.pdf(i, loc=self.stack_mean(), scale=self.stack_variance())) 

        x_axis3 = []
        y_norm_distr_good = []
        i = -0.05
        while i > float(self.tolm) / self.stack_variance():
            x_axis3.insert(0, self.stack_mean()+i*self.stack_variance())
            i -= 0.05
        x_axis3.insert(0, self.stack_mean()+float(self.tolm))
        i = 0
        while i < float(self.tolp) / self.stack_variance():
            x_axis3.append(self.stack_mean()+i*self.stack_variance())
            i += 0.05
        x_axis3.append(self.stack_mean()+float(self.tolp))
        for i in x_axis3:
           y_norm_distr_good.append(norm.pdf(i, loc=self.stack_mean(), scale=self.stack_variance())) 

        x_axis_mean = [self.stack_mean() for i in range(2)]    
        y_axis_mean = [0.02, (norm.pdf(self.stack_mean(), loc=self.stack_mean(), scale=self.stack_variance()))-0.02]
        
        x_axis_worst_case = [self.worst_case_min(), self.worst_case_max()]
        y_axis_worst_case = [.4 * (norm.pdf(self.stack_mean(),
                                      loc=self.stack_mean(),
                                      scale=self.stack_variance())) for i in range(2)]
    
        x_axis_tolerance = [self.min_dim(), self.max_dim()]
        y_axis_tolerance = [.7 * (norm.pdf(self.stack_mean(),
                                      loc=self.stack_mean(),
                                      scale=self.stack_variance())) for i in range(2)]
        return (x_axis3, y_norm_distr_good,
                x_axis1, y_norm_distr_out_left,
                x_axis2, y_norm_distr_out_right,
                x_axis_mean, y_axis_mean,
                x_axis_worst_case, y_axis_worst_case,
                x_axis_tolerance, y_axis_tolerance)
        
        

    def bar_chart_data(self):
        bar_chart = []
        length = len(self.stack)
        for i in range(length):
            
            dist_type = str(self.stack[i][7])
            dist = 0.0
            if dist_type == "N":
                dist = 6.0
            elif dist_type == "T":
                dist = 2 * ((6 / (1 + (2.0 / 3) ** 2)) ** (1/2.0))
            elif dist_type == "R":
                dist = 2 * 3.0 ** (1/2.0)
            bar_chart.append(contribution(float(self.stack[i][0]),
                                          int(self.confidence),
                                          dist, 
                                          abs(float(self.stack[i][3])-float(self.stack[i][4])),
                                          self.tol_end_dim()))
        return bar_chart