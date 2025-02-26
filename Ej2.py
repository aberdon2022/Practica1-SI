import sqlite3
import pandas as pd

def update_fecha_cierre(df):
    df['fecha_c'] = df.groupby('ticket_id')['fecha_atencion_ticket'].transform('max')
    return df

con = sqlite3.connect('test.db')
cursor = con.cursor()

sql = """SELECT t.id AS ticket_id, t.fecha_apertura AS fecha_a, t.fecha_cierre AS fecha_c, 
       t.es_mantenimiento, 
       t.satisfaccion_cliente, c.nombre as cliente, c.telefono, c.provincia,
       ti.nombre as tipo_incidencia, cet.fecha AS fecha_atencion_ticket, cet.tiempo, 
       e.nombre as empleado, e.nivel AS nivel_empleado, e.fecha_contrato AS fecha_contrato_empleado
       FROM tickets t
       JOIN clientes c ON t.cliente_id = c.id
       JOIN tipo_incidencia ti ON t.tipo_incidencia_id = ti.id
       JOIN contacto_empleados_ticket cet ON t.id = cet.ticket_id
       JOIN empleados e ON cet.empleado_id = e.id
       """

df = pd.read_sql_query(sql, con)

con.close()

df = update_fecha_cierre(df)

print("Número de muestras totales del dataframe",df.shape[0])

df_mayor_5 = df[df['satisfaccion_cliente'] >= 5]

cuenta_incidentes = df_mayor_5.groupby('cliente').size()

print("Media incidentes con satisfacción mayor o igual a 5:", cuenta_incidentes.mean())
print("Desviación estándar incidentes con satisfacción mayor o igual a 5:", cuenta_incidentes.std())