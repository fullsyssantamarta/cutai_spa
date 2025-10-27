#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script MÍNIMO para importar reservas - solo campos básicos
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
    if pd.isna(date_str):
        return False
    try:
        date_str = str(date_str).strip()
        dt = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return False

def main():
    print("=" * 80)
    print("IMPORTACIÓN MÍNIMA DE CITAS")
    print("=" * 80)
    
    uid, models = connect_odoo()
    print(f"\nConectado. UID: {uid}")
    
    df = pd.read_excel(EXCEL_FILE)
    print(f"Total: {len(df)} reservas\n")
    
    created = 0
    errors = 0
    
    for index, row in df.iterrows():
        if (index + 1) % 100 == 0:
            print(f"[{index+1}/{len(df)}] Creadas: {created}, Errores: {errors}")
        
        try:
            start_dt = parse_datetime(row.get('Fecha de realización'))
            if not start_dt:
                errors += 1
                continue
            
            email = str(row.get('E-mail', '')).strip().lower() if pd.notna(row.get('E-mail')) else ''
            
            if not email or '@' not in email:
                errors += 1
                continue
            
            # Buscar partner
            partner_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'search',
                [[['email', '=', email]]], {'limit': 1}
            )
            
            if not partner_ids:
                errors += 1
                continue
            
            servicio = str(row.get('Servicio', 'Cita')).strip() if pd.notna(row.get('Servicio')) else 'Cita'
            nombre = str(row.get('Nombre', '')).strip() if pd.notna(row.get('Nombre')) else ''
            apellido = str(row.get('Apellido', '')).strip() if pd.notna(row.get('Apellido')) else ''
            
            # Crear cita MÍN IMA
            event_vals = {
                'name': f"{servicio} - {nombre} {apellido}",
                'start': start_dt,
                'stop': start_dt,
                'partner_ids': [(6, 0, partner_ids)],
            }
            
            event_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'calendar.event', 'create',
                [event_vals]
            )
            created += 1
            
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error fila {index+1}: {str(e)[:100]}")
    
    print("\n" + "=" * 80)
    print(f"  Citas creadas: {created}")
    print(f"  Errores: {errors}")
    print("=" * 80)

if __name__ == '__main__':
    main()
