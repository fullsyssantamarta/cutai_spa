# CUTAI LASER SPA - Sistema Completo de Gestión

## Resumen Ejecutivo

Se ha desarrollado un **sistema integral de gestión para SPA láser y clínica estética** que cubre todas las operaciones del negocio, desde la atención al cliente hasta la facturación, inventario, comisiones y reportes.

---

## FUNCIONALIDADES PRINCIPALES

### 1. GESTIÓN DE CLIENTES (res.partner extendido)
**Información Médica y Estética:**
- Fototipo de piel (I-VI según Fitzpatrick)
- Zonas activas de tratamiento
- Uso de anticonceptivos/hormonas
- Diagnóstico SOP (Síndrome de Ovario Poliquístico)
- Alergias y contraindicaciones
- Consentimientos informados con vigencia automática

**Historial y Seguimiento:**
- Total de sesiones realizadas
- Última cita
- Próxima cita programada
- Membresía activa
- Tratamientos en curso

---

### 2. SERVICIOS SPA Y LÁSER

**Catálogo de Servicios (cutai.service):**
- Tratamientos láser (depilación por zonas)
- Faciales (limpieza, hidratación, anti-edad)
- Tratamientos corporales (reductores, reafirmantes)
- Masajes (relajantes, terapéuticos, deportivos)
- Depilación con cera
- Tratamientos estéticos (peeling, microdermoabrasión)
- Servicios SPA (circuitos, hidroterapia)

**Características por Servicio:**
- Duración estándar (minutos)
- Precio
- Tipo de comisión (porcentaje o monto fijo)
- Recursos necesarios (máquina, tipo de cabina)
- Productos backbar que consume
- Instrucciones para el terapeuta
- Imágenes promocionales

**Categorías Pre-configuradas:**
1. Tratamientos Láser
2. Faciales
3. Tratamientos Corporales
4. Masajes
5. Depilación con Cera
6. Tratamientos Estéticos
7. Paquetes y Combos

---

### 3. PAQUETES Y COMBOS (cutai.package)

**Tipos de Paquetes:**
- Paquete de sesiones (ej: 10 sesiones de láser)
- Combo de servicios (ej: facial + masaje)
- Membresías especiales

**Gestión de Paquetes:**
- Múltiples servicios incluidos con cantidades
- Cálculo automático de valor total
- Porcentaje de descuento calculado
- Vigencia configurable (días desde la compra)
- Producto asociado para facturación

---

### 4. SISTEMA DE CITAS MEJORADO

**Agenda Inteligente (calendar.event extendido):**
- Múltiples servicios por cita
- Asignación de terapeuta por servicio
- Control de ocupación de cabinas
- Reserva de máquinas láser
- Tipo de cita: consulta, láser, spa, facial, masaje, estético, combo
- Cálculo automático de duración total
- Monto total de la cita
- Estado de pago (pendiente, parcial, pagado)

**Servicios en Cita (cutai.appointment.service):**
- Servicio específico
- Terapeuta asignado
- Duración
- Precio
- Comisión calculada automáticamente
- Propina del cliente
- Calificación (1-5 estrellas)
- Comentarios del cliente
- Estado: programado, en proceso, completado, cancelado

**Recordatorios Automáticos:**
- T-48h: Email con recomendaciones
- T-24h: Email de confirmación
- T-3h: SMS recordatorio

---

### 5. TRATAMIENTOS LÁSER (cutai.treatment y cutai.session)

**Control de Tratamientos:**
- Zona específica
- Sesiones planificadas vs completadas
- Progreso en porcentaje
- Parámetros técnicos: fluencia, spot size, duración de pulso
- Frecuencia de sesiones (4/6/8 semanas)
- Membresía asociada

**Sesiones Detalladas:**
- Parámetros técnicos reales
- Número de pulsos
- Máquina utilizada
- Cabina y operador
- Observaciones pre y post-tratamiento
- Nivel de dolor (0-5)
- Reacción de piel
- Porcentaje de reducción de vello
- Fotos antes/después
- Consumo backbar automático

---

### 6. MEMBRESÍAS (cutai.membership)

**Sistema de Membresías:**
- Tipos: 9 pagos mensuales, prepago, por sesión
- Ciclos 1-9 con seguimiento
- Calendario de pagos automático
- Moras: $20 después de 5 días (configurable)
- Promociones aplicables

**Gestión de Pagos:**
- Estado por pago (pendiente, pagado, parcial)
- Días de atraso calculados
- Moras acumuladas
- Recordatorios automáticos (T-3 días)

**Congelamiento:**
- Motivo de congelamiento
- Fecha de descongelamiento
- Recálculo automático de fechas de pago

**Cancelación:**
- Política de aviso 30 días (configurable)
- Validación de tiempo mínimo
- Registro de motivo

---

### 7. RETAIL (Venta de Productos)

**Venta en Mostrador (cutai.retail.sale):**
- Cliente
- Sucursal
- Vendedor
- Múltiples productos
- Descuentos
- Métodos de pago (efectivo, tarjeta, transferencia, mixto)
- Comisiones automáticas al vendedor
- Integración con facturación

