#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script SIMPLE para corregir solo partner_id de las citas
"""

import xmlrpc.client

ODOO_URL = 'http://localhost:10018'
ODOO_DB = 'cutai'
ODOO_USERNAME = 'admin@gmail.com'
ODOO_PASSWORD = 'Admin123'

def main():
    print("=" * 80)
    print("CORRECCIÓN DE PARTNER_ID EN CITAS")
    print("=" * 80)
    
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    print(f"\nConectado. UID: {uid}\n")
    
    # Obtener todas las citas donde partner_id = Administrator (3)
    event_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'calendar.event', 'search',
        [[['partner_id', '=', 3]]]
    )
    
    print(f"Citas con partner_id = Administrator: {len(event_ids)}\n")
    
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
                {'fields': ['partner_ids']}
            )[0]
            
            if event['partner_ids']:
                # Actualizar partner_id con el primero de partner_ids
                correct_partner_id = event['partner_ids'][0]
                
                models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                    'calendar.event', 'write',
                    [[event_id], {'partner_id': correct_partner_id}]
                )
                updated += 1
            else:
                errors += 1
                
        except Exception as e:
            errors += 1
            if errors <= 10:
                print(f"  Error en cita {event_id}: {str(e)[:150]}")
    
    print("\n" + "=" * 80)
    print(f"RESUMEN:")
    print(f"  Citas actualizadas: {updated}")
    print(f"  Errores: {errors}")
    print("=" * 80)

if __name__ == '__main__':
    main()
