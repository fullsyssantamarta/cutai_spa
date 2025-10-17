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
