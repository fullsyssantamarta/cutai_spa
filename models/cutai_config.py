# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CutaiBranch(models.Model):
    _name = 'cutai.branch'
    _description = 'Sucursal CUTAI'
    _order = 'name'
    
    name = fields.Char(string='Nombre de Sucursal', required=True)
    code = fields.Char(string='Código', required=True)
    
    active = fields.Boolean(default=True)
    
    address_id = fields.Many2one(
        'res.partner',
        string='Dirección',
        domain=[('type', '=', 'other')]
    )
    
    phone = fields.Char(string='Teléfono')
    email = fields.Char(string='Email')
    
    manager_id = fields.Many2one(
        'res.users',
        string='Gerente de Sucursal'
    )
    
    stock_location_id = fields.Many2one(
        'stock.location',
        string='Ubicación de Inventario',
        domain=[('usage', '=', 'internal')]
    )
    
    cabin_ids = fields.One2many(
        'cutai.cabin',
        'branch_id',
        string='Cabinas'
    )
    
    machine_ids = fields.One2many(
        'cutai.machine',
        'branch_id',
        string='Máquinas'
    )
    
    cabin_count = fields.Integer(
        string='Número de Cabinas',
        compute='_compute_cabin_count'
    )
    
    @api.depends('cabin_ids')
    def _compute_cabin_count(self):
        for branch in self:
            branch.cabin_count = len(branch.cabin_ids)


class CutaiCabin(models.Model):
    _name = 'cutai.cabin'
    _description = 'Cabina de Tratamiento'
    _order = 'branch_id, name'
    
    name = fields.Char(string='Nombre de Cabina', required=True)
    code = fields.Char(string='Código')
    
    branch_id = fields.Many2one(
        'cutai.branch',
        string='Sucursal',
        required=True
    )
    
    active = fields.Boolean(default=True)
    
    capacity = fields.Integer(
        string='Capacidad',
        default=1,
        help='Número de personas que pueden ser atendidas simultáneamente'
    )
    
    machine_ids = fields.Many2many(
        'cutai.machine',
        'cutai_cabin_machine_rel',
        'cabin_id',
        'machine_id',
        string='Máquinas Disponibles'
    )
    
    notes = fields.Text(string='Notas')


class CutaiMachine(models.Model):
    _name = 'cutai.machine'
    _description = 'Máquina Láser'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    name = fields.Char(string='Nombre de Máquina', required=True)
    code = fields.Char(string='Código/Serie', required=True)
    
    branch_id = fields.Many2one(
        'cutai.branch',
        string='Sucursal',
        required=True
    )
    
    active = fields.Boolean(default=True)
    
    manufacturer = fields.Char(string='Fabricante')
    model = fields.Char(string='Modelo')
    
    technology = fields.Selection([
        ('alexandrite', 'Alexandrita'),
        ('diode', 'Diodo'),
        ('nd_yag', 'Nd:YAG'),
        ('ipl', 'IPL (Luz Pulsada)'),
        ('other', 'Otra'),
    ], string='Tecnología')
    
    wavelength = fields.Char(
        string='Longitud de Onda (nm)',
        help='Por ejemplo: 755, 808, 1064'
    )
    
    max_fluence = fields.Float(
        string='Fluencia Máxima (J/cm²)',
        help='Fluencia máxima permitida por la máquina'
    )
    
    spot_sizes = fields.Char(
        string='Tamaños de Spot Disponibles',
        help='Por ejemplo: 8, 10, 12, 15 mm'
    )
    
    purchase_date = fields.Date(string='Fecha de Compra')
    warranty_expiry_date = fields.Date(string='Vencimiento de Garantía')
    
    last_maintenance_date = fields.Date(
        string='Última Mantención',
        tracking=True
    )
    
    next_maintenance_date = fields.Date(
        string='Próxima Mantención',
        tracking=True
    )
    
    total_shots = fields.Integer(
        string='Total de Disparos',
        help='Contador total de disparos de la máquina'
    )
    
    status = fields.Selection([
        ('operational', 'Operacional'),
        ('maintenance', 'En Mantención'),
        ('repair', 'En Reparación'),
        ('inactive', 'Inactiva'),
    ], string='Estado', default='operational', required=True, tracking=True)
    
    notes = fields.Text(string='Notas')


class CutaiZone(models.Model):
    _name = 'cutai.zone'
    _description = 'Zona de Tratamiento'
    _order = 'sequence, name'
    
    name = fields.Char(string='Nombre de Zona', required=True, translate=True)
    code = fields.Char(string='Código')
    
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    category = fields.Selection([
        ('face', 'Facial'),
        ('body', 'Corporal'),
        ('intimate', 'Íntima'),
    ], string='Categoría', required=True)
    
    estimated_duration = fields.Float(
        string='Duración Estimada (min)',
        help='Tiempo promedio de tratamiento para esta zona'
    )
    
    recommended_sessions = fields.Integer(
        string='Sesiones Recomendadas',
        default=8,
        help='Número típico de sesiones para esta zona'
    )
    
    description = fields.Text(string='Descripción')


class CutaiPromotion(models.Model):
    _name = 'cutai.promotion'
    _description = 'Promoción'
    _order = 'start_date desc'
    
    name = fields.Char(string='Nombre de Promoción', required=True)
    code = fields.Char(string='Código')
    
    active = fields.Boolean(default=True)
    
    promotion_type = fields.Selection([
        ('discount', 'Descuento'),
        ('bonus_sessions', 'Sesiones Extra'),
        ('package', 'Paquete Especial'),
        ('referral', 'Referido'),
    ], string='Tipo de Promoción', required=True)
    
    discount_percentage = fields.Float(
        string='Porcentaje de Descuento',
        help='Descuento en porcentaje'
    )
    
    discount_amount = fields.Monetary(
        string='Monto de Descuento',
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    bonus_sessions = fields.Integer(
        string='Sesiones Bonus',
        help='Número de sesiones extra que incluye la promoción'
    )
    
    start_date = fields.Date(string='Fecha de Inicio', required=True)
    end_date = fields.Date(string='Fecha de Fin')
    
    description = fields.Text(string='Descripción')
    terms_and_conditions = fields.Text(string='Términos y Condiciones')
