# This file is part of the stock_shipment_return module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateAction

__all__ = ['CreateShipmentOutReturn']

MOVE_EXCLUDE_FIELDS = ['origin', 'shipment', 'invoice_lines']

class CreateShipmentOutReturn(Wizard):
    'Create Customer Return Shipment'
    __name__ = 'stock.shipment.out.return.create'
    start = StateAction('stock.act_shipment_out_return_form')

    @classmethod
    def __setup__(cls):
        super(CreateShipmentOutReturn, cls).__setup__()
        cls._error_messages.update({
                'shipment_done_title': 'You can not create return shipment',
                'shipment_done_msg': ('The shipment with code "%s" is not yet '
                    'sent.'),
                })

    def _get_shipment_out_return(self, shipment_out, default={}):
        'Returns Shipment Out Return object created from Shipment Out'
        pool = Pool()
        Shipment = pool.get('stock.shipment.out.return')
        shipment = Shipment()

        field_names = [n for n, f in Shipment._fields.iteritems()
            if (not isinstance(f, fields.Function)
                or isinstance(f, fields.Property))]
        default['state'] = 'draft'
        default['moves'] = []
        for field in field_names:
            if getattr(shipment_out, field, False):
                if field not in default:
                    setattr(shipment, field,
                        getattr(shipment_out, field))
                else:
                    setattr(shipment, field, default[field])

        # stock_origin fields
        if hasattr(shipment, 'origin_cache'):
            shipment.origin_cache = shipment_out
            shipment.origin_shipment = shipment_out
        return shipment

    def _get_incomming_move(self, outgoing_move, default={}):
        'Returns the equivalent incomming move instance for an outgoing move'
        pool = Pool()
        Move = pool.get('stock.move')
        move = Move()

        field_names = [n for n, f in Move._fields.iteritems()
            if (not isinstance(f, fields.Function)
                or isinstance(f, fields.Property))]
        default['state'] = 'draft'
        default['from_location'] = outgoing_move.to_location
        default['to_location'] = (
            outgoing_move.shipment.warehouse.input_location)
        for field in field_names:
            if field in MOVE_EXCLUDE_FIELDS:
                continue
            if field not in default:
                setattr(move, field, getattr(outgoing_move, field, None))
            else:
                setattr(move, field, default[field])
        move.origin = outgoing_move.shipment # origin is now from shipment out
        return move

    def do_start(self, action):
        pool = Pool()
        ShipmentOut = pool.get('stock.shipment.out')
        ShipmentOutReturn = pool.get('stock.shipment.out.return')

        def instance_to_dict(instance):
            '''
            It converts instance to dictionary converting Reference fields to
            string
            '''
            vals = {}
            for field in instance._values:
                if isinstance(instance._fields[field], fields.Reference):
                    vals[field] = str(getattr(instance, field))
                else:
                    vals[field] = getattr(instance, field)
            return vals

        shipment_ids = Transaction().context['active_ids']

        to_create = []
        for shipment_out in ShipmentOut.browse(shipment_ids):
            if shipment_out.state != 'done':
                self.raise_user_error('shipment_done_title',
                        error_description='shipment_done_msg',
                        error_description_args=shipment_out.code)

            shipment = self._get_shipment_out_return(shipment_out)
            shipment = instance_to_dict(shipment)
            incoming_moves = [self._get_incomming_move(m)
                for m in shipment_out.outgoing_moves]
            incoming_moves = [instance_to_dict(m)
                for m in incoming_moves]
            if incoming_moves:
                shipment.update({
                        'incoming_moves': [('create', incoming_moves)]
                        })
            to_create.append(shipment)
        shipment_out_returns = ShipmentOutReturn.create(to_create)

        data = {'res_id': [x.id for x in shipment_out_returns]}
        if len(shipment_out_returns) == 1:
            action['views'].reverse()
        return action, data

    def transition_start(self):
        return 'end'
