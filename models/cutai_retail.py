# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CutaiAppointmentService(models.Model):
    _name = 'cutai.appointment.service'
    _description = 'Servicio en Cita'
    _order = 'appointment_id, sequence'
    
    name = fields.Char(string='Descripción', compute='_compute_name', store=True)
    sequence = fields.Integer(default=10)
    
    appointment_id = fields.Many2one(
        'calendar.event',
        string='Cita',
        required=True,
        ondelete='cascade'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        compute='_compute_partner',
        store=True
    )
    
    service_id = fields.Many2one(
        'cutai.service',
        string='Servicio',
        required=True
    )
    
    session_id = fields.Many2one(
        'cutai.session',
        string='Sesión Láser',
        help='Si es tratamiento láser, vincular con la sesión'
    )
    
    therapist_id = fields.Many2one(
        'res.users',
        string='Terapeuta/Operador',
        required=True
    )
    
    duration_minutes = fields.Float(
        string='Duración (min)',
        related='service_id.duration_minutes'
    )
    
    price_unit = fields.Float(
        string='Precio',
        related='service_id.price',
        readonly=False
    )
    
    state = fields.Selection([
        ('scheduled', 'Programado'),
        ('in_progress', 'En Proceso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='scheduled', required=True)
    
    # Comisión
    commission_type = fields.Selection(
        related='service_id.commission_type',
        store=True
    )
    
    commission_percentage = fields.Float(
        related='service_id.commission_percentage',
        store=True
    )
    
    commission_amount = fields.Float(
        string='Comisión',
        compute='_compute_commission',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Propinas
    tip_amount = fields.Monetary(
        string='Propina',
        currency_field='currency_id'
    )
    
    # Calificación
    rating = fields.Selection([
        ('1', '1 Estrella'),
        ('2', '2 Estrellas'),
        ('3', '3 Estrellas'),
        ('4', '4 Estrellas'),
        ('5', '5 Estrellas'),
    ], string='Calificación del Cliente')
    
    feedback = fields.Text(string='Comentarios del Cliente')
    
    notes = fields.Text(string='Notas del Terapeuta')
    
    @api.depends('appointment_id.partner_ids')
    def _compute_partner(self):
        for record in self:
            # Tomar el primer partner de la cita
            if record.appointment_id and record.appointment_id.partner_ids:
                record.partner_id = record.appointment_id.partner_ids[0]
            else:
                record.partner_id = False
    
    @api.depends('service_id')
    def _compute_name(self):
        for record in self:
            if record.service_id:
                record.name = record.service_id.name
            else:
                record.name = 'Servicio'
    
    @api.depends('price_unit', 'commission_type', 'commission_percentage', 'service_id.commission_amount')
    def _compute_commission(self):
        for record in self:
            if record.commission_type == 'percentage':
                record.commission_amount = record.price_unit * (record.commission_percentage / 100)
            elif record.commission_type == 'fixed':
                record.commission_amount = record.service_id.commission_amount
            else:
                record.commission_amount = 0.0


class CutaiRetailSale(models.Model):
    _name = 'cutai.retail.sale'
    _description = 'Venta Retail en Clínica'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    
    name = fields.Char(string='Número de Venta', required=True, readonly=True, default=lambda self: _('Nuevo'))
    
    date = fields.Datetime(
        string='Fecha',
        default=fields.Datetime.now,
        required=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True
    )
    
    branch_id = fields.Many2one(
        'cutai.branch',
        string='Sucursal',
        required=True
    )
    
    seller_id = fields.Many2one(
        'res.users',
        string='Vendedor',
        default=lambda self: self.env.user,
        required=True
    )
    
    line_ids = fields.One2many(
        'cutai.retail.sale.line',
        'sale_id',
        string='Productos'
    )
    
    subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True
    )
    
    discount_amount = fields.Monetary(
        string='Descuento',
        currency_field='currency_id'
    )
    
    total_amount = fields.Monetary(
        string='Total',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True
    )
    
    commission_amount = fields.Monetary(
        string='Comisión Vendedor',
        currency_field='currency_id',
        compute='_compute_commission',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('invoiced', 'Facturado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', required=True, tracking=True)
    
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura',
        readonly=True
    )
    
    payment_method = fields.Selection([
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('mixed', 'Mixto'),
    ], string='Método de Pago')
    
    notes = fields.Text(string='Notas')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('cutai.retail.sale') or _('Nuevo')
        return super().create(vals)
    
    @api.depends('line_ids.subtotal', 'discount_amount')
    def _compute_amounts(self):
        for sale in self:
            sale.subtotal = sum(sale.line_ids.mapped('subtotal'))
            sale.total_amount = sale.subtotal - sale.discount_amount
    
    @api.depends('line_ids.commission')
    def _compute_commission(self):
        for sale in self:
            sale.commission_amount = sum(sale.line_ids.mapped('commission'))


class CutaiRetailSaleLine(models.Model):
    _name = 'cutai.retail.sale.line'
    _description = 'Línea de Venta Retail'
    
    sale_id = fields.Many2one('cutai.retail.sale', string='Venta', required=True, ondelete='cascade')
    
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,
        domain=[('is_retail_product', '=', True)]
    )
    
    quantity = fields.Float(string='Cantidad', required=True, default=1.0)
    
    price_unit = fields.Monetary(
        string='Precio Unitario',
        currency_field='currency_id',
        required=True
    )
    
    discount_percentage = fields.Float(string='Descuento %')
    
    subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True
    )
    
    # Comisión del vendedor
    commission_percentage = fields.Float(
        string='% Comisión',
        related='product_id.retail_commission_percentage'
    )
    
    commission = fields.Monetary(
        string='Comisión',
        currency_field='currency_id',
        compute='_compute_commission',
        store=True
    )
    
    currency_id = fields.Many2one('res.currency', related='sale_id.currency_id')
    
    @api.depends('quantity', 'price_unit', 'discount_percentage')
    def _compute_subtotal(self):
        for line in self:
            amount = line.quantity * line.price_unit
            if line.discount_percentage:
                amount = amount * (1 - line.discount_percentage / 100)
            line.subtotal = amount
    
    @api.depends('subtotal', 'commission_percentage')
    def _compute_commission(self):
        for line in self:
            line.commission = line.subtotal * (line.commission_percentage / 100)
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    is_retail_product = fields.Boolean(
        string='Producto Retail',
        default=False,
        help='Producto para venta en mostrador (cosméticos, cremas, etc.)'
    )
    
    retail_commission_percentage = fields.Float(
        string='% Comisión Retail',
        help='Porcentaje de comisión para el vendedor'
    )
    
    product_brand_id = fields.Many2one(
        'cutai.product.brand',
        string='Marca'
    )
    
    retail_category = fields.Selection([
        ('skincare', 'Cuidado de la Piel'),
        ('haircare', 'Cuidado del Cabello'),
        ('cosmetics', 'Cosméticos'),
        ('supplements', 'Suplementos'),
        ('tools', 'Herramientas'),
        ('other', 'Otro'),
    ], string='Categoría Retail')


class CutaiProductBrand(models.Model):
    _name = 'cutai.product.brand'
    _description = 'Marca de Producto'
    
    name = fields.Char(string='Marca', required=True)
    code = fields.Char(string='Código')
    active = fields.Boolean(default=True)
    
    product_ids = fields.One2many('product.product', 'product_brand_id', string='Productos')
    product_count = fields.Integer(string='Número de Productos', compute='_compute_product_count')
    
    @api.depends('product_ids')
    def _compute_product_count(self):
        for brand in self:
            brand.product_count = len(brand.product_ids)
