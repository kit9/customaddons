# -*- encoding: utf-8 -*-
#
#Created on May 7, 2018
#
#@author: dogan
#
#TODO @dogan: v12 de yeni tedarik talep sihirbazi yapilacak

from openerp import models, fields, api
from openerp.exceptions import except_orm

from openerp.addons.procurement.procurement import PROCUREMENT_PRIORITIES

class make_procurement(models.TransientModel):
    _inherit = 'make.procurement'
    
    priority = fields.Selection(PROCUREMENT_PRIORITIES,string='Priority', default='1')
    
    @api.multi
    def make_procurement(self):
        self.ensure_one()
        user = self.env.user
        wh_obj = self.env['stock.warehouse']
        procurement_obj = self.env['procurement.order']
        group_obj = self.env['procurement.group']
        data_obj = self.env['ir.model.data']

        group_id = group_obj.create({'name':'Request by %s at %s' % (user.name, fields.Datetime.now())})
        wh = wh_obj.browse(self.warehouse_id.id)
        procure_id = procurement_obj.create({
            'name':'INT: '+user.name.encode('utf-8'),
            'date_planned': self.date_planned,
            'product_id': self.product_id.id,
            'product_qty': self.qty,
            'product_uom': self.uom_id.id,
            'warehouse_id': self.warehouse_id.id,
            'location_id': wh.lot_stock_id.id,
            'company_id': wh.company_id.id,
            'group_id':group_id.id,
            'priority':self.priority
        })
        procure_id.signal_workflow( 'button_confirm')

        id2 = data_obj._get_id( 'procurement', 'procurement_tree_view')
        id3 = data_obj._get_id( 'procurement', 'procurement_form_view')

        if id2:
            id2 = data_obj.browse( id2).res_id
        if id3:
            id3 = data_obj.browse(id3).res_id

        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'procurement.order',
            'res_id' : procure_id.id,
            'views': [(id3,'form'),(id2,'tree')],
            'type': 'ir.actions.act_window',
         }
        
        
    @api.model
    def default_get(self, fields):
        """ override default to remove warehouse_id
        """        
        res = super(make_procurement, self).default_get( fields)

        if 'warehouse_id' in fields:
            res['warehouse_id'] = self.env.user.default_procurement_wh_id.id

        return res
    