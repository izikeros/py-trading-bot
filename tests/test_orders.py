#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 20:20:29 2022

@author: maxime
"""

import unittest
import numpy as np
from django.test import TestCase
from orders import models as m

class TestOrders(TestCase):
    def setUp(self):
        f=m.Fees.objects.create(name="zero",fixed=0,percent=0)
        
        e=m.StockEx.objects.create(name="Paris",fees=f,ib_ticker="SBF")
        self.e=e
        e2=m.StockEx.objects.create(name="XETRA",fees=f,ib_ticker="IBIS")
        c=m.Currency.objects.create(name="euro")
        cat=m.ActionCategory.objects.create(name="actions",short="ACT")
        strategy=m.Strategy.objects.create(name="none")
        s=m.ActionSector.objects.create(name="sec")
        self.s=s
        
        self.strategy=strategy
        m.Action.objects.create(
            symbol='AC.PA',
            #ib_ticker='AC',
            name="Accor",
            stock_ex=e,
            currency=c,
            category=cat,
            strategy=strategy,
            sector=s,
            )
        a=m.Action.objects.create(
            symbol='AI.PA',
            #ib_ticker='AC',
            name="Air liquide",
            stock_ex=e,
            currency=c,
            category=cat,
            strategy=strategy,
            sector=s,
            )
        self.a=a
        a2=m.Action.objects.create(
            symbol='AIR.PA',
            #ib_ticker='AC',
            name="Airbus",
            stock_ex=e,
            currency=c,
            category=cat,
            strategy=strategy,
            sector=s,
            )
        self.a2=a2
        m.Action.objects.create(
            symbol='SIE.DE',
            #ib_ticker='AC',
            name="Siemens",
            stock_ex=e2,
            currency=c,
            category=cat,
            strategy=strategy,
            sector=s,
            )
        symbols=['AC.PA','AI.PA','AIR.PA'] 
        m.Excluded.objects.create(name="all",strategy=strategy)
        
    def test_retrieve(self):
        cours_high, cours_low, cours_close, cours_open, cours_volume,  \
               cours_high_ind, cours_low_ind,  cours_close_ind, cours_open_ind,\
               cours_volume_ind=m.retrieve_data(['AC.PA','AI.PA','AIR.PA'] ,"1y")
               
        self.assertEqual(np.shape(cours_close)[1],3)
        self.assertTrue(np.shape(cours_close)[0]>200)
        self.assertTrue(np.shape(cours_close_ind)[0]>200)
        self.assertEqual(np.shape(cours_high)[1],3)
        self.assertTrue(np.shape(cours_high)[0]>200)
 
    def test_exchange_to_symbol(self):
        a=m.Action.objects.get(symbol="AIR.PA")
        self.assertEqual(m.exchange_to_symbol(a),"^FCHI")
        a=m.Action.objects.get(symbol="SIE.DE")
        self.assertEqual(m.exchange_to_symbol(a),"^GDAXI")       
        
    def test_get_exchange_actions(self):
        t=m.get_exchange_actions("Paris")
        self.assertEqual(len(t),3)
        t=m.get_exchange_actions("XETRA")
        self.assertEqual(len(t),1)     
     
    def test_get_ratio(self):
        t=m.get_ratio('AIR.PA')
        self.assertTrue(t!=0)
        
    def test_get_pf(self):
        pf=m.PF.objects.create(name="abc",short=False,strategy=self.strategy,stock_ex=self.e,sector=self.s)
        pf2= m.get_pf("none", "Paris",False)
        
        self.assertEqual(pf,pf2)
        
    def test_pf_retrieve(self):
        pf=m.PF.objects.create(name="abc",short=False,strategy=self.strategy,stock_ex=self.e,sector=self.s)
        self.assertEqual(pf.retrieve(),[])      
        pf.actions.add(self.a)
        self.assertEqual(pf.retrieve(),["AI.PA"])        
        
    def test_pf_retrieve_all(self):
        pf=m.PF.objects.create(name="abc",short=False,strategy=self.strategy,stock_ex=self.e,sector=self.s)
        pf.actions.add(self.a)
        pf2=m.PF.objects.create(name="abc2",short=False,strategy=self.strategy,stock_ex=self.e,sector=self.s)
        pf2.actions.add(self.a2)        
        
        self.assertEqual(m.pf_retrieve_all(),["AI.PA","AIR.PA"])      

    def test_pf_append(self):
        pf=m.PF.objects.create(name="abc",short=False,strategy=self.strategy,stock_ex=self.e,sector=self.s)
        pf.append("AI.PA")
        
        self.assertEqual(pf.retrieve(),["AI.PA"])  
        
    def test_pf_remove(self):
        pf=m.PF.objects.create(name="abc",short=False,strategy=self.strategy,stock_ex=self.e,sector=self.s)
        pf.append("AI.PA")
        pf.remove("AI.PA")
        
        self.assertEqual(pf.retrieve(),[])          
        
    def test_get_order_capital(self):
        ocap=m.OrderCapital.objects.create(capital=1,name="abc",strategy=self.strategy,stock_ex=self.e,sector=self.s)
        ocap2=m.get_order_capital("none","Paris")
        
        self.assertEqual(ocap,ocap2)
        
    def test_entry_order_test(self):
        pf=m.PF.objects.create(name="abc",short=False,strategy=self.strategy,stock_ex=self.e,sector=self.s)
        ocap=m.OrderCapital.objects.create(capital=1,name="abc",strategy=self.strategy,stock_ex=self.e,sector=self.s)
                
        t=m.entry_order_test("AIR.PA","none","Paris",False)

        self.assertTrue(t)
        self.assertEqual(len(pf.retrieve()),1)
        
        ocap=m.get_order_capital("none","Paris")
        self.assertEqual(ocap.capital,0)
        order=m.Order.objects.get(action="AIR.PA") #if not there, it will return an error
        
        t=m.entry_order_test("AIR.PA","none","Paris",False)
        self.assertFalse(t)
        
    def test_exit_order_test(self):        
        pf=m.PF.objects.create(name="abc",short=False,strategy=self.strategy,stock_ex=self.e,sector=self.s)
        ocap=m.OrderCapital.objects.create(capital=1,name="abc",strategy=self.strategy,stock_ex=self.e,sector=self.s)
                
        m.entry_order_test("AIR.PA","none","Paris",False)   
        t=m.exit_order_test("AIR.PA","none","Paris",False)   
        self.assertTrue(t)
        self.assertEqual(len(pf.retrieve()),0)
        ocap=m.get_order_capital("none","Paris")
        self.assertEqual(ocap.capital,1)
        
        order=m.Order.objects.get(action="AIR.PA")
        self.assertFalse(order.active)
        self.assertTrue(order.exiting_date is not None)
        


        
if __name__ == '__main__':
    unittest.main() 