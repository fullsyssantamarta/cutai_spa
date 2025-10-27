#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script RÁPIDO para importar SOLO clientes nuevos (sin buscar duplicados)
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
EXCEL_FILE = '/root/clientes_28107_1760455365.xlsx'

def connect_odoo():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        print("Error: No se pudo autenticar")
        sys.exit(1)
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    return uid, models

def clean_phone(phone):
    if pd.isna(phone):
        return False
    phone_str = str(phone).strip()
    phone_str = ''.join(c for c in phone_str if c.isdigit() or c == '+')
    return phone_str if phone_str and phone_str != '+' else False

def parse_date(day, month, year):
    try:
        if pd.notna(day) and pd.notna(month) and pd.notna(year):
            day, month, year = int(day), int(month), int(year)
            if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2025:
                return f"{year:04d}-{month:02d}-{day:02d}"
    except:
        pass
    return False

def import_fast():
    print("=" * 80)
    print("IMPORTACIÓN RÁPIDA DE CLIENTES")
    print("=" * 80)
    
    uid, models = connect_odoo()
    print(f"\nConectado a Odoo. UID: {uid}")
    
    # Leer Excel
    print(f"\nLeyendo: {EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE)
    print(f"Total registros: {len(df)}\n")
    
    # Obtener todos los emails existentes de una vez
    print("Obteniendo clientes existentes...")
    existing_partners = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search_read',
        [[['customer_rank', '>', 0]]],
        {'fields': ['email', 'vat', 'ref']}
    )
    
    existing_emails = {p['email'].lower() for p in existing_partners if p.get('email')}
    existing_vats = {p['vat'] for p in existing_partners if p.get('vat')}
    existing_refs = {p['ref'] for p in existing_partners if p.get('ref')}
    
    print(f"Clientes existentes: {len(existing_partners)}")
    print(f"  - Con email: {len(existing_emails)}")
    print(f"  - Con cédula: {len(existing_vats)}")
    print(f"  - Con ref: {len(existing_refs)}\n")
    
    created = 0
    skipped = 0
    errors = 0
    
    print("Procesando clientes...")
    print("=" * 80)
    
    for index, row in df.iterrows():
        if (index + 1) % 200 == 0:
            print(f"[{index+1}/{len(df)}] Creados: {created}, Omitidos: {skipped}, Errores: {errors}")
        
        try:
            # Extraer datos
            email = str(row.get('Email', '')).strip() if pd.notna(row.get('Email')) else ''
            first_name = str(row.get('Nombres', '')).strip() if pd.notna(row.get('Nombres')) else ''
            last_name = str(row.get('Apellidos', '')).strip() if pd.notna(row.get('Apellidos')) else ''
            cedula = str(row.get('cédula', '')).strip() if pd.notna(row.get('cédula')) else ''
            customer_number = str(int(row.get('Número de cliente'))) if pd.notna(row.get('Número de cliente')) else ''
            
            # Nombre completo
            name_parts = [p for p in [first_name, last_name] if p]
            full_name = ' '.join(name_parts) if name_parts else f'Cliente {index + 1}'
            
            # Verificar si ya existe (rápido, en memoria)
            skip = False
            if email and '@' in email and email.lower() in existing_emails:
                skip = True
            elif cedula and cedula in existing_vats:
                skip = True
            elif customer_number and customer_number in existing_refs:
                skip = True
            
            if skip:
                skipped += 1
                continue
            
            # Preparar datos
            partner_vals = {
                'name': full_name,
                'customer_rank': 1,
                'is_company': False,
                'active': True,
            }
            
            if email and '@' in email:
                partner_vals['email'] = email.lower()
            
            phone = clean_phone(row.get('Teléfono'))
            mobile = clean_phone(row.get('Teléfono secundario del cliente'))
            if phone:
                partner_vals['phone'] = phone
            if mobile:
                partner_vals['mobile'] = mobile
            
            street = str(row.get('Dirección', '')).strip() if pd.notna(row.get('Dirección')) else ''
            if street:
                partner_vals['street'] = street
            
            city = str(row.get('Ciudad', '')).strip() if pd.notna(row.get('Ciudad')) else ''
            if city:
                partner_vals['city'] = city
            
            if cedula:
                partner_vals['vat'] = cedula
            if customer_number:
                partner_vals['ref'] = customer_number
            
            # Género y fecha de nacimiento en comentarios
            comments = []
            gender_val = row.get('Género. 1 = Femenino, 2 = Masculino')
            if pd.notna(gender_val):
                gender_text = 'Femenino' if int(gender_val) == 1 else 'Masculino'
                comments.append(f"Género: {gender_text}")
            
            birthdate = parse_date(
                row.get('Día del nacimiento'),
                row.get('Mes del nacimiento'),
                row.get('Año de nacimiento.')
            )
            if birthdate:
                comments.append(f"Fecha de nacimiento: {birthdate}")
            
            if comments:
                partner_vals['comment'] = '\n'.join(comments)
            
            # Crear cliente
            partner_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'create',
                [partner_vals]
            )
            created += 1
            
        except Exception as e:
            errors += 1
            if errors <= 10:
                print(f"  ERROR: {str(e)[:100]}")
    
    print("\n" + "=" * 80)
    print("RESUMEN:")
    print(f"  Clientes creados: {created}")
    print(f"  Omitidos (ya existen): {skipped}")
    print(f"  Errores: {errors}")
    print("=" * 80)

if __name__ == '__main__':
    import_fast()
