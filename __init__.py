# This file is part of the stock_shipment_return module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import shipment
from . import move

def register():
    Pool.register(
        move.Move,
        module='stock_shipment_return', type_='model')
    Pool.register(
        shipment.CreateShipmentOutReturn,
        module='stock_shipment_return', type_='wizard')
