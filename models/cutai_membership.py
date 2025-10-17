# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CutaiMembership(models.Model):
    _name = 'cutai.membership'
    _description = 'Membresía de Cliente CUTAI'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'
    
    name = fields.Char(
        string='Número de Membresía',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nuevo')
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        tracking=True,
        domain=[('is_cutai_client', '=', True)]
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activa'),
        ('frozen', 'Congelada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Completada'),
    ], string='Estado', default='draft', required=True, tracking=True)
    
    membership_type = fields.Selection([
        ('9_payments', '9 Pagos Mensuales'),
        ('prepaid', 'Prepago'),
        ('per_session', 'Por Sesión'),
    ], string='Tipo de Membresía', required=True, default='9_payments')
    
    cycle = fields.Selection([
        ('1', 'Ciclo 1'),
        ('2', 'Ciclo 2'),
        ('3', 'Ciclo 3'),
        ('4', 'Ciclo 4'),
        ('5', 'Ciclo 5'),
        ('6', 'Ciclo 6'),
        ('7', 'Ciclo 7'),
        ('8', 'Ciclo 8'),
        ('9', 'Ciclo 9'),
    ], string='Ciclo Actual', default='1', tracking=True)
    
    start_date = fields.Date(
        string='Fecha de Inicio',
        required=True,
        default=fields.Date.today
    )
    
    end_date = fields.Date(
        string='Fecha de Fin',
        compute='_compute_end_date',
        store=True
    )
    
    next_charge_date = fields.Date(
        string='Próxima Fecha de Cobro',
        tracking=True
    )
    
    payment_amount = fields.Monetary(
        string='Monto de Pago Mensual',
        currency_field='currency_id',
        required=True
    )
    
    total_amount = fields.Monetary(
        string='Monto Total',
        currency_field='currency_id',
        compute='_compute_total_amount',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    
    late_fee_amount = fields.Monetary(
        string='Monto de Mora',
        currency_field='currency_id',
        default=20.00,
        help='Monto de mora por pago atrasado (default: $20)'
    )
    
    late_fee_days = fields.Integer(
        string='Días para Mora',
        default=5,
        help='Número de días después del vencimiento para aplicar mora'
    )
    
    accumulated_late_fees = fields.Monetary(
        string='Moras Acumuladas',
        currency_field='currency_id',
        compute='_compute_accumulated_late_fees',
        store=True
    )
    
    is_frozen = fields.Boolean(
        string='Congelada',
        default=False,
        tracking=True
    )
    
    freeze_date = fields.Date(
        string='Fecha de Congelamiento',
        tracking=True
    )
    
    freeze_reason = fields.Text(
        string='Motivo de Congelamiento'
    )
    
    unfreeze_date = fields.Date(
        string='Fecha de Descongelamiento',
        help='Fecha programada para reactivar la membresía'
    )
    
    promotion_id = fields.Many2one(
        'cutai.promotion',
        string='Promoción Aplicada',
        tracking=True
    )
    
    has_active_promotion = fields.Boolean(
        string='Tiene Promoción Activa',
        compute='_compute_has_active_promotion'
    )
    
    payment_ids = fields.One2many(
        'cutai.membership.payment',
        'membership_id',
        string='Pagos'
    )
    
    payments_count = fields.Integer(
        string='Número de Pagos',
        compute='_compute_payments_count'
    )
    
    paid_payments_count = fields.Integer(
        string='Pagos Realizados',
        compute='_compute_payments_count'
    )
    
    cancellation_date = fields.Date(
        string='Fecha de Cancelación'
    )
    
    cancellation_reason = fields.Text(
        string='Motivo de Cancelación'
    )
    
    requires_30_day_notice = fields.Boolean(
        string='Requiere Aviso 30 Días',
        default=True,
        help='Según cláusula del contrato, se requiere aviso con 30 días de anticipación'
    )
    
    cancellation_notice_date = fields.Date(
        string='Fecha de Aviso de Cancelación'
    )
    
    notes = fields.Text(string='Notas')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('cutai.membership') or _('Nuevo')
        return super().create(vals)
    
    @api.depends('membership_type', 'start_date', 'cycle')
    def _compute_end_date(self):
        for membership in self:
            if membership.membership_type == '9_payments' and membership.start_date:
                from dateutil.relativedelta import relativedelta
                membership.end_date = membership.start_date + relativedelta(months=9)
            else:
                membership.end_date = False
    
    @api.depends('payment_amount', 'membership_type')
    def _compute_total_amount(self):
        for membership in self:
            if membership.membership_type == '9_payments':
                membership.total_amount = membership.payment_amount * 9
            else:
                membership.total_amount = membership.payment_amount
    
    @api.depends('payment_ids.state', 'payment_ids.late_fee')
    def _compute_accumulated_late_fees(self):
        for membership in self:
            membership.accumulated_late_fees = sum(
                membership.payment_ids.filtered(lambda p: p.state == 'paid').mapped('late_fee')
            )
    
    @api.depends('promotion_id', 'promotion_id.active', 'promotion_id.end_date')
    def _compute_has_active_promotion(self):
        today = fields.Date.today()
        for membership in self:
            if membership.promotion_id:
                membership.has_active_promotion = (
                    membership.promotion_id.active and
                    (not membership.promotion_id.end_date or membership.promotion_id.end_date >= today)
                )
            else:
                membership.has_active_promotion = False
    
    @api.depends('payment_ids')
    def _compute_payments_count(self):
        for membership in self:
            membership.payments_count = len(membership.payment_ids)
            membership.paid_payments_count = len(
                membership.payment_ids.filtered(lambda p: p.state == 'paid')
            )
    
    def action_activate(self):
        """Activar membresía"""
        self.ensure_one()
        if self.membership_type == '9_payments':
            self._generate_payment_schedule()
        self.state = 'active'
        return True
    
    def action_freeze(self):
        """Congelar membresía"""
        self.ensure_one()
        self.write({
            'state': 'frozen',
            'is_frozen': True,
            'freeze_date': fields.Date.today(),
        })
        return True
    
    def action_unfreeze(self):
        """Descongelar membresía"""
        self.ensure_one()
        self.write({
            'state': 'active',
            'is_frozen': False,
            'unfreeze_date': fields.Date.today(),
        })
        # Recalcular fechas de pago pendientes
        self._recalculate_payment_dates()
        return True
    
    def action_cancel(self):
        """Cancelar membresía con validación de aviso 30 días"""
        self.ensure_one()
        if self.requires_30_day_notice and not self.cancellation_notice_date:
            raise ValidationError(
                _('Esta membresía requiere un aviso de cancelación con 30 días de anticipación. '
                  'Por favor registre la fecha de aviso primero.')
            )
        
        if self.requires_30_day_notice and self.cancellation_notice_date:
            from datetime import timedelta
            min_cancellation_date = self.cancellation_notice_date + timedelta(days=30)
            if fields.Date.today() < min_cancellation_date:
                raise ValidationError(
                    _('No se puede cancelar hasta el %s (30 días después del aviso)') % 
                    min_cancellation_date.strftime('%d/%m/%Y')
                )
        
        self.write({
            'state': 'cancelled',
            'cancellation_date': fields.Date.today(),
        })
        return True
    
    def _generate_payment_schedule(self):
        """Generar calendario de 9 pagos mensuales"""
        self.ensure_one()
        from dateutil.relativedelta import relativedelta
        
        PaymentObj = self.env['cutai.membership.payment']
        
        for i in range(1, 10):
            payment_date = self.start_date + relativedelta(months=i-1)
            due_date = self.start_date + relativedelta(months=i)
            
            PaymentObj.create({
                'membership_id': self.id,
                'payment_number': i,
                'amount': self.payment_amount,
                'due_date': due_date,
                'state': 'pending',
            })
        
        self.next_charge_date = self.start_date + relativedelta(months=1)
    
    def _recalculate_payment_dates(self):
        """Recalcular fechas de pagos pendientes después de descongelar"""
        self.ensure_one()
        if not self.freeze_date or not self.unfreeze_date:
            return
        
        from datetime import timedelta
        freeze_days = (self.unfreeze_date - self.freeze_date).days
        
        pending_payments = self.payment_ids.filtered(lambda p: p.state == 'pending')
        for payment in pending_payments:
            if payment.due_date:
                payment.due_date = payment.due_date + timedelta(days=freeze_days)
    
    @api.model
    def _cron_check_late_payments(self):
        """Cron para revisar pagos atrasados y aplicar moras"""
        today = fields.Date.today()
        active_memberships = self.search([('state', '=', 'active')])
        
        for membership in active_memberships:
            overdue_payments = membership.payment_ids.filtered(
                lambda p: p.state == 'pending' and p.due_date and 
                (today - p.due_date).days >= membership.late_fee_days
            )
            
            for payment in overdue_payments:
                if not payment.late_fee_applied:
                    payment.write({
                        'late_fee': membership.late_fee_amount,
                        'late_fee_applied': True,
                    })
    
    @api.model
    def _cron_send_payment_reminders(self):
        """Cron para enviar recordatorios de pago"""
        from datetime import timedelta
        today = fields.Date.today()
        reminder_date = today + timedelta(days=3)
        
        memberships = self.search([
            ('state', '=', 'active'),
            ('next_charge_date', '=', reminder_date)
        ])
        
        template = self.env.ref('cutai_laser_clinic.email_template_payment_reminder', raise_if_not_found=False)
        if template:
            for membership in memberships:
                template.send_mail(membership.id, force_send=True)
