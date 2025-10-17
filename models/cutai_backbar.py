# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CutaiBackbarConsumption(models.Model):
    _name = 'cutai.backbar.consumption'
    _description = 'Consumo de Productos Backbar'
    _order = 'date desc'
    
    name = fields.Char(
        string='Referencia',
        compute='_compute_name',
        store=True
    )
    
    date = fields.Date(
        string='Fecha',
        default=fields.Date.today,
        required=True
    )
    
    session_id = fields.Many2one(
        'cutai.session',
        string='Sesión',
        ondelete='cascade'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        related='session_id.partner_id',
        store=True
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,
        domain=[('is_backbar_product', '=', True)]
    )
    
    quantity = fields.Float(
        string='Cantidad Consumida',
        required=True,
        default=1.0,
        digits='Product Unit of Measure'
    )
    
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unidad de Medida',
        related='product_id.uom_id',
        store=True
    )
    
    branch_id = fields.Many2one(
        'cutai.branch',
        string='Sucursal',
        required=True
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Ubicación de Stock',
        related='branch_id.stock_location_id',
        store=True
    )
    
    stock_move_id = fields.Many2one(
        'stock.move',
        string='Movimiento de Inventario',
        readonly=True
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('posted', 'Registrado en Inventario'),
    ], string='Estado', default='draft', required=True)
    
    notes = fields.Text(string='Notas')
    
    @api.depends('session_id', 'product_id', 'date')
    def _compute_name(self):
        for record in self:
            if record.session_id:
                record.name = f"Consumo Sesión {record.session_id.name}"
            elif record.product_id:
                record.name = f"Consumo {record.product_id.name} - {record.date}"
            else:
                record.name = _('Nuevo Consumo')
    
    def action_confirm(self):
        """Confirmar consumo"""
        self.write({'state': 'confirmed'})
        return True
    
    def action_post_to_inventory(self):
        """Registrar el consumo en el inventario"""
        for record in self:
            if record.state != 'confirmed':
                continue
            
            # Crear movimiento de stock
            StockMove = self.env['stock.move']
            
            # Ubicación de consumo interno
            consumption_location = self.env.ref('stock.stock_location_production', raise_if_not_found=False)
            if not consumption_location:
                consumption_location = self.env['stock.location'].search([
                    ('usage', '=', 'production')
                ], limit=1)
            
            move_vals = {
                'name': record.name,
                'product_id': record.product_id.id,
                'product_uom_qty': record.quantity,
                'product_uom': record.uom_id.id,
                'location_id': record.location_id.id,
                'location_dest_id': consumption_location.id if consumption_location else record.location_id.id,
                'origin': record.name,
            }
            
            move = StockMove.create(move_vals)
            move._action_confirm()
            move._action_assign()
            move._action_done()
            
            record.write({
                'stock_move_id': move.id,
                'state': 'posted',
            })
        
        return True


class CutaiBackbarProduct(models.Model):
    _name = 'cutai.backbar.product'
    _description = 'Configuración de Producto Backbar'
    
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,
        domain=[('is_backbar_product', '=', True)]
    )
    
    zone_ids = fields.Many2many(
        'cutai.zone',
        'cutai_backbar_product_zone_rel',
        'backbar_product_id',
        'zone_id',
        string='Zonas de Aplicación'
    )
    
    consumption_type = fields.Selection([
        ('per_session', 'Por Sesión'),
        ('per_area', 'Por Área'),
        ('manual', 'Manual'),
    ], string='Tipo de Consumo', default='per_session', required=True)
    
    default_quantity = fields.Float(
        string='Cantidad por Defecto',
        default=1.0,
        digits='Product Unit of Measure',
        help='Cantidad que se consume por sesión o por área'
    )
    
    active = fields.Boolean(default=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    is_backbar_product = fields.Boolean(
        string='Es Producto Backbar',
        default=False,
        help='Marcar si este producto se usa en el backbar de tratamientos'
    )
    
    backbar_category = fields.Selection([
        ('sheets', 'Hojas'),
        ('gel', 'Gel'),
        ('towels', 'Toallas'),
        ('cryogen', 'Criógeno'),
        ('other', 'Otro'),
    ], string='Categoría Backbar')