**Productos Retail (product.product extendido):**
- Categorías: skincare, haircare, cosmetics, supplements, tools
- Marca del producto
- Porcentaje de comisión
- Control de inventario

**Marcas (cutai.product.brand):**
- Gestión de marcas
- Productos por marca
- Análisis de margen por marca

---

### 8. INVENTARIO

**Productos Backbar (consumo interno):**
- Hojas de camilla
- Gel conductor
- Toallas
- Criógeno
- Otros consumibles

**Consumo Automático:**
- Al completar sesión se registra consumo
- Configuración por servicio/zona
- Movimientos de inventario automáticos
- Control por sucursal

**Productos Retail (venta):**
- Stock por sucursal
- Alertas de stock mínimo
- Control de lotes y caducidad
- Ciclos de conteo

---

### 9. COMISIONES

**Sistema de Comisiones:**
- Por servicio (porcentaje o monto fijo)
- Por venta retail (porcentaje)
- Cálculo automático por terapeuta
- Cálculo automático por vendedor
- Registro de propinas

**Reportes de Comisiones:**
- Por terapeuta/operador
- Por vendedor
- Por período
- Por sucursal
- Por tipo de servicio

---

### 10. CONFIGURACIÓN MULTI-SUCURSAL

**Sucursales (cutai.branch):**
- Código único
- Gerente
- Ubicación de inventario
- Cabinas
- Máquinas

**Cabinas (cutai.cabin):**
- Tipos: estándar, VIP, doble/parejas, láser
- Capacidad
- Máquinas disponibles
- Control de ocupación

**Máquinas Láser (cutai.machine):**
- Tecnologías: Alexandrita, Diodo, Nd:YAG, IPL
- Especificaciones técnicas
- Mantenimiento programado
- Contador de disparos
- Estados: operacional, en mantención, en reparación

**Zonas de Tratamiento (15 pre-configuradas):**
- Facial: Bozo, Mentón, Mejillas, Cejas
- Corporal: Axilas, Brazos, Piernas, Abdomen, Espalda
- Íntima: Bikini básico, completo, brasileño

**Promociones:**
- Tipos: descuento, sesiones extra, paquete, referido
- Vigencia
- Términos y condiciones

---

### 11. COMUNICACIONES AUTOMATIZADAS

**8 Plantillas de Email:**
1. Recordatorio T-48h (con recomendaciones pre-tratamiento)
2. Recordatorio T-24h (confirmación)
3. Recordatorio T-3h (SMS)
4. Política de no-show
5. Encuesta de satisfacción post-servicio
6. Recordatorio de pago de membresía
7. Felicitación de cumpleaños (con descuento 20%)
8. Renovación de membresía

**Integración WhatsApp:**
- Listo para integrar con módulo whatsapp_fullsys
- Confirmaciones de cita
- Recordatorios
- Encuestas
- Seguimiento post-servicio

---

### 12. REPORTES Y KPIs

**Dashboard Diario por Sucursal:**
- Citas programadas vs atendidas
- Show rate %
- Ingresos por servicios
- Ingresos por retail
- Ticket promedio
- Ocupación de cabinas %
- Comisiones generadas
- Propinas

**Reportes Semanales:**
- Nuevos leads
- Conversión a cita
- No-show %
- Rebook %
- Satisfacción (NPS)
- Top 5 servicios
- Top 5 terapeutas

**Reportes Mensuales:**
- Margen retail por marca
- Consumo backbar
- Horas máquina
- Utilización de cabinas
- ROI por campaña/promoción
- Nuevas membresías vs canceladas
- Servicios por categoría

**Reportes Financieros:**
- P&L por sucursal
- Flujo de caja
- Impuestos (ITBMS)
- Comisiones por pagar
- Cuentas por cobrar (membresías)

---

### 13. SEGURIDAD Y PERMISOS

**4 Niveles de Acceso:**

1. **Usuario:** Solo lectura
   - Ver clientes, citas, servicios
   - No puede modificar

2. **Operador/Técnico:**
   - Crear y editar sesiones
   - Registrar servicios realizados
   - Vender retail
   - Ver sus comisiones

3. **Manager:**
   - Control operativo total
   - Gestión de membresías
   - Reportes completos
   - No puede modificar configuración del sistema

4. **Administrador:**
   - Acceso completo
   - Configuración de sistema
   - Sucursales, máquinas, servicios
   - Usuarios y permisos

---

## ESTRUCTURA TÉCNICA

### Modelos Creados (15 modelos principales):

1. **res.partner** (extendido) - Clientes con info médica
2. **cutai.membership** - Membresías
3. **cutai.membership.payment** - Pagos de membresías
4. **cutai.treatment** - Tratamientos láser
5. **cutai.session** - Sesiones de tratamiento
6. **cutai.service** - Catálogo de servicios SPA
7. **cutai.service.category** - Categorías de servicios
8. **cutai.package** - Paquetes y combos
9. **cutai.package.line** - Líneas de paquetes
10. **cutai.appointment.service** - Servicios en cita
11. **cutai.retail.sale** - Ventas retail
12. **cutai.retail.sale.line** - Líneas de venta
13. **cutai.product.brand** - Marcas de productos
14. **cutai.backbar.consumption** - Consumo backbar
15. **calendar.event** (extendido) - Citas mejoradas

