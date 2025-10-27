#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar reservas como citas agendadas en calendar.event
"""

import pandas as pd
import xmlrpc.client
from datetime import datetime
import sys

# Configuración
ODOO_URL = 'http://localhost:10018'
ODOO_DB = 'cutai'
ODOO_USERNAME = 'admin@gmail.com'
ODOO_PASSWORD = 'Admin123'
EXCEL_FILE = '/root/reservas_28107_1760495806.xlsx'

def connect_odoo():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        print("Error: No se pudo autenticar")
        sys.exit(1)
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    return uid, models

def parse_datetime(date_str):
    """Convertir fecha del formato DD/MM/YYYY HH:MM a formato Odoo"""
    if pd.isna(date_str):
        return False
    try:
        date_str = str(date_str).strip()
        # Intentar formato DD/MM/YYYY HH:MM
        dt = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        try:
            # Intentar solo fecha DD/MM/YYYY
            dt = datetime.strptime(date_str, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d 09:00:00')
        except:
            return False

def clean_phone(phone):
    if pd.isna(phone):
        return False
    phone_str = str(phone).strip()
    phone_str = ''.join(c for c in phone_str if c.isdigit() or c == '+')
    return phone_str if phone_str and phone_str != '+' else False

def get_or_create_partner(models, uid, password, row):
    """Buscar o crear el cliente asociado a la reserva"""
    email = str(row.get('E-mail', '')).strip().lower() if pd.notna(row.get('E-mail')) else ''
    customer_number = str(int(row.get('N° de Cliente'))) if pd.notna(row.get('N° de Cliente')) else ''
    first_name = str(row.get('Nombre', '')).strip() if pd.notna(row.get('Nombre')) else ''
    last_name = str(row.get('Apellido', '')).strip() if pd.notna(row.get('Apellido')) else ''
    
    # Buscar por email o número de cliente
    partner_id = False
    if email and '@' in email:
        partner_ids = models.execute_kw(ODOO_DB, uid, password,
            'res.partner', 'search',
            [[['email', '=', email]]], {'limit': 1}
        )
        if partner_ids:
            partner_id = partner_ids[0]
    
    if not partner_id and customer_number:
        partner_ids = models.execute_kw(ODOO_DB, uid, password,
            'res.partner', 'search',
            [[['ref', '=', customer_number]]], {'limit': 1}
        )
        if partner_ids:
            partner_id = partner_ids[0]
    
    # Si no existe, crear el cliente
    if not partner_id:
        name_parts = [p for p in [first_name, last_name] if p]
        full_name = ' '.join(name_parts) if name_parts else 'Cliente sin nombre'
        
        partner_vals = {
            'name': full_name,
            'customer_rank': 1,
            'is_company': False,
        }
        
        if email and '@' in email:
            partner_vals['email'] = email
        
        phone = clean_phone(row.get('Teléfono'))
        if phone:
            partner_vals['phone'] = phone
        
        if customer_number:
            partner_vals['ref'] = customer_number
        
        try:
            partner_id = models.execute_kw(ODOO_DB, uid, password,
                'res.partner', 'create', [partner_vals]
            )
        except:
            return False
    
    return partner_id

def map_estado(estado):
    """Mapear estado de la reserva al estado de la cita"""
    estado_map = {
        'Asiste': 'completed',
        'No Asiste': 'no_show',
        'Confirmado': 'confirmed',
        'Pendiente': 'pending',
    }
    return estado_map.get(estado, 'pending')

def import_appointments():
    print("=" * 80)
    print("IMPORTACIÓN DE RESERVAS/CITAS")
    print("=" * 80)
    
    uid, models = connect_odoo()
    print(f"\nConectado a Odoo. UID: {uid}")
    
    # Leer Excel
    print(f"\nLeyendo: {EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE)
    print(f"Total de reservas: {len(df)}\n")
    
    created = 0
    errors = 0
    error_list = []
    
    print("Procesando reservas...")
    print("=" * 80)
    
    for index, row in df.iterrows():
        if (index + 1) % 100 == 0:
            print(f"[{index+1}/{len(df)}] Creadas: {created}, Errores: {errors}")
        
        try:
            # Fecha de realización (obligatoria)
            start_datetime = parse_datetime(row.get('Fecha de realización'))
            if not start_datetime:
                errors += 1
                if len(error_list) < 10:
                    error_list.append(f"Fila {index+1}: Fecha inválida")
                continue
            
            # Buscar o crear el cliente
            partner_id = get_or_create_partner(models, uid, ODOO_PASSWORD, row)
            if not partner_id:
                errors += 1
                if len(error_list) < 10:
                    error_list.append(f"Fila {index+1}: No se pudo crear/encontrar cliente")
                continue
            
            # Preparar datos de la cita
            first_name = str(row.get('Nombre', '')).strip() if pd.notna(row.get('Nombre')) else ''
            last_name = str(row.get('Apellido', '')).strip() if pd.notna(row.get('Apellido')) else ''
            full_name = f"{first_name} {last_name}".strip()
            servicio = str(row.get('Servicio', 'Servicio')).strip() if pd.notna(row.get('Servicio')) else 'Servicio'
            
            event_vals = {
                'name': f"{servicio} - {full_name}",
                'start': start_datetime,
                'stop': start_datetime,  # Duración 1 hora por defecto
                'partner_ids': [(6, 0, [partner_id])],
                'allday': False,
            }
            
            # Estado
            estado = str(row.get('Estado', '')).strip() if pd.notna(row.get('Estado')) else ''
            if estado:
                event_vals['state'] = map_estado(estado)
            
            # Precios
            precio_lista = row.get('Precio lista')
            if pd.notna(precio_lista):
                event_vals['list_price'] = float(precio_lista)
            
            precio_real = row.get('Precio real')
            if pd.notna(precio_real):
                event_vals['real_price'] = float(precio_real)
            
            # Sesiones
            num_sesion = row.get('Nº de sesión')
            if pd.notna(num_sesion):
                event_vals['session_number'] = int(num_sesion)
            
            sesiones_totales = row.get('Sesiones Totales')
            if pd.notna(sesiones_totales):
                event_vals['total_sessions'] = int(sesiones_totales)
            
            # Estado de pago
            estado_pago = str(row.get('Estado de pago', '')).strip() if pd.notna(row.get('Estado de pago')) else ''
            payment_reference = ''
            id_pago = row.get('ID pago')
            if pd.notna(id_pago):
                payment_reference = str(int(id_pago))
            
            if estado_pago and payment_reference:
                if 'Pago' in estado_pago or 'pagado' in estado_pago.lower():
                    event_vals['payment_status'] = 'paid'
                    event_vals['payment_reference'] = payment_reference
                elif 'No' in estado_pago:
                    event_vals['payment_status'] = 'pending'
            
            # Notas y comentarios
            comentario = str(row.get('Comentario interno', '')).strip() if pd.notna(row.get('Comentario interno')) else ''
            
            if comentario and comentario not in ['Sin Preferencia', 'Manual']:
                event_vals['description'] = comentario[:2000]  # Limitar longitud
            
            # Crear la cita
            event_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'calendar.event', 'create',
                [event_vals]
            )
            created += 1
            
        except Exception as e:
            errors += 1
            if len(error_list) < 10:
                error_list.append(f"Fila {index+1}: {str(e)[:100]}")
    
    print("\n" + "=" * 80)
    print("RESUMEN:")
    print(f"  Citas creadas: {created}")
    print(f"  Errores: {errors}")
    
    if error_list:
        print(f"\nPrimeros errores:")
        for error in error_list:
            print(f"  - {error}")
    
    print("=" * 80)

if __name__ == '__main__':
    import_appointments()
