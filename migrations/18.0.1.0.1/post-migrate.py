# -*- coding: utf-8 -*-
"""
Post-migration script para actualizar estados de citas a Requerimientos V2
"""

def migrate(cr, version):
    """Migrar estados antiguos a nuevos estados"""
    
    # Mapeo de estados antiguos a nuevos
    state_mapping = {
        'scheduled': 'reserved',
        'done': 'attended',
        'in_progress': 'confirmed',
    }
    
    for old_state, new_state in state_mapping.items():
        cr.execute("""
            UPDATE calendar_event
            SET appointment_state = %s
            WHERE appointment_state = %s
        """, (new_state, old_state))
        
        affected_rows = cr.rowcount
        if affected_rows > 0:
            print(f"Migrated {affected_rows} appointments from '{old_state}' to '{new_state}'")
    
    # Invalidar caché
    cr.execute("SELECT id FROM calendar_event LIMIT 1")
    if cr.fetchone():
        cr.execute("DELETE FROM ir_model_data WHERE model = 'ir.ui.view' AND module = 'cutai_laser_clinic'")
        print("Cache invalidated successfully")
