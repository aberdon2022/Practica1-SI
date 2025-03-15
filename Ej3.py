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

df['fecha_a'] = pd.to_datetime(df['fecha_a'])
df['dia'] = df['fecha_a'].dt.day_name()

# Número de incidentes

df_por_empleado_fraude = df[df['tipo_incidencia'] == 'Fraude'].groupby('empleado').agg({'ticket_id': 'count'}).reset_index().rename(columns={'ticket_id': 'count'})
df_por_nivel_fraude = df[df['tipo_incidencia'] == 'Fraude'].groupby('nivel_empleado').agg({'ticket_id': 'count'}).reset_index().rename(columns={'ticket_id': 'count'})
df_por_cliente_fraude = df[df['tipo_incidencia'] == 'Fraude'].groupby('cliente').agg({'ticket_id': 'count'}).reset_index().rename(columns={'ticket_id': 'count'})
df_por_tipo_incidencia = df.groupby('tipo_incidencia').agg({'ticket_id': 'count'}).reset_index().rename(columns={'ticket_id': 'count'})
df_por_dia_fraude = df[df['tipo_incidencia'] == 'Fraude'].groupby('dia').agg({'ticket_id': 'count'}).reset_index().rename(columns={'ticket_id': 'count'})

print(df_por_empleado_fraude.to_string())
print(df_por_nivel_fraude.to_string())
print(df_por_cliente_fraude.to_string())
print(df_por_tipo_incidencia.to_string())
print(df_por_dia_fraude.to_string())

# Numero de actuaciones por empleado

df_contactos_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('empleado').agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})
df_contactos_empleado_por_nivel = df[df['tipo_incidencia'] == 'Fraude'].groupby(['nivel_empleado']).agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})
df_contactos_cliente = df[df['tipo_incidencia'] == 'Fraude'].groupby(['cliente']).agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})
df_contactos_tipo_incidencia = df.groupby('tipo_incidencia').agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})
df_contactos_por_dia = df[df['tipo_incidencia'] == 'Fraude'].groupby('dia').agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})

print(df_contactos_empleado.to_string())
print(df_contactos_empleado_por_nivel.to_string())
print(df_contactos_cliente.to_string())
print(df_contactos_tipo_incidencia.to_string())
print(df_contactos_por_dia.to_string())

#Analisis estadistico

estadisticas_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('empleado').agg({'ticket_id':['count','median', 'mean', 'var', 'min', 'max']}).reset_index()
estadisticas_nivel = df[df['tipo_incidencia'] == 'Fraude'].groupby('nivel_empleado').agg({'ticket_id':['count','median', 'mean', 'var', 'min', 'max']}).reset_index()
estadisticas_cliente = df[df['tipo_incidencia'] == 'Fraude'].groupby('cliente').agg({'ticket_id':['count','median', 'mean', 'var', 'min', 'max']}).reset_index()
estadisticas_tipo_incidencia = df.groupby('tipo_incidencia').agg({'ticket_id':['count','median', 'mean', 'var', 'min', 'max']}).reset_index()
estadisticas_dia = df[df['tipo_incidencia'] == 'Fraude'].groupby('dia').agg({'ticket_id':['count','median', 'mean', 'var', 'min', 'max']}).reset_index()

dias = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

estadisticas_dia['dia'] = estadisticas_dia['dia'].map(dias)

print()
print("Estadisticas por empleado\n" + estadisticas_empleado.to_string() + "\n")
print("Estadisticas por nivel de empleado\n" + estadisticas_nivel.to_string() + "\n")
print("Estadisticas por cliente\n" + estadisticas_cliente.to_string() + "\n")
print("Estadisticas por tipos de incidencia\n" + estadisticas_tipo_incidencia.to_string() + "\n")
print("Estadisticas por dia\n" +estadisticas_dia.to_string() + "\n")