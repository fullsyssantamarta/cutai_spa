# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'
    
    # Campos relacionados con tratamientos láser
    phototype = fields.Selection([
        ('1', 'Tipo I - Muy blanca'),
        ('2', 'Tipo II - Blanca'),
        ('3', 'Tipo III - Media'),
        ('4', 'Tipo IV - Morena clara'),
        ('5', 'Tipo V - Morena'),
        ('6', 'Tipo VI - Negra'),
    ], string='Fototipo', help='Clasificación del color de piel según Fitzpatrick')
    
    active_zones = fields.Many2many(
        'cutai.zone',
        'cutai_partner_zone_rel',
        'partner_id',
        'zone_id',
        string='Zonas Activas de Tratamiento'
    )
    
    uses_contraceptives = fields.Boolean(
        string='Usa Anticonceptivos/Hormonas',
        help='Indica si la clienta usa anticonceptivos u hormonas'
    )
    
    has_pcos = fields.Boolean(
        string='SOP (Síndrome de Ovario Poliquístico)',
        help='Marca si la clienta tiene diagnóstico de SOP'
    )
    
    consent_valid = fields.Boolean(
        string='Consentimiento Vigente',
        compute='_compute_consent_valid',
        store=True,
        help='Indica si el consentimiento informado está vigente'
    )
    
    consent_date = fields.Date(
        string='Fecha Último Consentimiento',
        help='Fecha del último consentimiento informado firmado'
    )
    
    consent_document_id = fields.Many2one(
        'documents.document',
        string='Documento de Consentimiento',
        help='Documento digital del consentimiento firmado'
    )
    
    allergy_info = fields.Text(
        string='Alergias y Contraindicaciones',
        help='Información sobre alergias conocidas y contraindicaciones médicas'
    )
    
    # Relaciones con otros módulos CUTAI
    membership_ids = fields.One2many(
        'cutai.membership',
        'partner_id',
        string='Membresías'
    )
    
    active_membership_id = fields.Many2one(
        'cutai.membership',
        string='Membresía Activa',
        compute='_compute_active_membership',
        store=True
    )
    
    # Campos relacionados de membresía para mostrar en perfil
    membership_cycle = fields.Selection(
        related='active_membership_id.cycle',
        string='Ciclo Actual',
        readonly=True
    )
    
    membership_next_charge = fields.Date(
        related='active_membership_id.next_charge_date',
        string='Próximo Cobro',
        readonly=True
    )
    
    membership_late_fees = fields.Monetary(
        related='active_membership_id.accumulated_late_fees',
        string='Moras Acumuladas',
        currency_field='currency_id',
        readonly=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    
    membership_is_frozen = fields.Boolean(
        related='active_membership_id.is_frozen',
        string='Membresía Congelada',
        readonly=True
    )
    
    membership_freeze_reason = fields.Text(
        related='active_membership_id.freeze_reason',
        string='Motivo de Congelamiento',
        readonly=True
    )
    
    treatment_ids = fields.One2many(
        'cutai.treatment',
        'partner_id',
        string='Tratamientos'
    )
    
    session_ids = fields.One2many(
        'cutai.session',
        'partner_id',
        string='Sesiones de Tratamiento'
    )
    
    total_sessions_count = fields.Integer(
        string='Total de Sesiones',
        compute='_compute_sessions_count'
    )
    
    last_appointment_date = fields.Datetime(
        string='Última Cita',
        compute='_compute_last_appointment'
    )
    
    next_appointment_date = fields.Datetime(
        string='Próxima Cita',
        compute='_compute_next_appointment'
    )
    
    is_cutai_client = fields.Boolean(
        string='Cliente CUTAI',
        default=False,
        help='Marca este cliente como cliente de CUTAI'
    )
    
    instagram_account = fields.Char(
        string='Cuenta de Instagram',
        help='Usuario de Instagram del cliente (sin @)'
    )
    
    birthdate = fields.Date(
        string='Fecha de Nacimiento',
        help='Fecha de nacimiento del cliente'
    )
    
    age = fields.Integer(
        string='Edad',
        compute='_compute_age',
        store=False,
        help='Edad calculada a partir de la fecha de nacimiento'
    )
    
    total_appointments = fields.Integer(
        string='Total de Reservas',
        compute='_compute_appointments_count',
        store=True
    )
    
    cancelled_appointments = fields.Integer(
        string='Reservas Canceladas',
        compute='_compute_appointments_count',
        store=True
    )
    
    completed_appointments = fields.Integer(
        string='Reservas Completadas',
        compute='_compute_appointments_count',
        store=True
    )
    
    # ==================== PROMOCIONES ====================
    has_promotion = fields.Boolean(
        string='Tiene Promoción',
        default=False,
        help='Indica si el cliente tiene una promoción activa'
    )
    
    promotion_name = fields.Char(
        string='Nombre de Promoción',
        help='Descripción de la promoción activa'
    )
    
    promotion_expiry = fields.Date(
        string='Vencimiento Promoción',
        help='Fecha de vencimiento de la promoción'
    )
    
    @api.depends('consent_date')
    def _compute_consent_valid(self):
        for partner in self:
            if partner.consent_date:
                # Considerar válido si tiene menos de 1 año
                from datetime import date, timedelta
                one_year_ago = date.today() - timedelta(days=365)
                partner.consent_valid = partner.consent_date >= one_year_ago
            else:
                partner.consent_valid = False
    
    @api.depends('membership_ids.state')
    def _compute_active_membership(self):
        for partner in self:
            active_membership = partner.membership_ids.filtered(
                lambda m: m.state == 'active'
            )
            partner.active_membership_id = active_membership[:1] if active_membership else False
    
    def _compute_appointments_count(self):
        """Calcular estadísticas de citas"""
        for partner in self:
            try:
                appointments = self.env['calendar.event'].search([
                    ('partner_ids', 'in', [partner.id])
                ])
                partner.total_appointments = len(appointments)
                partner.cancelled_appointments = len(appointments.filtered(
                    lambda a: a.appointment_state == 'cancelled'
                ))
                partner.completed_appointments = len(appointments.filtered(
                    lambda a: a.appointment_state == 'attended'
                ))
            except Exception:
                partner.total_appointments = 0
                partner.cancelled_appointments = 0
                partner.completed_appointments = 0
    
    @api.depends('birthdate')
    def _compute_age(self):
        """Calcular edad del cliente a partir de la fecha de nacimiento"""
        from datetime import date
        for partner in self:
            if partner.birthdate:
                today = date.today()
                partner.age = today.year - partner.birthdate.year - (
                                        (today.month, today.day) < (partner.birthdate.month, partner.birthdate.day)
                )
            else:
                partner.age = 0
    
    def get_sessions_by_zone(self):
        """Obtener historial de sesiones agrupadas por zona"""
        self.ensure_one()
        
        sessions_by_zone = {}
        sessions = self.env['cutai.session'].search([
            ('partner_id', '=', self.id),
            ('state', '=', 'completed')
        ], order='zone_id, session_date')
        
        for session in sessions:
            zone_name = session.zone_id.name if session.zone_id else 'Sin zona'
            if zone_name not in sessions_by_zone:
                sessions_by_zone[zone_name] = []
            
            sessions_by_zone[zone_name].append({
                'session_number': session.session_number_by_zone,
                'date': session.session_date,
                'branch': session.branch_id.name,
                'attendant': session.attendant_id.name,
                'fluence': session.fluence,
                'spot_size': session.spot_size,
                'notes': session.post_treatment_notes,
                'reduction': session.hair_reduction_percentage,
            })
        
        return sessions_by_zone
    
    def action_view_session_history(self):
        """Abrir vista de historial de sesiones por zona"""
        self.ensure_one()
        
        # Obtener el ID de la vista especial de historial
        tree_view = self.env.ref('cutai_laser_clinic.view_cutai_session_history_tree', raise_if_not_found=False)
        
        return {
            'name': f'Historial de Sesiones - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'cutai.session',
            'view_mode': 'tree,form',
            'views': [(tree_view.id if tree_view else False, 'tree'), (False, 'form')],
            'domain': [('partner_id', '=', self.id), ('state', '=', 'completed')],
            'context': {
                'default_partner_id': self.id,
                'group_by': ['zone_id'],
                'search_default_group_zone': 1,
            },
            'target': 'current',
        }
    
    @api.constrains('phototype', 'active_zones')
    def _check_treatment_suitability(self):
        """Validar que el fototipo sea compatible con tratamiento láser"""
        for partner in self:
            if partner.phototype == '6' and partner.active_zones:
                raise ValidationError(
                    _('Advertencia: Los fototipos VI requieren evaluación médica especializada '
                      'antes de iniciar tratamientos láser. Por favor consulte con el médico responsable.')
                )
    
    @api.depends('session_ids')
    def _compute_sessions_count(self):
        for partner in self:
            partner.total_sessions_count = len(partner.session_ids)
    
    @api.depends('session_ids.appointment_id.start')
    def _compute_last_appointment(self):
        for partner in self:
            past_sessions = partner.session_ids.filtered(
                lambda s: s.appointment_id and s.appointment_id.start < fields.Datetime.now()
            ).sorted('appointment_id.start', reverse=True)
            partner.last_appointment_date = past_sessions[0].appointment_id.start if past_sessions else False
    
    @api.depends('session_ids.appointment_id.start')
    def _compute_next_appointment(self):
        for partner in self:
            future_sessions = partner.session_ids.filtered(
                lambda s: s.appointment_id and s.appointment_id.start >= fields.Datetime.now()
            ).sorted('appointment_id.start')
            partner.next_appointment_date = future_sessions[0].appointment_id.start if future_sessions else False
    
    @api.constrains('phototype', 'active_zones')
    def _check_treatment_suitability(self):
        """Validar que el fototipo sea compatible con tratamiento láser"""
        for partner in self:
            if partner.phototype == '6' and partner.active_zones:
                raise ValidationError(
                    _('Advertencia: Los fototipos VI requieren evaluación médica especializada '
                      'antes de iniciar tratamientos láser. Por favor consulte con el médico responsable.')
                )
