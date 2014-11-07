#!/usr/bin/env python
# This file is part of the stock_shipment_return module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.tests.test_tryton import test_depends
import os
import sys
import trytond.tests.test_tryton
import unittest


class StockShipmentReturnTestCase(unittest.TestCase):
    'Test Stock Shipment Return module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('stock_shipment_return')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        StockShipmentReturnTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
