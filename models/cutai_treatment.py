# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CutaiTreatment(models.Model):
    _name = 'cutai.treatment'
    _description = 'Tratamiento de Depilación Láser'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'
    
    name = fields.Char(
        string='Nombre del Tratamiento',
        compute='_compute_name',
        store=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        tracking=True,
        domain=[('is_cutai_client', '=', True)]
    )
    
    zone_id = fields.Many2one(
        'cutai.zone',
        string='Zona de Tratamiento',
        required=True,
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('paused', 'Pausado'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', required=True, tracking=True)
    
    start_date = fields.Date(
        string='Fecha de Inicio',
        default=fields.Date.today,
        required=True
    )
    
    end_date = fields.Date(
        string='Fecha de Finalización'
    )
    
    planned_sessions = fields.Integer(
        string='Sesiones Planificadas',
        default=8,
        help='Número total de sesiones planificadas para este tratamiento'
    )
    
    completed_sessions = fields.Integer(
        string='Sesiones Completadas',
        compute='_compute_completed_sessions',
        store=True
    )
    
    progress = fields.Float(
        string='Progreso (%)',
        compute='_compute_progress',
        store=True
    )
    
    # Parámetros del tratamiento
    default_fluence = fields.Float(
        string='Fluencia Predeterminada (J/cm²)',
        help='Fluencia en Joules por centímetro cuadrado',
        digits=(5, 2)
    )
    
    default_spot_size = fields.Integer(
        string='Tamaño de Spot Predeterminado (mm)',
        help='Tamaño del spot en milímetros'
    )
    
    default_pulse_duration = fields.Float(
        string='Duración de Pulso Predeterminada (ms)',
        help='Duración del pulso en milisegundos',
        digits=(5, 2)
    )
    
    frequency = fields.Selection([
        ('4_weeks', 'Cada 4 semanas'),
        ('6_weeks', 'Cada 6 semanas'),
        ('8_weeks', 'Cada 8 semanas'),
        ('custom', 'Personalizado'),
    ], string='Frecuencia de Sesiones', default='6_weeks')
    
    custom_frequency_days = fields.Integer(
        string='Frecuencia Personalizada (días)'
    )
    
    session_ids = fields.One2many(
        'cutai.session',
        'treatment_id',
        string='Sesiones'
    )
    
    next_session_date = fields.Date(
        string='Próxima Sesión',
        compute='_compute_next_session_date'
    )
    
    membership_id = fields.Many2one(
        'cutai.membership',
        string='Membresía Asociada'
    )
    
    notes = fields.Text(string='Notas del Tratamiento')
    
    @api.depends('partner_id', 'zone_id')
    def _compute_name(self):
        for treatment in self:
            if treatment.partner_id and treatment.zone_id:
                treatment.name = f"{treatment.partner_id.name} - {treatment.zone_id.name}"
            else:
                treatment.name = _('Nuevo Tratamiento')
    
    @api.depends('session_ids.state')
    def _compute_completed_sessions(self):
        for treatment in self:
            treatment.completed_sessions = len(
                treatment.session_ids.filtered(lambda s: s.state == 'completed')
            )
    
    @api.depends('completed_sessions', 'planned_sessions')
    def _compute_progress(self):
        for treatment in self:
            if treatment.planned_sessions > 0:
                treatment.progress = (treatment.completed_sessions / treatment.planned_sessions) * 100
            else:
                treatment.progress = 0.0
    
    @api.depends('session_ids.appointment_id.start')
    def _compute_next_session_date(self):
        for treatment in self:
            future_sessions = treatment.session_ids.filtered(
                lambda s: s.appointment_id and 
                s.appointment_id.start >= fields.Datetime.now() and
                s.state in ['scheduled', 'confirmed']
            ).sorted('appointment_id.start')
            treatment.next_session_date = future_sessions[0].appointment_id.start.date() if future_sessions else False
    
    def action_activate(self):
        """Activar tratamiento"""
        self.write({'state': 'active'})
        return True
    
    def action_pause(self):
        """Pausar tratamiento"""
        self.write({'state': 'paused'})
        return True
    
    def action_complete(self):
        """Completar tratamiento"""
        self.write({
            'state': 'completed',
            'end_date': fields.Date.today(),
        })
        return True
    
    def action_schedule_next_session(self):
        """Abrir wizard para programar próxima sesión"""
        self.ensure_one()
        return {
            'name': _('Programar Sesión'),
            'type': 'ir.actions.act_window',
            'res_model': 'cutai.session.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_treatment_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_zone_id': self.zone_id.id,
                'default_session_number': self.completed_sessions + 1,
            }
        }
