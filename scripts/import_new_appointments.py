#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar nuevas reservas con toda la información
"""

import pandas as pd
import xmlrpc.client
from datetime import datetime, timedelta
import sys

# Configuración
ODOO_URL = 'http://localhost:10018'
ODOO_DB = 'cutai'
ODOO_USERNAME = 'admin@gmail.com'
ODOO_PASSWORD = 'Admin123'
EXCEL_FILE = '/root/reservas_28107_1760725844.xlsx'

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
        dt = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return False

def find_partner(models, uid, password, email, customer_number):
    """Buscar cliente por email o número"""
    partner_id = False
    
    if email and '@' in email:
        partner_ids = models.execute_kw(ODOO_DB, uid, password,
            'res.partner', 'search',
            [[['email', '=', email.lower()]]], {'limit': 1}
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
    
    return partner_id

def map_estado(estado):
    """Mapear estado de la reserva"""
    estado_lower = str(estado).lower().strip()
    if 'asiste' in estado_lower or 'completado' in estado_lower:
        return 'completed'
    elif 'no asiste' in estado_lower or 'no_asiste' in estado_lower:
        return 'no_show'
    elif 'confirmado' in estado_lower or 'confirmada' in estado_lower:
        return 'confirmed'
    elif 'pendiente' in estado_lower:
        return 'pending'
    elif 'cancelado' in estado_lower or 'cancelada' in estado_lower:
        return 'cancelled'
    return 'pending'

def import_appointments():
    print("=" * 80)
    print("IMPORTACIÓN DE NUEVAS RESERVAS")
    print("=" * 80)
    
    uid, models = connect_odoo()
    print(f"\nConectado a Odoo. UID: {uid}")
    
    # Preguntar si eliminar citas anteriores
    print("\n¿Deseas eliminar las citas anteriores? (s/n): ", end='')
    response = input().strip().lower()
    
    if response == 's':
        print("\nEliminando citas anteriores...")
        old_event_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
            'calendar.event', 'search',
            [[['id', '>', 1]]]
        )
        if old_event_ids:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                'calendar.event', 'unlink',
                [old_event_ids]
            )
            print(f"✓ Eliminadas {len(old_event_ids)} citas antiguas")
    
    # Leer Excel
    print(f"\nLeyendo: {EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE)
    print(f"Total de reservas: {len(df)}\n")
    
    created = 0
    skipped = 0
    errors = 0
    error_list = []
    
    print("Procesando reservas...")
    print("=" * 80)
    
    for index, row in df.iterrows():
        if (index + 1) % 100 == 0:
            print(f"[{index+1}/{len(df)}] Creadas: {created}, Omitidas: {skipped}, Errores: {errors}")
        
        try:
            # Fecha de realización (LA FECHA DE LA CITA)
            start_datetime = parse_datetime(row.get('Fecha de realización'))
            if not start_datetime:
                skipped += 1
                continue
            
            # Calcular stop (1 hora después)
            start_dt = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
            stop_datetime = (start_dt + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Buscar el cliente
            email = str(row.get('E-mail', '')).strip().lower() if pd.notna(row.get('E-mail')) else ''
            customer_number = str(int(row.get('N° de Cliente'))) if pd.notna(row.get('N° de Cliente')) else ''
            
            partner_id = find_partner(models, uid, ODOO_PASSWORD, email, customer_number)
            if not partner_id:
                skipped += 1
                continue
            
            # Preparar datos de la cita
            first_name = str(row.get('Nombre', '')).strip() if pd.notna(row.get('Nombre')) else ''
            last_name = str(row.get('Apellido', '')).strip() if pd.notna(row.get('Apellido')) else ''
            full_name = f"{first_name} {last_name}".strip()
            servicio = str(row.get('Servicio', 'Servicio')).strip() if pd.notna(row.get('Servicio')) else 'Servicio'
            
            event_vals = {
                'name': f"{servicio} - {full_name}",
                'start': start_datetime,
                'stop': stop_datetime,
                'partner_id': partner_id,  # Cliente principal
                'partner_ids': [(6, 0, [partner_id])],  # Asistentes
                'allday': False,
            }
            
            # Estado
            estado = str(row.get('Estado', '')).strip() if pd.notna(row.get('Estado')) else ''
            if estado:
                event_vals['appointment_state'] = map_estado(estado)
            
            # Prestador/Terapeuta
            prestador = str(row.get('Prestador', '')).strip() if pd.notna(row.get('Prestador')) else ''
            if prestador:
                event_vals['attendant_name'] = prestador
            
            # Precios
            try:
                precio_lista = row.get('Precio lista')
                if pd.notna(precio_lista) and float(precio_lista) > 0:
                    event_vals['list_price'] = float(precio_lista)
                
                precio_real = row.get('Precio real')
                if pd.notna(precio_real) and float(precio_real) > 0:
                    event_vals['real_price'] = float(precio_real)
            except:
                pass
            
            # Sesiones
            try:
                num_sesion = row.get('Nº de sesión')
                if pd.notna(num_sesion) and int(num_sesion) > 0:
                    event_vals['session_number'] = int(num_sesion)
                
                sesiones_totales = row.get('Sesiones Totales')
                if pd.notna(sesiones_totales) and int(sesiones_totales) > 0:
                    event_vals['total_sessions'] = int(sesiones_totales)
            except:
                pass
            
            # Estado de pago
            estado_pago = str(row.get('Estado de pago', '')).strip() if pd.notna(row.get('Estado de pago')) else ''
            if estado_pago:
                if 'pago' in estado_pago.lower() or 'pagado' in estado_pago.lower():
                    event_vals['payment_status'] = 'paid'
                else:
                    event_vals['payment_status'] = 'pending'
            
            # Referencia de pago
            id_pago = row.get('ID pago')
            if pd.notna(id_pago):
                event_vals['payment_reference'] = str(int(id_pago))
            
            # Comentarios
            comentario = str(row.get('Comentario interno', '')).strip() if pd.notna(row.get('Comentario interno')) else ''
            if comentario and comentario not in ['Sin Preferencia', 'Manual']:
                event_vals['description'] = comentario[:2000]
            
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
                error_msg = str(e)
                if 'Traceback' in error_msg:
                    lines = error_msg.split('\n')
                    error_msg = lines[-2] if len(lines) > 1 else error_msg
                error_list.append(f"Fila {index+1}: {error_msg[:150]}")
    
    print("\n" + "=" * 80)
    print("RESUMEN:")
    print(f"  Citas creadas: {created}")
    print(f"  Omitidas (sin cliente): {skipped}")
    print(f"  Errores: {errors}")
    
    if error_list:
        print(f"\nPrimeros errores:")
        for error in error_list:
            print(f"  - {error}")
    
    print("=" * 80)

if __name__ == '__main__':
    import_appointments()
