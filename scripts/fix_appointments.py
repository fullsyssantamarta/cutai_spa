#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir partner_id en las citas importadas
"""

import xmlrpc.client
import pandas as pd

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

def main():
    print("=" * 80)
    print("CORRECCIÓN Y ACTUALIZACIÓN DE CITAS")
    print("=" * 80)
    
    uid, models = connect_odoo()
    print(f"\nConectado. UID: {uid}")
    
    # Leer Excel
    df = pd.read_excel(EXCEL_FILE)
    print(f"Excel: {len(df)} registros\n")
    
    # Obtener todas las citas (excepto la de prueba ID 1)
    event_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'calendar.event', 'search',
        [[['id', '>', 1]]],
        {'order': 'id asc'}
    )
    
    print(f"Citas a actualizar: {len(event_ids)}\n")
    
    updated = 0
    errors = 0
    
    for idx, event_id in enumerate(event_ids):
        if (idx + 1) % 100 == 0:
            print(f"[{idx+1}/{len(event_ids)}] Actualizadas: {updated}, Errores: {errors}")
        
        try:
            # Leer la cita
            event = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                'calendar.event', 'read',
                [[event_id]],
                {'fields': ['partner_ids', 'start', 'name']}
            )[0]
            
            if not event['partner_ids']:
                errors += 1
                continue
            
            partner_id = event['partner_ids'][0]
            
            # Buscar el registro en Excel por fecha y nombre
            event_start = event['start'][:16]  # YYYY-MM-DD HH:MM
            
            # Buscar en Excel la fila correspondiente
            matching_row = None
            for _, row in df.iterrows():
                fecha_str = str(row.get('Fecha de realización', '')).strip()
                if fecha_str:
                    try:
                        from datetime import datetime
                        fecha_dt = datetime.strptime(fecha_str, '%d/%m/%Y %H:%M')
                        fecha_formatted = fecha_dt.strftime('%Y-%m-%d %H:%M')
                        
                        if fecha_formatted == event_start:
                            matching_row = row
                            break
                    except:
                        continue
            
            if matching_row is None:
                errors += 1
                continue
            
            # Preparar datos para actualizar
            update_vals = {
                'partner_id': partner_id  # Corregir partner_id
            }
            
            # Agregar precios si existen
            precio_lista = matching_row.get('Precio lista')
            if pd.notna(precio_lista) and float(precio_lista) > 0:
                update_vals['list_price'] = float(precio_lista)
            
            precio_real = matching_row.get('Precio real')
            if pd.notna(precio_real) and float(precio_real) > 0:
                update_vals['real_price'] = float(precio_real)
            
            # Sesiones
            num_sesion = matching_row.get('Nº de sesión')
            if pd.notna(num_sesion) and int(num_sesion) > 0:
                update_vals['session_number'] = int(num_sesion)
            
            sesiones_totales = matching_row.get('Sesiones Totales')
            if pd.notna(sesiones_totales) and int(sesiones_totales) > 0:
                update_vals['total_sessions'] = int(sesiones_totales)
            
            # Estado
            estado = str(matching_row.get('Estado', '')).strip()
            if estado:
                estado_lower = estado.lower()
                if 'asiste' in estado_lower and 'no' not in estado_lower:
                    update_vals['appointment_state'] = 'completed'
                elif 'no asiste' in estado_lower:
                    update_vals['appointment_state'] = 'no_show'
                elif 'confirmado' in estado_lower:
                    update_vals['appointment_state'] = 'confirmed'
                else:
                    update_vals['appointment_state'] = 'pending'
            
            # Comentario interno
            comentario = str(matching_row.get('Comentario interno', '')).strip()
            if comentario and comentario not in ['Sin Preferencia', 'Manual']:
                update_vals['description'] = comentario[:2000]
            
            # Actualizar la cita
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                'calendar.event', 'write',
                [[event_id], update_vals]
            )
            updated += 1
            
        except Exception as e:
            errors += 1
            if errors <= 10:
                print(f"  Error en cita {event_id}: {str(e)[:100]}")
    
    print("\n" + "=" * 80)
    print(f"RESUMEN:")
    print(f"  Citas actualizadas: {updated}")
    print(f"  Errores: {errors}")
    print("=" * 80)

if __name__ == '__main__':
    main()