### Configuración:
- cutai.branch (Sucursales)
- cutai.cabin (Cabinas)
- cutai.machine (Máquinas)
- cutai.zone (Zonas de tratamiento)
- cutai.promotion (Promociones)
- cutai.backbar.product (Config backbar)

---

## FLUJOS DE TRABAJO

### A. Cliente Nuevo → Membresía → Tratamiento
1. Crear cliente CUTAI con fototipo y alergias
2. Cargar consentimiento informado
3. Crear membresía 9 pagos
4. Sistema genera calendario de pagos automático
5. Crear tratamiento por zona
6. Programar primera sesión
7. Cliente recibe recordatorios T-48h, T-24h, T-3h

### B. Servicio SPA Estándar
1. Cliente llama/llega
2. Se crea cita con servicio(s)
3. Se asigna terapeuta
4. Se reserva cabina
5. Cliente recibe confirmación
6. Terapeuta marca servicio como "en proceso"
7. Al completar: registra observaciones y calificación
8. Sistema calcula comisión automáticamente
9. Cliente recibe encuesta de satisfacción

### C. Venta Retail
1. Cliente compra productos
2. Vendedor crea venta retail
3. Agrega productos con descuentos si aplica
4. Sistema calcula comisión del vendedor
5. Se genera factura
6. Se descuenta del inventario

### D. Paquete/Combo
1. Cliente compra paquete (ej: 10 faciales)
2. Se genera orden de venta
3. Cliente agenda citas usando sesiones del paquete
4. Sistema controla sesiones consumidas vs disponibles
5. Al agotar paquete, se ofrece renovación

---

## INSTALACIÓN

```bash
# 1. Módulo ya creado en:
/root/odoo-one/addons/cutai_laser_clinic/

# 2. Reiniciar Odoo
docker restart odoo-one_odoo18_1

# 3. En Odoo:
- Aplicaciones → Actualizar lista de aplicaciones
- Buscar "CUTAI"
- Instalar "CUTAI Laser Spa Management"

# 4. Configuración inicial:
- Crear sucursales
- Configurar cabinas
- Registrar máquinas
- Revisar servicios pre-configurados
- Configurar comisiones
- Ajustar plantillas de email
```

---

## DEPENDENCIAS

**Odoo Enterprise 18:**
- base, sale, sale_management, crm
- calendar, stock, account
- contacts, hr, hr_expense
- **documents, sign** (Enterprise)
- sms, point_of_sale
- **whatsapp_fullsys** (módulo personalizado)

---

## PRÓXIMOS PASOS RECOMENDADOS

### Fase 1: Configuración Básica
1. Crear sucursales y cabinas
2. Registrar máquinas láser
3. Crear catálogo de servicios SPA
4. Configurar comisiones por servicio
5. Crear paquetes/combos

### Fase 2: Productos
1. Cargar productos retail (cremas, cosméticos)
2. Configurar marcas
3. Establecer comisiones retail
4. Configurar productos backbar
5. Establecer stock mínimo

### Fase 3: Operación
1. Capacitar personal en uso del sistema
2. Migrar clientes existentes
3. Migrar membresías activas
4. Comenzar a agendar citas
5. Registrar servicios y ventas

### Fase 4: Integración
1. Conectar WhatsApp para recordatorios
2. Configurar punto de venta para retail
3. Integrar con contabilidad
4. Configurar impresoras para tickets
5. Habilitar portal del cliente

### Fase 5: Reportes
1. Crear dashboards personalizados
2. Configurar reportes automáticos diarios
3. Reportes semanales para gerencia
4. KPIs mensuales por sucursal
5. Análisis de rentabilidad por servicio

---

## BENEFICIOS DEL SISTEMA

### Operativos:
- Control total de agenda con recursos
- No más doble reserva de cabinas
- Recordatorios automáticos = menos no-shows
- Consumo backbar controlado
- Inventario retail en tiempo real

### Financieros:
- Comisiones calculadas automáticamente
- Control de membresías y pagos
- Moras aplicadas automáticamente
- Facturación integrada
- Reportes financieros precisos

### Comerciales:
- Paquetes y promociones flexibles
- Seguimiento de satisfacción del cliente
- Historial completo por cliente
- Oportunidades de upselling
- Fidelización con membresías

### Gerenciales:
- KPIs en tiempo real
- Reportes por sucursal
- Análisis de rentabilidad
- Control de terapeutas y vendedores
- Toma de decisiones basada en datos

---

## SOPORTE

**FullSys Tecnología Santa Marta**
- Web: https://www.fullsys.com.co
- Email: soporte@fullsys.com.co
- Licencia: LGPL-3
- Versión: 18.0.1.0.0

---

**Sistema desarrollado específicamente para CUTAI Laser SPA**
*Octubre 2025*
