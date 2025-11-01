# -*- coding: utf-8 -*-
{
    'name': 'CUTAI Laser Spa Management',
    'version': '18.0.1.0.8',
    'category': 'Services',
    'summary': 'Sistema completo de gestión para SPA y clínica de depilación láser',
    'description': """
        Sistema integral para gestión de SPA láser y clínica estética que incluye:
        - Gestión de clientes con historial médico y estético completo
        - Membresías con control de pagos, mora y congelamiento
        - Tratamientos láser con seguimiento de sesiones y parámetros técnicos
        - Servicios SPA: faciales, corporales, masajes, tratamientos estéticos
        - Paquetes y combos de servicios
        - Inventario retail y backbar (productos de venta y consumo interno)
        - Agenda inteligente con control de ocupación por cabina y terapeuta
        - Consentimientos electrónicos y contratos digitales
        - Comisiones para terapeutas y operadores
        - Propinas y caja diaria
        - Reportes y KPI por sucursal, terapeuta y servicio
        - Integración con WhatsApp para recordatorios, confirmaciones y seguimiento
        - Control de inventario con alertas de stock mínimo
        - Facturación y punto de venta integrado
    """,
    'author': 'FullSys Tecnología Santa Marta',
    'website': 'https://www.fullsys.com.co',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'sale_management',
        'crm',
        'calendar',
        'stock',
        'account',
        'contacts',
        'hr',
        'hr_expense',
        'documents',
        'sign',
        'sms',
        'point_of_sale',
        'whatsapp_fullsys',
    ],
    'data': [
        # Seguridad
        'security/cutai_security.xml',
        'security/ir.model.access.csv',
        
        # Datos maestros
        'data/cutai_data_clean.xml',
        #'data/cutai_data.xml',
        #'data/email_templates.xml',
        #'data/sms_templates.xml',
        
        # Vistas - Clientes
        'views/res_partner_views.xml',
        
        # Vistas - Tratamientos
        'views/cutai_treatment_views.xml',
        'views/cutai_session_views.xml',
        
        # Vistas - Membresías
        'views/cutai_membership_views.xml',
        'views/cutai_membership_payment_views.xml',
        
        # Vistas - Citas
        'views/calendar_event_views.xml',
        
        # Vistas - Servicios SPA
        'views/cutai_service_views.xml',
        'views/cutai_service_category_views.xml',
        'views/cutai_package_views.xml',
        
        # Vistas - Retail
        'views/cutai_retail_sale_views.xml',
        'views/cutai_product_brand_views.xml',
        
        # Vistas - Citas Extendidas
        'views/cutai_appointment_service_views.xml',
        
        # Vistas - Inventario
        'views/cutai_backbar_views.xml',
        'views/stock_inventory_views.xml',
        
        # Vistas - Configuración
        'views/cutai_config_views.xml',
        'views/cutai_zone_views.xml',
        'views/cutai_machine_views.xml',
        'views/cutai_cabin_views.xml',
        'views/cutai_branch_views.xml',
        'views/cutai_promotion_views.xml',
        
        # Documentos y Contratos
        'views/cutai_consent_views.xml',
        
        # Reportes
        'report/cutai_reports.xml',
        'report/cutai_daily_report_template.xml',
        'report/cutai_monthly_report_template.xml',
        
        # Dashboards
        'views/cutai_dashboard_views.xml',
        
        # Menús
        'views/cutai_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cutai_laser_clinic/static/src/css/cutai_dashboard.css',
            'cutai_laser_clinic/static/src/js/cutai_dashboard.js',
        ],
    },
    'demo': [
        'demo/cutai_demo.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
