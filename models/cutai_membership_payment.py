# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CutaiMembershipPayment(models.Model):
    _name = 'cutai.membership.payment'
    _description = 'Pago de Membresía'
    _order = 'due_date asc'
    
    membership_id = fields.Many2one(
        'cutai.membership',
        string='Membresía',
        required=True,
        ondelete='cascade'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        related='membership_id.partner_id',
        store=True
    )
    
    payment_number = fields.Integer(
        string='Número de Pago',
        required=True,
        help='Número del pago en el ciclo (1-9 para membresías de 9 pagos)'
    )
    
    amount = fields.Monetary(
        string='Monto Base',
        currency_field='currency_id',
        required=True
    )
    
    late_fee = fields.Monetary(
        string='Mora',
        currency_field='currency_id',
        default=0.0
    )
    
    total_amount = fields.Monetary(
        string='Monto Total',
        currency_field='currency_id',
        compute='_compute_total_amount',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        related='membership_id.currency_id',
        store=True
    )
    
    due_date = fields.Date(
        string='Fecha de Vencimiento',
        required=True
    )
    
    payment_date = fields.Date(
        string='Fecha de Pago Real'
    )
    
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('partial', 'Pago Parcial'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='pending', required=True)
    
    late_fee_applied = fields.Boolean(
        string='Mora Aplicada',
        default=False
    )
    
    days_overdue = fields.Integer(
        string='Días de Atraso',
        compute='_compute_days_overdue'
    )
    
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura',
        readonly=True
    )
    
    payment_id = fields.Many2one(
        'account.payment',
        string='Pago Contable',
        readonly=True
    )
    
    notes = fields.Text(string='Notas')
    
    @api.depends('amount', 'late_fee')
    def _compute_total_amount(self):
        for payment in self:
            payment.total_amount = payment.amount + payment.late_fee
    
    @api.depends('due_date', 'state')
    def _compute_days_overdue(self):
        today = fields.Date.today()
        for payment in self:
            if payment.state == 'pending' and payment.due_date:
                delta = today - payment.due_date
                payment.days_overdue = delta.days if delta.days > 0 else 0
            else:
                payment.days_overdue = 0
    
    def action_register_payment(self):
        """Abrir wizard para registrar pago"""
        self.ensure_one()
        return {
            'name': _('Registrar Pago'),
            'type': 'ir.actions.act_window',
            'res_model': 'cutai.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payment_id': self.id,
                'default_amount': self.total_amount,
            }
        }
    
    def mark_as_paid(self):
        """Marcar pago como pagado"""
        self.ensure_one()
        self.write({
            'state': 'paid',
            'payment_date': fields.Date.today(),
        })
        
        # Actualizar próxima fecha de cobro en la membresía
        if self.membership_id.membership_type == '9_payments':
            next_payment = self.membership_id.payment_ids.filtered(
                lambda p: p.payment_number == self.payment_number + 1
            )
            if next_payment:
                self.membership_id.next_charge_date = next_payment.due_date
            else:
                # Era el último pago
                self.membership_id.write({
                    'state': 'completed',
                    'next_charge_date': False,
                })
