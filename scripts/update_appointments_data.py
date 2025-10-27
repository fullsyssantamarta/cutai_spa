#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar información adicional de las citas desde Excel
"""

import pandas as pd
import xmlrpc.client
from datetime import datetime

# Configuración
ODOO_URL = 'http://localhost:10018'
ODOO_DB = 'cutai'
ODOO_USERNAME = 'admin@gmail.com'
ODOO_PASSWORD = 'Admin123'
EXCEL_FILE = '/root/reservas_28107_1760495806.xlsx'

def connect_odoo():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    return uid, models

def parse_datetime(date_str):
    if pd.isna(date_str):
        return False
    try:
        date_str = str(date_str).strip()
        dt = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return False

def map_estado(estado):
    """Mapear estado de la reserva"""
    estado_lower = str(estado).lower().strip()
    if 'asiste' in estado_lower:
        return 'completed'
    elif 'no asiste' in estado_lower or 'no_asiste' in estado_lower:
        return 'no_show'
    elif 'confirmado' in estado_lower:
        return 'confirmed'
    elif 'pendiente' in estado_lower:
        return 'pending'
    return 'pending'

def main():
    print("=" * 80)
    print("ACTUALIZACIÓN DE DATOS ADICIONALES DE CITAS")
    print("=" * 80)
    
    uid, models = connect_odoo()
    print(f"\nConectado. UID: {uid}")
    
    df = pd.read_excel(EXCEL_FILE)
    print(f"Total: {len(df)} registros en Excel\n")
    
    updated = 0
    errors = 0
    
    for index, row in df.iterrows():
        if (index + 1) % 100 == 0:
            print(f"[{index+1}/{len(df)}] Actualizadas: {updated}, Errores: {errors}")
        
        try:
            start_dt = parse_datetime(row.get('Fecha de realización'))
            if not start_dt:
                continue
            
            email = str(row.get('E-mail', '')).strip().lower() if pd.notna(row.get('E-mail')) else ''
            if not email or '@' not in email:
                continue
            
            # Buscar la cita por fecha y email del partner
            event_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                'calendar.event', 'search',
                [[['start', '=', start_dt], ['partner_id.email', '=', email]]],
                {'limit': 1}
            )
            
            if not event_ids:
                errors += 1
                continue
            
            # Preparar datos para actualizar
            update_vals = {}
            
            # Estado
            estado = str(row.get('Estado', '')).strip() if pd.notna(row.get('Estado')) else ''
            if estado:
                update_vals['appointment_state'] = map_estado(estado)
            
            # Precios
            precio_lista = row.get('Precio lista')
            if pd.notna(precio_lista) and float(precio_lista) > 0:
                update_vals['list_price'] = float(precio_lista)
            
            precio_real = row.get('Precio real')
            if pd.notna(precio_real) and float(precio_real) > 0:
                update_vals['real_price'] = float(precio_real)
            
            # Sesiones
            num_sesion = row.get('Nº de sesión')
            if pd.notna(num_sesion):
                update_vals['session_number'] = int(num_sesion)
            
            sesiones_totales = row.get('Sesiones Totales')
            if pd.notna(sesiones_totales):
                update_vals['total_sessions'] = int(sesiones_totales)
            
            # Estado de pago
            estado_pago = str(row.get('Estado de pago', '')).strip() if pd.notna(row.get('Estado de pago')) else ''
            id_pago = row.get('ID pago')
            
            if estado_pago:
                if 'pago' in estado_pago.lower():
                    update_vals['payment_status'] = 'paid'
                    if pd.notna(id_pago):
                        update_vals['payment_reference'] = str(int(id_pago))
                elif 'no' in estado_pago.lower():
                    update_vals['payment_status'] = 'pending'
            
            # Comentarios internos
            comentario = str(row.get('Comentario interno', '')).strip() if pd.notna(row.get('Comentario interno')) else ''
            if comentario and comentario not in ['Sin Preferencia', 'Manual']:
                update_vals['description'] = comentario[:2000]
            
            # Origen
            origen = str(row.get('Origen', '')).strip() if pd.notna(row.get('Origen')) else ''
            if origen:
                update_vals['origin'] = origen
            
            # Actualizar la cita
            if update_vals:
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'calendar.event', 'write',
                    [[event_ids[0]], update_vals]
                )
                updated += 1
            
        except Exception as e:
            errors += 1
            if errors <= 10:
                print(f"  Error fila {index+1}: {str(e)[:100]}")
    
    print("\n" + "=" * 80)
    print(f"  Citas actualizadas: {updated}")
    print(f"  Errores: {errors}")
    print("=" * 80)

if __name__ == '__main__':
    main()
