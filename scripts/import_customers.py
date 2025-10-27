#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar clientes desde Excel a Odoo 18
Importa clientes/contactos al modelo res.partner
"""

import pandas as pd
import xmlrpc.client
from datetime import datetime
import sys

# Configuración de conexión a Odoo
ODOO_URL = 'http://localhost:10018'
ODOO_DB = 'cutai'
ODOO_USERNAME = 'admin@gmail.com'
ODOO_PASSWORD = 'Admin123'

# Archivo Excel
EXCEL_FILE = '/root/clientes_28107_1760455365.xlsx'

def connect_odoo():
    """Conecta con Odoo y retorna el UID y modelos"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("Error: No se pudo autenticar con Odoo")
            sys.exit(1)
            
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return uid, models
    except Exception as e:
        print(f"Error conectando a Odoo: {e}")
        sys.exit(1)

def parse_date(day, month, year):
    """Convierte día, mes, año a formato fecha YYYY-MM-DD"""
    try:
        if pd.notna(day) and pd.notna(month) and pd.notna(year):
            day = int(day)
            month = int(month)
            year = int(year)
            
            # Validar valores
            if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2025:
                return f"{year:04d}-{month:02d}-{day:02d}"
    except:
        pass
    return False

def clean_phone(phone):
    """Limpia y formatea número de teléfono"""
    if pd.isna(phone):
        return False
    
    phone_str = str(phone).strip()
    # Remover caracteres especiales pero mantener el +
    phone_str = ''.join(c for c in phone_str if c.isdigit() or c == '+')
    
    if not phone_str or phone_str == '+':
        return False
    
    return phone_str

def import_customers(uid, models):
    """Importa clientes desde Excel a Odoo"""
    
    # Leer archivo Excel
    print(f"\nLeyendo archivo: {EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE)
    print(f"Total de registros en el archivo: {len(df)}")
    print(f"Columnas: {list(df.columns)}\n")
    
    created_count = 0
    updated_count = 0
    error_count = 0
    skip_count = 0
    
    print("Iniciando importación de clientes...\n")
    print("=" * 80)
    
    for index, row in df.iterrows():
        # Mostrar progreso cada 100 registros
        if (index + 1) % 100 == 0:
            print(f"\n[PROGRESO] {index + 1}/{len(df)} - Creados: {created_count}, Actualizados: {updated_count}, Errores: {error_count}, Omitidos: {skip_count}\n")
        try:
            # Extraer datos del cliente
            email = str(row.get('Email', '')).strip() if pd.notna(row.get('Email')) else ''
            first_name = str(row.get('Nombres', '')).strip() if pd.notna(row.get('Nombres')) else ''
            last_name = str(row.get('Apellidos', '')).strip() if pd.notna(row.get('Apellidos')) else ''
            
            # Nombre completo
            name_parts = []
            if first_name:
                name_parts.append(first_name)
            if last_name:
                name_parts.append(last_name)
            
            full_name = ' '.join(name_parts) if name_parts else f'Cliente {index + 1}'
            
            # Cédula/Identificación
            cedula = str(row.get('cédula', '')).strip() if pd.notna(row.get('cédula')) else ''
            
            # Número de cliente
            customer_number = ''
            if pd.notna(row.get('Número de cliente')):
                customer_number = str(int(row.get('Número de cliente')))
            
            # Teléfonos
            phone = clean_phone(row.get('Teléfono'))
            mobile = clean_phone(row.get('Teléfono secundario del cliente'))
            
            # Dirección
            street = str(row.get('Dirección', '')).strip() if pd.notna(row.get('Dirección')) else ''
            
            # Ciudad (guardamos como string en campo city)
            city = ''
            if pd.notna(row.get('Ciudad')):
                city = str(row.get('Ciudad')).strip()
            
            # Género
            gender = ''
            if pd.notna(row.get('Género. 1 = Femenino, 2 = Masculino')):
                gender_val = int(row.get('Género. 1 = Femenino, 2 = Masculino'))
                if gender_val == 1:
                    gender = 'female'
                elif gender_val == 2:
                    gender = 'male'
            
            # Fecha de nacimiento
            birthdate = parse_date(
                row.get('Día del nacimiento'),
                row.get('Mes del nacimiento'),
                row.get('Año de nacimiento.')
            )
            
            # Buscar si el cliente ya existe (solo si tenemos criterios de búsqueda únicos)
            existing_ids = []
            if email and '@' in email:
                # Buscar por email
                existing_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner', 'search',
                    [[['email', '=', email]]]
                )
            elif cedula:
                # Buscar por cédula
                existing_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner', 'search',
                    [[['vat', '=', cedula]]]
                )
            elif customer_number:
                # Buscar por número de cliente
                existing_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner', 'search',
                    [[['ref', '=', customer_number]]]
                )
            # Si no hay criterios únicos, no buscar, solo crear
            
            # Preparar valores del contacto
            partner_vals = {
                'name': full_name,
                'customer_rank': 1,  # Marcar como cliente
                'is_company': False,  # Es una persona
                'active': True,
            }
            
            # Email
            if email and '@' in email:
                partner_vals['email'] = email.lower()
            
            # Teléfonos
            if phone:
                partner_vals['phone'] = phone
            if mobile:
                partner_vals['mobile'] = mobile
            
            # Dirección
            if street:
                partner_vals['street'] = street
            if city:
                partner_vals['city'] = city
            
            # Cédula como VAT (Tax ID)
            if cedula:
                partner_vals['vat'] = cedula
            
            # Número de cliente como referencia
            if customer_number:
                partner_vals['ref'] = customer_number
            
            # Género (usar campo comment para guardar esta info)
            comments = []
            if gender:
                gender_text = 'Femenino' if gender == 'female' else 'Masculino'
                comments.append(f"Género: {gender_text}")
            
            # Fecha de nacimiento (guardar en comment si no hay campo directo)
            if birthdate:
                comments.append(f"Fecha de nacimiento: {birthdate}")
            
            if comments:
                partner_vals['comment'] = '\n'.join(comments)
            
            if existing_ids:
                # Actualizar cliente existente
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner', 'write',
                    [existing_ids, partner_vals]
                )
                updated_count += 1
            else:
                # Crear nuevo cliente
                partner_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'res.partner', 'create',
                    [partner_vals]
                )
                created_count += 1
                
        except Exception as e:
            error_count += 1
            if error_count <= 5:  # Solo mostrar los primeros 5 errores
                print(f"  ERROR [{full_name}]: {str(e)[:100]}")
            continue
    
    print("\n" + "=" * 80)
    print("RESUMEN DE IMPORTACIÓN:")
    print(f"  Clientes creados: {created_count}")
    print(f"  Clientes actualizados: {updated_count}")
    print(f"  Errores: {error_count}")
    print(f"  Omitidos: {skip_count}")
    print(f"  Total procesado: {created_count + updated_count}")
    print("=" * 80)
    print("\n¡Importación completada!")

def main():
    print("=" * 80)
    print("IMPORTACIÓN DE CLIENTES A ODOO")
    print("=" * 80)
    
    # Conectar a Odoo
    print("\nConectando a Odoo...")
    uid, models = connect_odoo()
    print(f"Conectado exitosamente. UID: {uid}")
    
    # Importar clientes
    import_customers(uid, models)

if __name__ == '__main__':
    main()
