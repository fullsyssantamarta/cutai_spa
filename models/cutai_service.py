# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CutaiService(models.Model):
    _name = 'cutai.service'
    _description = 'Servicio SPA/Láser'
    _order = 'category_id, sequence, name'
    
    name = fields.Char(string='Nombre del Servicio', required=True, translate=True)
    code = fields.Char(string='Código')
    
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    category_id = fields.Many2one(
        'cutai.service.category',
        string='Categoría',
        required=True
    )
    
    service_type = fields.Selection([
        ('laser', 'Tratamiento Láser'),
        ('facial', 'Facial'),
        ('corporal', 'Tratamiento Corporal'),
        ('massage', 'Masaje'),
        ('waxing', 'Depilación con Cera'),
        ('aesthetic', 'Tratamiento Estético'),
        ('spa', 'Servicio SPA'),
        ('combo', 'Combo/Paquete'),
        ('other', 'Otro'),
    ], string='Tipo de Servicio', required=True, default='laser')
    
    product_id = fields.Many2one(
        'product.product',
        string='Producto Asociado',
        required=True,
        help='Producto que se facturará por este servicio'
    )
    
    duration_minutes = fields.Float(
        string='Duración (minutos)',
        required=True,
        default=30.0,
        help='Duración estándar del servicio'
    )
    
    price = fields.Float(
        string='Precio',
        related='product_id.list_price',
        store=True,
        readonly=False
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Comisiones
    commission_type = fields.Selection([
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto Fijo'),
        ('none', 'Sin Comisión'),
    ], string='Tipo de Comisión', default='percentage')
    
    commission_percentage = fields.Float(
        string='% Comisión',
        help='Porcentaje de comisión para el terapeuta/operador'
    )
    
    commission_amount = fields.Float(
        string='Comisión Fija'
    )
    
    # Recursos necesarios
    requires_machine = fields.Boolean(
        string='Requiere Máquina',
        default=False
    )
    
    machine_ids = fields.Many2many(
        'cutai.machine',
        'cutai_service_machine_rel',
        'service_id',
        'machine_id',
        string='Máquinas Compatibles'
    )
    
    requires_cabin = fields.Boolean(
        string='Requiere Cabina',
        default=True
    )
    
    cabin_type = fields.Selection([
        ('standard', 'Estándar'),
        ('vip', 'VIP'),
        ('couple', 'Doble/Parejas'),
        ('laser', 'Láser'),
        ('any', 'Cualquiera'),
    ], string='Tipo de Cabina')
    
    # Consumibles
    backbar_product_ids = fields.Many2many(
        'product.product',
        'cutai_service_backbar_rel',
        'service_id',
        'product_id',
        string='Productos Backbar',
        domain=[('is_backbar_product', '=', True)]
    )
    
    # Zonas aplicables (para láser)
    zone_ids = fields.Many2many(
        'cutai.zone',
        'cutai_service_zone_rel',
        'service_id',
        'zone_id',
        string='Zonas Aplicables'
    )
    
    description = fields.Html(string='Descripción')
    instructions = fields.Text(string='Instrucciones para el Terapeuta')
    
    image_1920 = fields.Image(string='Imagen', max_width=1920, max_height=1920)
    
    # Estadísticas
    total_sales = fields.Integer(
        string='Total Vendido',
        compute='_compute_statistics'
    )
    
    average_rating = fields.Float(
        string='Calificación Promedio',
        compute='_compute_statistics'
    )
    
    def _compute_statistics(self):
        for service in self:
            # Aquí se pueden calcular estadísticas reales
            service.total_sales = 0
            service.average_rating = 0.0


class CutaiServiceCategory(models.Model):
    _name = 'cutai.service.category'
    _description = 'Categoría de Servicios'
    _order = 'sequence, name'
    
    name = fields.Char(string='Nombre', required=True, translate=True)
    code = fields.Char(string='Código')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    parent_id = fields.Many2one('cutai.service.category', string='Categoría Padre')
    child_ids = fields.One2many('cutai.service.category', 'parent_id', string='Subcategorías')
    
    service_ids = fields.One2many('cutai.service', 'category_id', string='Servicios')
    service_count = fields.Integer(string='Número de Servicios', compute='_compute_service_count')
    
    color = fields.Integer(string='Color')
    
    @api.depends('service_ids')
    def _compute_service_count(self):
        for category in self:
            category.service_count = len(category.service_ids)


class CutaiPackage(models.Model):
    _name = 'cutai.package'
    _description = 'Paquete/Combo de Servicios'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Nombre del Paquete', required=True)
    code = fields.Char(string='Código')
    active = fields.Boolean(default=True)
    
    package_type = fields.Selection([
        ('sessions', 'Paquete de Sesiones'),
        ('combo', 'Combo de Servicios'),
        ('membership', 'Membresía'),
    ], string='Tipo de Paquete', required=True, default='sessions')
    
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True
    )
    
    price = fields.Float(
        string='Precio del Paquete',
        related='product_id.list_price',
        store=True,
        readonly=False
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    line_ids = fields.One2many(
        'cutai.package.line',
        'package_id',
        string='Servicios Incluidos'
    )
    
    total_value = fields.Float(
        string='Valor Total',
        compute='_compute_total_value',
        store=True
    )
    
    discount_percentage = fields.Float(
        string='Descuento (%)',
        compute='_compute_discount'
    )
    
    validity_days = fields.Integer(
        string='Vigencia (días)',
        default=180,
        help='Días de vigencia del paquete desde la compra'
    )
    
    description = fields.Html(string='Descripción')
    image_1920 = fields.Image(string='Imagen')
    
    @api.depends('line_ids.subtotal')
    def _compute_total_value(self):
        for package in self:
            package.total_value = sum(package.line_ids.mapped('subtotal'))
    
    @api.depends('total_value', 'price')
    def _compute_discount(self):
        for package in self:
            if package.total_value > 0:
                package.discount_percentage = ((package.total_value - package.price) / package.total_value) * 100
            else:
                package.discount_percentage = 0.0


class CutaiPackageLine(models.Model):
    _name = 'cutai.package.line'
    _description = 'Línea de Paquete'
    
    package_id = fields.Many2one('cutai.package', string='Paquete', required=True, ondelete='cascade')
    service_id = fields.Many2one('cutai.service', string='Servicio', required=True)
    quantity = fields.Integer(string='Cantidad', required=True, default=1)
    
    price_unit = fields.Float(
        string='Precio Unitario',
        related='service_id.price',
        store=True,
        readonly=False
    )
    
    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True
    )
    
    currency_id = fields.Many2one('res.currency', related='package_id.currency_id')
    
    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
