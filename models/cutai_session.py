# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CutaiSession(models.Model):
    _name = 'cutai.session'
    _description = 'Sesión de Tratamiento Láser'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'session_date desc'
    
    name = fields.Char(
        string='Nombre de Sesión',
        compute='_compute_name',
        store=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        domain=[('is_cutai_client', '=', True)]
    )
    
    treatment_id = fields.Many2one(
        'cutai.treatment',
        string='Tratamiento',
        required=True,
        ondelete='cascade'
    )
    
    zone_id = fields.Many2one(
        'cutai.zone',
        string='Zona Tratada',
        related='treatment_id.zone_id',
        store=True
    )
    
    session_number = fields.Integer(
        string='Número de Sesión',
        required=True,
        help='Número de la sesión dentro del tratamiento'
    )
    
    session_number_by_zone = fields.Integer(
        string='Sesión # por Zona',
        compute='_compute_session_number_by_zone',
        store=True,
        help='Número de sesión para esta zona específica (todas las sesiones del cliente en esta zona)'
    )
    
    total_sessions_zone = fields.Integer(
        string='Total Sesiones en Zona',
        compute='_compute_total_sessions_zone',
        help='Total de sesiones completadas para esta zona'
    )
    
    session_date = fields.Date(
        string='Fecha de Sesión',
        default=fields.Date.today
    )
    
    appointment_id = fields.Many2one(
        'calendar.event',
        string='Cita Asociada'
    )
    
    state = fields.Selection([
        ('scheduled', 'Programada'),
        ('confirmed', 'Confirmada'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
        ('no_show', 'No Asistió'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='scheduled', required=True, tracking=True)
    
    # Parámetros técnicos de la sesión
    fluence = fields.Float(
        string='Fluencia (J/cm²)',
        help='Fluencia utilizada en esta sesión',
        digits=(5, 2),
        tracking=True
    )
    
    spot_size = fields.Integer(
        string='Tamaño de Spot (mm)',
        help='Tamaño del spot utilizado',
        tracking=True
    )
    
    pulse_duration = fields.Float(
        string='Duración de Pulso (ms)',
        help='Duración del pulso utilizado',
        digits=(5, 2)
    )
    
    shot_width = fields.Char(
        string='Ancho de Disparo',
        help='Ancho de disparo utilizado en el tratamiento'
    )
    
    pulses_count = fields.Integer(
        string='Número de Pulsos',
        help='Total de pulsos aplicados en la sesión'
    )
    
    # Recursos utilizados
    machine_id = fields.Many2one(
        'cutai.machine',
        string='Máquina Utilizada',
        tracking=True
    )
    
    cabin_id = fields.Many2one(
        'cutai.cabin',
        string='Cabina',
        tracking=True
    )
    
    branch_id = fields.Many2one(
        'cutai.branch',
        string='Sucursal',
        required=True
    )
    
    attendant_id = fields.Many2one(
        'res.users',
        string='Operador/a',
        default=lambda self: self.env.user,
        tracking=True
    )
    
    # Control de tiempo
    start_time = fields.Datetime(string='Hora de Inicio')
    end_time = fields.Datetime(string='Hora de Fin')
    
    duration_minutes = fields.Float(
        string='Duración (minutos)',
        compute='_compute_duration',
        store=True
    )
    
    # Observaciones clínicas
    pre_treatment_notes = fields.Text(
        string='Observaciones Pre-Tratamiento',
        help='Estado de la piel, área a tratar, etc.'
    )
    
    post_treatment_notes = fields.Text(
        string='Observaciones Post-Tratamiento',
        help='Reacción de la piel, efectos secundarios, etc.'
    )
    
    pain_level = fields.Selection([
        ('0', 'Sin dolor'),
        ('1', 'Muy leve'),
        ('2', 'Leve'),
        ('3', 'Moderado'),
        ('4', 'Fuerte'),
        ('5', 'Muy fuerte'),
    ], string='Nivel de Dolor Reportado')
    
    skin_reaction = fields.Selection([
        ('normal', 'Normal'),
        ('mild_redness', 'Enrojecimiento Leve'),
        ('moderate_redness', 'Enrojecimiento Moderado'),
        ('swelling', 'Inflamación'),
        ('blistering', 'Ampollas'),
        ('other', 'Otro'),
    ], string='Reacción de la Piel', default='normal')
    
    cooling_applied = fields.Boolean(
        string='Enfriamiento Aplicado',
        default=True
    )
    
    # Consumo de backbar
    backbar_consumption_ids = fields.One2many(
        'cutai.backbar.consumption',
        'session_id',
        string='Consumo de Backbar'
    )
    
    # Resultados y seguimiento
    hair_reduction_percentage = fields.Float(
        string='Reducción de Vello (%)',
        help='Porcentaje estimado de reducción de vello'
    )
    
    photos_before = fields.Many2many(
        'ir.attachment',
        'cutai_session_photos_before_rel',
        'session_id',
        'attachment_id',
        string='Fotos Antes'
    )
    
    photos_after = fields.Many2many(
        'ir.attachment',
        'cutai_session_photos_after_rel',
        'session_id',
        'attachment_id',
        string='Fotos Después'
    )
    
    # Facturación
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura'
    )
    
    @api.depends('partner_id', 'treatment_id', 'session_number')
    def _compute_name(self):
        for session in self:
            if session.partner_id and session.treatment_id:
                session.name = f"Sesión {session.session_number} - {session.partner_id.name} - {session.treatment_id.zone_id.name}"
            else:
                session.name = _('Nueva Sesión')
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for session in self:
            if session.start_time and session.end_time:
                delta = session.end_time - session.start_time
                session.duration_minutes = delta.total_seconds() / 60
            else:
                session.duration_minutes = 0.0
    
    @api.depends('partner_id', 'zone_id', 'session_date', 'state')
    def _compute_session_number_by_zone(self):
        """Calcular número de sesión para esta zona específica"""
        for session in self:
            if session.partner_id and session.zone_id:
                # Contar sesiones anteriores completadas en esta zona
                previous_sessions = self.search_count([
                    ('partner_id', '=', session.partner_id.id),
                    ('zone_id', '=', session.zone_id.id),
                    ('session_date', '<', session.session_date or fields.Date.today()),
                    ('state', '=', 'completed'),
                    ('id', '!=', session.id)
                ])
                # Si esta sesión está completada, sumar 1
                if session.state == 'completed':
                    session.session_number_by_zone = previous_sessions + 1
                else:
                    session.session_number_by_zone = previous_sessions + 1
            else:
                session.session_number_by_zone = 1
    
    @api.depends('partner_id', 'zone_id')
    def _compute_total_sessions_zone(self):
        """Calcular total de sesiones completadas en esta zona"""
        for session in self:
            if session.partner_id and session.zone_id:
                session.total_sessions_zone = self.search_count([
                    ('partner_id', '=', session.partner_id.id),
                    ('zone_id', '=', session.zone_id.id),
                    ('state', '=', 'completed')
                ])
            else:
                session.total_sessions_zone = 0
    
    @api.onchange('treatment_id')
    def _onchange_treatment_id(self):
        """Cargar parámetros predeterminados del tratamiento"""
        if self.treatment_id:
            self.fluence = self.treatment_id.default_fluence
            self.spot_size = self.treatment_id.default_spot_size
            self.pulse_duration = self.treatment_id.default_pulse_duration
            self.branch_id = self.appointment_id.branch_id if self.appointment_id else False
    
    def action_start_session(self):
        """Iniciar sesión"""
        self.write({
            'state': 'in_progress',
            'start_time': fields.Datetime.now(),
        })
        return True
    
    def action_complete_session(self):
        """Completar sesión"""
        self.ensure_one()
        
        if not self.fluence or not self.spot_size:
            raise ValidationError(
                _('Debe ingresar al menos la fluencia y el tamaño de spot antes de completar la sesión.')
            )
        
        self.write({
            'state': 'completed',
            'end_time': fields.Datetime.now(),
        })
        
        # Registrar consumo automático de backbar
        self._register_backbar_consumption()
        
        # Enviar encuesta de satisfacción
        self._send_satisfaction_survey()
        
        return True
    
    def action_mark_no_show(self):
        """Marcar como no asistió"""
        self.write({'state': 'no_show'})
        
        # Enviar mensaje sobre política de no show
        self._send_no_show_notification()
        
        return True
    
    def _register_backbar_consumption(self):
        """Registrar consumo automático de productos backbar"""
        self.ensure_one()
        
        # Obtener productos backbar configurados para la zona
        BackbarProduct = self.env['cutai.backbar.product']
        products = BackbarProduct.search([
            ('zone_ids', 'in', self.zone_id.id),
            ('active', '=', True)
        ])
        
        BackbarConsumption = self.env['cutai.backbar.consumption']
        for product in products:
            if product.consumption_type == 'per_session':
                BackbarConsumption.create({
                    'session_id': self.id,
                    'product_id': product.product_id.id,
                    'quantity': product.default_quantity,
                    'branch_id': self.branch_id.id,
                })
    
    def _send_satisfaction_survey(self):
        """Enviar encuesta de satisfacción post-tratamiento"""
        template = self.env.ref('cutai_laser_clinic.email_template_satisfaction_survey', raise_if_not_found=False)
        if template and self.partner_id.email:
            template.send_mail(self.id, force_send=False)
    
    def _send_no_show_notification(self):
        """Enviar notificación sobre política de no show"""
        template = self.env.ref('cutai_laser_clinic.email_template_no_show_policy', raise_if_not_found=False)
        if template and self.partner_id.email:
            template.send_mail(self.id, force_send=True)
