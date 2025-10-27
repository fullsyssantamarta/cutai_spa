#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar productos desde Excel a Odoo
Los productos quedarán disponibles en:
- Punto de Venta (POS)
- Compras
- Ventas
"""

import xmlrpc.client
import pandas as pd
import sys
import os

# Configuración de conexión a Odoo
ODOO_URL = 'http://localhost:10018'
ODOO_DB = 'cutai'
ODOO_USERNAME = 'admin@gmail.com'
ODOO_PASSWORD = 'Admin123'

# Archivo Excel
EXCEL_FILE = '/root/Productos 2025.xlsx'

def connect_odoo():
    """Conectar a Odoo usando XML-RPC"""
    print("Conectando a Odoo...")
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    
    if not uid:
        print("Error: No se pudo autenticar en Odoo")
        sys.exit(1)
    
    print(f"Conectado exitosamente. UID: {uid}")
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    return uid, models

def get_or_create_category(models, uid, category_name):
    """Obtener o crear categoría de producto"""
    if not category_name or pd.isna(category_name):
        return False
    
    # Buscar categoría existente
    category_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'product.category', 'search',
        [[('name', '=', category_name)]]
    )
    
    if category_ids:
        print(f"  Categoría encontrada: {category_name}")
        return category_ids[0]
    
    # Crear nueva categoría
    category_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'product.category', 'create',
        [{
            'name': category_name,
        }]
    )
    print(f"  Categoría creada: {category_name}")
    return category_id

def get_or_create_brand(models, uid, brand_name):
    """Obtener o crear marca de producto (usando cutai_product_brand)"""
    if not brand_name or pd.isna(brand_name):
        return False
    
    # Buscar marca existente en cutai_product_brand
    brand_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'cutai.product.brand', 'search',
        [[('name', '=', brand_name)]]
    )
    
    if brand_ids:
        print(f"  Marca encontrada: {brand_name}")
        return brand_ids[0]
    
    # Crear nueva marca
    brand_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'cutai.product.brand', 'create',
        [{
            'name': brand_name,
        }]
    )
    print(f"  Marca creada: {brand_name}")
    return brand_id

def import_products(models, uid, df):
    """Importar productos desde DataFrame"""
    print(f"\nIniciando importación de {len(df)} productos...")
    
    created = 0
    updated = 0
    errors = 0
    
    for index, row in df.iterrows():
        try:
            # Obtener datos del producto (usando columnas del Excel real)
            default_code = str(row.get('SKU', '')).strip() if pd.notna(row.get('SKU')) else f"PROD-{index+1}"
            name = str(row.get('Nombre', '')).strip() if pd.notna(row.get('Nombre')) else f"Producto {index+1}"
            formato = str(row.get('Formato', '')).strip() if pd.notna(row.get('Formato')) else ''
            
            # Agregar formato al nombre si existe
            if formato:
                name = f"{name} - {formato}"
            
            # Precios y costos
            list_price = float(row.get('Precio venta externa', 0)) if pd.notna(row.get('Precio venta externa')) else 0.0
            standard_price = float(row.get('Costo', 0)) if pd.notna(row.get('Costo')) else 0.0
            
            # Categoría y marca
            category_name = str(row.get('Categoría', '')).strip() if pd.notna(row.get('Categoría')) else None
            brand_name = str(row.get('Marca', '')).strip() if pd.notna(row.get('Marca')) else None
            
            # Stock inicial
            qty_available = float(row.get('Stock Cutai', 0)) if pd.notna(row.get('Stock Cutai')) else 0.0
            
            # Descripción
            description = str(row.get('Descripción', '')).strip() if pd.notna(row.get('Descripción')) else ''
            
            # Estado (activo/inactivo)
            estado = str(row.get('Estado', 'Activo')).strip() if pd.notna(row.get('Estado')) else 'Activo'
            active = estado.lower() == 'activo'
            
            print(f"\n[{index+1}/{len(df)}] Procesando: {name} ({default_code})")
            
            # Obtener o crear categoría y marca
            category_id = get_or_create_category(models, uid, category_name) if category_name else False
            brand_id = get_or_create_brand(models, uid, brand_name) if brand_name else False
            
            # Verificar si el producto ya existe (por código)
            product_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'product.product', 'search',
                [[('default_code', '=', default_code)]]
            )
            
            # Preparar valores del producto
            product_vals = {
                'name': name,
                'default_code': default_code,
                'type': 'consu',  # Producto consumible (en Odoo 18: 'consu' para consumible, 'service' para servicio)
                'list_price': list_price,
                'standard_price': standard_price,
                'categ_id': category_id if category_id else False,
                'sale_ok': True,  # Disponible en Ventas
                'purchase_ok': True,  # Disponible en Compras
                'available_in_pos': True,  # Disponible en Punto de Venta
                'active': active,
            }
            
            # Agregar descripción con marca si existe
            desc_parts = []
            if brand_name:
                desc_parts.append(f"Marca: {brand_name}")
            if description:
                desc_parts.append(description)
            
            if desc_parts:
                full_description = '\n'.join(desc_parts)
                product_vals['description'] = full_description
                product_vals['description_sale'] = full_description
            
            if product_ids:
                # Actualizar producto existente
                models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'product.product', 'write',
                    [product_ids, product_vals]
                )
                product_id = product_ids[0]
                print(f"  Producto actualizado: {name}")
                updated += 1
            else:
                # Crear nuevo producto
                product_id = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'product.product', 'create',
                    [product_vals]
                )
                print(f"  Producto creado: {name}")
                created += 1
            
            # Actualizar stock si es necesario (mediante ajuste de inventario)
            if qty_available > 0:
                try:
                    # Buscar ubicación de stock
                    location_ids = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'stock.location', 'search',
                        [[('usage', '=', 'internal')], ('name', '=', 'Stock')],
                        {'limit': 1}
                    )
                    
                    if location_ids:
                        # Actualizar cantidad en stock
                        models.execute_kw(
                            ODOO_DB, uid, ODOO_PASSWORD,
                            'stock.quant', 'create',
                            [{
                                'product_id': product_id,
                                'location_id': location_ids[0],
                                'inventory_quantity': qty_available,
                            }]
                        )
                        print(f"  Stock actualizado: {qty_available} unidades")
                except Exception as e:
                    print(f"  Advertencia: No se pudo actualizar stock: {e}")
            
        except Exception as e:
            print(f"  ERROR procesando producto: {e}")
            errors += 1
    
    print("\n" + "="*80)
    print(f"RESUMEN DE IMPORTACIÓN:")
    print(f"  Productos creados: {created}")
    print(f"  Productos actualizados: {updated}")
    print(f"  Errores: {errors}")
    print(f"  Total procesado: {created + updated}")
    print("="*80)

def main():
    """Función principal"""
    print("="*80)
    print("IMPORTACIÓN DE PRODUCTOS A ODOO")
    print("="*80)
    
    # Verificar que existe el archivo
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: No se encuentra el archivo {EXCEL_FILE}")
        sys.exit(1)
    
    # Leer archivo Excel
    print(f"\nLeyendo archivo: {EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE, sheet_name=0)
    print(f"Total de productos en el archivo: {len(df)}")
    print(f"Columnas: {df.columns.tolist()}")
    
    # Conectar a Odoo
    uid, models = connect_odoo()
    
    # Importar productos
    import_products(models, uid, df)
    
    print("\n¡Importación completada!")

if __name__ == "__main__":
    main()
