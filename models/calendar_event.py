# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'
    
    # ==================== INFORMACIÓN DE CLIENTE ====================
    client_number = fields.Char(
        string='N° de Cliente',
        related='partner_id.ref',
        store=True
    )
    
    client_first_name = fields.Char(
        string='Nombre',
        compute='_compute_client_names',
        store=True
    )
    
    client_last_name = fields.Char(
        string='Apellido',
        compute='_compute_client_names',
        store=True
    )
    
    client_email = fields.Char(
        string='E-mail',
        related='partner_id.email',
        store=True
    )
    
    client_phone = fields.Char(
        string='Teléfono',
        related='partner_id.phone',
        store=True
    )
    
    client_vat = fields.Char(
        string='Cédula',
        related='partner_id.vat',
        store=True
    )
    
    # ==================== FECHAS Y RESPONSABLES ====================
    realization_date = fields.Datetime(
        string='Fecha de realización',
        compute='_compute_realization_date',
        store=True,
        help='Fecha en que se realizó la cita'
    )
    
    # create_date, create_uid, write_date, write_uid ya existen en el modelo base
    
    # ==================== UBICACIÓN Y RECURSOS ====================
    branch_id = fields.Many2one(
        'cutai.branch',
        string='Local',
        tracking=True
    )
    
    cabin_id = fields.Many2one(
        'cutai.cabin',
        string='Cabina',
        tracking=True
    )
    
    machine_id = fields.Many2one(
        'cutai.machine',
        string='Máquina Láser',
        tracking=True
    )
    
    attendant_id = fields.Many2one(
        'res.users',
        string='Prestador',
        tracking=True,
        help='Terapeuta o profesional responsable'
    )
    
    # ==================== SERVICIO Y PRECIOS ====================
    main_service_id = fields.Many2one(
        'cutai.service',
        string='Servicio',
        tracking=True
    )
    
    service_ids = fields.One2many(
        'cutai.appointment.service',
        'appointment_id',
        string='Servicios'
    )
    
    list_price = fields.Float(
        string='Precio lista',
        compute='_compute_prices',
        store=True
    )
    
    real_price = fields.Float(
        string='Precio real',
        compute='_compute_prices',
        store=True
    )
    
    # ==================== SESIONES Y TRATAMIENTO ====================
    session_number = fields.Integer(
        string='Nº de sesión',
        help='Número de sesión actual'
    )
    
    total_sessions = fields.Integer(
        string='Sesiones Totales'
    )
    
    session_id = fields.Many2one(
        'cutai.session',
        string='Sesión Láser'
    )
    
    treatment_id = fields.Many2one(
        'cutai.treatment',
        string='Tratamiento'
    )
    
    zone_id = fields.Many2one(
        'cutai.zone',
        string='Zona'
    )
    
    # ==================== ESTADO Y PAGOS ====================
    appointment_state = fields.Selection([
        ('scheduled', 'Programada'),
        ('confirmed', 'Confirmada'),
        ('in_progress', 'En Progreso'),
        ('done', 'Completada'),
        ('no_show', 'No Asistió'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='scheduled', tracking=True)
    
    payment_status = fields.Selection([
        ('pending', 'Pendiente'),
        ('partial', 'Parcial'),
        ('paid', 'Pagado'),
        ('refunded', 'Reembolsado'),
    ], string='Estado de pago', default='pending', tracking=True)
    
    payment_date = fields.Date(
        string='Fecha pago',
        tracking=True
    )
    
    payment_id = fields.Char(
        string='ID pago'
    )
    
    # ==================== NOTAS Y COMENTARIOS ====================
    shared_notes = fields.Text(
        string='Notas compartidas con cliente'
    )
    
    internal_notes = fields.Text(
        string='Comentario interno'
    )
    
    client_preference = fields.Text(
        string='Preferencia Cliente'
    )
    
    # ==================== ORIGEN ====================
    origin = fields.Selection([
        ('web', 'Sitio Web'),
        ('phone', 'Teléfono'),
        ('whatsapp', 'WhatsApp'),
        ('walk_in', 'Walk-in'),
        ('referral', 'Referido'),
        ('social_media', 'Redes Sociales'),
        ('email', 'Email'),
        ('app', 'App Móvil'),
        ('other', 'Otro'),
    ], string='Origen', tracking=True)
    
    # ==================== WHATSAPP ====================
    whatsapp_notification_sent = fields.Boolean(
        string='Notificación WhatsApp Enviada',
        default=False
    )
    
    whatsapp_reminder_48h_sent = fields.Boolean(
        string='Recordatorio 48h WhatsApp',
        default=False
    )
    
    whatsapp_reminder_24h_sent = fields.Boolean(
        string='Recordatorio 24h WhatsApp',
        default=False
    )
    
    whatsapp_reminder_3h_sent = fields.Boolean(
        string='Recordatorio 3h WhatsApp',
        default=False
    )
    
    # ==================== CAMPOS COMPUTADOS ====================
    
    @api.depends('partner_id', 'partner_id.name')
    def _compute_client_names(self):
        for record in self:
            if record.partner_id and record.partner_id.name:
                name_parts = record.partner_id.name.split(' ', 1)
                record.client_first_name = name_parts[0] if name_parts else ''
                record.client_last_name = name_parts[1] if len(name_parts) > 1 else ''
            else:
                record.client_first_name = ''
                record.client_last_name = ''
    
    @api.depends('appointment_state', 'stop')
    def _compute_realization_date(self):
        for record in self:
            if record.appointment_state == 'done' and record.stop:
                record.realization_date = record.stop
            else:
                record.realization_date = False
    
    @api.depends('main_service_id', 'service_ids')
    def _compute_prices(self):
        for record in self:
            if record.main_service_id:
                record.list_price = record.main_service_id.price
                record.real_price = record.main_service_id.price
            elif record.service_ids:
                record.list_price = sum(record.service_ids.mapped('price_unit'))
                record.real_price = sum(record.service_ids.mapped('price_unit'))
            else:
                record.list_price = 0.0
                record.real_price = 0.0
    
    # ==================== MÉTODOS DE WHATSAPP ====================
    
    def send_whatsapp_notification(self, template_type='confirmation'):
        """
        Envía notificación por WhatsApp usando el módulo whatsapp_fullsys
        """
        self.ensure_one()
        
        if not self.partner_id or not self.partner_id.phone:
            _logger.warning(f"No se puede enviar WhatsApp para cita {self.id}: sin teléfono")
            return False
        
        # Buscar el módulo de WhatsApp
        WhatsappMessage = self.env.get('whatsapp.message')
        if not WhatsappMessage:
            _logger.warning("Módulo whatsapp_fullsys no instalado")
            return False
        
        # Preparar mensaje según el tipo
        messages = {
            'confirmation': self._get_whatsapp_confirmation_message(),
            'reminder_48h': self._get_whatsapp_reminder_message(48),
            'reminder_24h': self._get_whatsapp_reminder_message(24),
            'reminder_3h': self._get_whatsapp_reminder_message(3),
        }
        
        message_text = messages.get(template_type, messages['confirmation'])
        
        try:
            # Crear y enviar mensaje de WhatsApp
            whatsapp_msg = WhatsappMessage.create({
                'partner_id': self.partner_id.id,
                'phone': self.partner_id.phone,
                'message': message_text,
                'model': 'calendar.event',
                'res_id': self.id,
            })
            
            whatsapp_msg.send_message()
            
            # Marcar como enviado
            if template_type == 'confirmation':
                self.whatsapp_notification_sent = True
            elif template_type == 'reminder_48h':
                self.whatsapp_reminder_48h_sent = True
            elif template_type == 'reminder_24h':
                self.whatsapp_reminder_24h_sent = True
            elif template_type == 'reminder_3h':
                self.whatsapp_reminder_3h_sent = True
            
            _logger.info(f"WhatsApp enviado para cita {self.id} - tipo: {template_type}")
            return True
            
        except Exception as e:
            _logger.error(f"Error enviando WhatsApp para cita {self.id}: {str(e)}")
            return False
    
    def _get_whatsapp_confirmation_message(self):
        """Mensaje de confirmación de cita"""
        service_name = self.main_service_id.name if self.main_service_id else 'Servicio SPA'
        date_str = fields.Datetime.context_timestamp(self, self.start).strftime('%d/%m/%Y %H:%M')
        branch_name = self.branch_id.name if self.branch_id else 'nuestra clínica'
        
        return f"""¡Hola {self.client_first_name}! 👋

✅ Tu cita ha sido confirmada:

📅 Fecha: {date_str}
💆 Servicio: {service_name}
🏢 Local: {branch_name}
💰 Precio: ${self.real_price:.2f}

{self.shared_notes if self.shared_notes else ''}

¿Necesitas cancelar o reagendar? Contáctanos con anticipación.

¡Te esperamos! 🌟"""
    
    def _get_whatsapp_reminder_message(self, hours_before):
        """Mensaje de recordatorio"""
        service_name = self.main_service_id.name if self.main_service_id else 'Servicio SPA'
        date_str = fields.Datetime.context_timestamp(self, self.start).strftime('%d/%m/%Y %H:%M')
        branch_name = self.branch_id.name if self.branch_id else 'nuestra clínica'
        
        time_text = f"{hours_before} horas" if hours_before > 3 else f"{hours_before} horas"
        
        return f"""¡Hola {self.client_first_name}! 🔔

⏰ Recordatorio: Tu cita es en {time_text}

📅 Fecha: {date_str}
💆 Servicio: {service_name}
🏢 Local: {branch_name}

{self.shared_notes if self.shared_notes else ''}

¡Te esperamos! 😊"""
    
    # ==================== HOOKS Y ACCIONES ====================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create para enviar WhatsApp al crear cita"""
        events = super().create(vals_list)
        
        for event in events:
            if event.partner_id and event.partner_id.phone:
                # Enviar notificación de confirmación por WhatsApp
                event.send_whatsapp_notification('confirmation')
        
        return events
    
    def write(self, vals):
        """Override write para detectar cambios y notificar"""
        result = super().write(vals)
        
        # Si cambia la fecha, reenviar recordatorios
        if 'start' in vals or 'stop' in vals:
            for record in self:
                record.write({
                    'whatsapp_reminder_48h_sent': False,
                    'whatsapp_reminder_24h_sent': False,
                    'whatsapp_reminder_3h_sent': False,
                })
        
        return result
    
    def action_confirm_appointment(self):
        """Confirmar cita"""
        self.write({'appointment_state': 'confirmed'})
        return True
    
    def action_start_appointment(self):
        """Iniciar cita"""
        self.write({'appointment_state': 'in_progress'})
        return True
    
    def action_complete_appointment(self):
        """Completar cita"""
        self.write({
            'appointment_state': 'done',
            'realization_date': fields.Datetime.now()
        })
        return True
    
    def action_mark_no_show(self):
        """Marcar como no asistió"""
        self.write({'appointment_state': 'no_show'})
        return True
    
    def action_cancel_appointment(self):
        """Cancelar cita"""
        self.write({'appointment_state': 'cancelled'})
        return True
