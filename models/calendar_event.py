# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'
    
    # Campos específicos de CUTAI SPA
    branch_id = fields.Many2one(
        'cutai.branch',
        string='Sucursal',
        help='Sucursal donde se realizará la cita'
    )
    
    cabin_id = fields.Many2one(
        'cutai.cabin',
        string='Cabina',
        help='Cabina asignada para la cita'
    )
    
    machine_id = fields.Many2one(
        'cutai.machine',
        string='Máquina Láser',
        help='Máquina que se utilizará en la sesión (si aplica)'
    )
    
    attendant_id = fields.Many2one(
        'res.users',
        string='Terapeuta/Operador Principal',
        help='Persona responsable principal de la cita'
    )
    
    # Servicios en la cita
    service_ids = fields.One2many(
        'cutai.appointment.service',
        'appointment_id',
        string='Servicios'
    )
    
    service_count = fields.Integer(
        string='Número de Servicios',
        compute='_compute_service_count'
    )
    
    session_id = fields.Many2one(
        'cutai.session',
        string='Sesión de Tratamiento Láser',
        help='Sesión de tratamiento láser asociada (si aplica)'
    )
    
    treatment_id = fields.Many2one(
        'cutai.treatment',
        string='Tratamiento',
        related='session_id.treatment_id',
        store=True
    )
    
    zone_id = fields.Many2one(
        'cutai.zone',
        string='Zona a Tratar',
        related='session_id.zone_id',
        store=True
    )
    
    appointment_type = fields.Selection([
        ('consultation', 'Consulta'),
        ('laser', 'Tratamiento Láser'),
        ('spa', 'Servicio SPA'),
        ('facial', 'Facial'),
        ('massage', 'Masaje'),
        ('aesthetic', 'Estético'),
        ('combo', 'Combo'),
        ('follow_up', 'Seguimiento'),
        ('other', 'Otro'),
    ], string='Tipo de Cita', default='spa')
    
    estimated_duration_minutes = fields.Float(
        string='Duración Estimada (min)',
        compute='_compute_estimated_duration',
        store=True,
        help='Duración estimada total de la cita'
    )
    
    total_amount = fields.Float(
        string='Monto Total',
        compute='_compute_total_amount',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Estado de pago
    payment_status = fields.Selection([
        ('pending', 'Pendiente'),
        ('partial', 'Pago Parcial'),
        ('paid', 'Pagado'),
    ], string='Estado de Pago', default='pending')
    
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura'
    )
    
    @api.depends('service_ids')
    def _compute_service_count(self):
        for event in self:
            event.service_count = len(event.service_ids)
    
    @api.depends('service_ids.duration_minutes')
    def _compute_estimated_duration(self):
        for event in self:
            event.estimated_duration_minutes = sum(event.service_ids.mapped('duration_minutes'))
    
    @api.depends('service_ids.price_unit')
    def _compute_total_amount(self):
        for event in self:
            event.total_amount = sum(event.service_ids.mapped('price_unit'))
    
    reminder_sent_48h = fields.Boolean(
        string='Recordatorio T-48h Enviado',
        default=False
    )
    
    reminder_sent_24h = fields.Boolean(
        string='Recordatorio T-24h Enviado',
        default=False
    )
    
    reminder_sent_3h = fields.Boolean(
        string='Recordatorio T-3h Enviado',
        default=False
    )
    
    def action_send_reminder_48h(self):
        """Enviar recordatorio 48 horas antes"""
        template = self.env.ref('cutai_laser_clinic.email_template_reminder_48h', raise_if_not_found=False)
        if template:
            for event in self:
                if event.partner_ids and not event.reminder_sent_48h:
                    template.send_mail(event.id, force_send=True)
                    event.reminder_sent_48h = True
    
    def action_send_reminder_24h(self):
        """Enviar recordatorio 24 horas antes"""
        template = self.env.ref('cutai_laser_clinic.email_template_reminder_24h', raise_if_not_found=False)
        if template:
            for event in self:
                if event.partner_ids and not event.reminder_sent_24h:
                    template.send_mail(event.id, force_send=True)
                    event.reminder_sent_24h = True
    
    def action_send_reminder_3h(self):
        """Enviar recordatorio 3 horas antes"""
        template = self.env.ref('cutai_laser_clinic.sms_template_reminder_3h', raise_if_not_found=False)
        if template:
            for event in self:
                if event.partner_ids and not event.reminder_sent_3h:
                    # Enviar SMS
                    template.send_mail(event.id, force_send=True)
                    event.reminder_sent_3h = True
