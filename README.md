# CUTAI Laser Clinic Management System

Sistema integral de gestión para clínicas de depilación láser CUTAI.

## Características Principales

### 1. Gestión de Clientes
- Campos personalizados para clientes de depilación láser
- Fototipo de piel (clasificación Fitzpatrick I-VI)
- Zonas activas de tratamiento
- Información hormonal (anticonceptivos, SOP)
- Gestión de consentimientos informados
- Registro de alergias y contraindicaciones
- Historial completo de tratamientos y sesiones

### 2. Sistema de Membresías
- Membresías con ciclos de 1-9 pagos mensuales
- Control automático de pagos y vencimientos
- Aplicación automática de moras por pagos atrasados
- Congelamiento de membresías con motivo
- Política de cancelación con aviso de 30 días
- Promociones asociadas a membresías
- Recordatorios automáticos de pago

### 3. Tratamientos y Sesiones
- Registro detallado de tratamientos por zona
- Parámetros técnicos: fluencia, spot size, duración de pulso
- Seguimiento de progreso por número de sesiones
- Observaciones pre y post-tratamiento
- Nivel de dolor y reacción de la piel
- Fotografías antes y después
- Asignación de máquina, cabina y operador

### 4. Inventario Backbar
- Consumo automático de productos por sesión
- Productos backbar: hojas, gel, toallas, criógeno
- Configuración de consumo por zona de tratamiento
- Registro en inventario de Odoo
- Control de stock por sucursal

### 5. Sistema de Citas
- Integración con calendario de Odoo
- Asignación de sucursal, cabina y máquina
- Control de operadores asignados
- Recordatorios automáticos:
  - T-48h: Email con recomendaciones
  - T-24h: Email de confirmación
  - T-3h: SMS de recordatorio
- Política de no-show

### 6. Documentos y Plantillas
- Consentimiento informado para láser
- Política de no-show
- Cláusulas de membresía
- Encuestas de satisfacción post-tratamiento
- Felicitaciones de cumpleaños
- Notificaciones de renovación de membresía

### 7. Configuración Multi-Sucursal
- Gestión de múltiples sucursales
- Cabinas por sucursal
- Máquinas láser con control de mantenimiento
- Ubicaciones de inventario por sucursal

### 8. Reportes y KPIs
- Dashboard diario por sucursal
- Reportes semanales de conversión
- Análisis mensual de consumo y ROI
- Reportes financieros por sucursal

## Instalación

1. Copiar el módulo a la carpeta de addons de Odoo
2. Actualizar la lista de aplicaciones
3. Instalar "CUTAI Laser Clinic Management"

## Dependencias

- base
- sale
- sale_management
- crm
- calendar
- stock
- account
- contacts
- hr
- documents
- sign
- sms
- whatsapp_fullsys

## Configuración Inicial

### 1. Crear Sucursales
Ir a CUTAI > Configuración > Sucursales y crear las sucursales

### 2. Configurar Cabinas
Crear las cabinas de tratamiento por sucursal

### 3. Registrar Máquinas
Registrar las máquinas láser con sus especificaciones técnicas

### 4. Configurar Zonas
Las zonas de tratamiento vienen precargadas, pero pueden personalizarse

### 5. Configurar Productos Backbar
Verificar los productos de consumo backbar y ajustar cantidades según necesidad

## Flujo de Trabajo

### Registro de Nuevo Cliente
1. Crear contacto marcando "Cliente CUTAI"
2. Registrar fototipo y zonas de interés
3. Cargar consentimiento informado
4. Registrar alergias y contraindicaciones

### Creación de Membresía
1. Desde el cliente, crear nueva membresía
2. Seleccionar tipo (9 pagos, prepago, por sesión)
3. Definir monto de pago
4. Aplicar promoción si corresponde
5. Activar membresía (genera calendario de 9 pagos automáticamente)

### Inicio de Tratamiento
1. Crear nuevo tratamiento para el cliente
2. Seleccionar zona a tratar
3. Definir parámetros técnicos predeterminados
4. Indicar número de sesiones planificadas
5. Asociar a membresía si corresponde

### Programación de Sesión
1. Crear cita en calendario
2. Asignar sucursal, cabina y máquina
3. Asignar operador
4. El sistema envía recordatorios automáticos

### Ejecución de Sesión
1. Al inicio: marcar sesión como "En Progreso"
2. Registrar parámetros utilizados (fluencia, spot, pulsos)
3. Ingresar observaciones pre-tratamiento
4. Al finalizar: completar sesión
5. Ingresar observaciones post-tratamiento
6. Sistema registra consumo backbar automáticamente
7. Cliente recibe encuesta de satisfacción

### Gestión de Pagos
1. Sistema envía recordatorio 3 días antes del vencimiento
2. Registrar pago cuando se recibe
3. Si pasa el período de gracia, se aplica mora automáticamente
4. Cron diario revisa pagos atrasados

## Tareas Automáticas (Crons)

- **Revisión de Pagos Atrasados**: Diaria, aplica moras según configuración
- **Recordatorios de Pago**: Diaria, envía emails 3 días antes del vencimiento

## Seguridad

El módulo incluye 4 niveles de acceso:

1. **Usuario**: Solo lectura
2. **Operador/Técnico**: Puede crear y editar sesiones, registrar tratamientos
3. **Manager**: Control total excepto configuración del sistema
4. **Administrador**: Acceso completo

## Soporte

Para soporte técnico, contactar a FullSys Tecnología Santa Marta
- Web: https://www.fullsys.com.co
- Email: soporte@fullsys.com.co

## Licencia

LGPL-3

## Versión

18.0.1.0.0

## Autor

FullSys Tecnología Santa Marta
