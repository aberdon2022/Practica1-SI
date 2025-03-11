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
df_por_dia_fraude = df[df['tipo_incidencia'] == 'Fraude'].groupby('dia').agg({'ticket_id': 'count'}).reset_index().rename(columns={'ticket_id': 'count'})

print(df_por_empleado_fraude.to_string())
print(df_por_nivel_fraude.to_string())
print(df_por_cliente_fraude.to_string())
print(df_por_dia_fraude.to_string())

# Numero de actuaciones por empleado

df_contactos_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('empleado').agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})
df_contactos_empleado_por_nivel = df[df['tipo_incidencia'] == 'Fraude'].groupby(['nivel_empleado']).agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})
df_contactos_cliente = df[df['tipo_incidencia'] == 'Fraude'].groupby(['cliente']).agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})
df_contactos_por_dia = df[df['tipo_incidencia'] == 'Fraude'].groupby(['dia']).agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})

print(df_contactos_empleado.to_string())
print(df_contactos_empleado_por_nivel.to_string())
print(df_contactos_cliente.to_string())
print(df_contactos_por_dia.to_string())

#Analisis estadistico

mediana_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('empleado').agg({'ticket_id': 'count'}).median()
media_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('empleado').agg({'ticket_id': 'count'}).mean()
varianza_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('empleado').agg({'ticket_id': 'count'}).var()
max_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('empleado').agg({'ticket_id': 'count'}).max()
min_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('empleado').agg({'ticket_id': 'count'}).min()

print()
print("Mediana por empleado: " + str(mediana_empleado.values[0]))
print("Media por empleado: " + str(media_empleado.values[0]))
print("Varianza por empleado: " + str(varianza_empleado.values[0]))
print("Valor max por empleado: " + str(max_empleado.values[0]))
print("Valor min por empleado: " + str(min_empleado.values[0]))
print()

mediana_nivel_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('nivel_empleado').agg({'ticket_id': 'count'}).median()
media_nivel_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('nivel_empleado').agg({'ticket_id': 'count'}).mean()
varianza_nivel_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('nivel_empleado').agg({'ticket_id': 'count'}).var()
max_nivel_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('nivel_empleado').agg({'ticket_id': 'count'}).max()
min_nivel_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('nivel_empleado').agg({'ticket_id': 'count'}).min()

print("Mediana por nivel de empleado: " + str(mediana_nivel_empleado.values[0]))
print("Media por nivel de empleado: " + str(media_nivel_empleado.values[0]))
print("Varianza por nivel de empleado: " + str(varianza_nivel_empleado.values[0]))
print("Valor max por nivel de empleado: " + str(max_nivel_empleado.values[0]))
print("Valor min por nivel de empleado: " + str(min_nivel_empleado.values[0]))
print()

mediana_cliente = df[df['tipo_incidencia'] == 'Fraude'].groupby('cliente').agg({'ticket_id': 'count'}).median()
media_cliente = df[df['tipo_incidencia'] == 'Fraude'].groupby('cliente').agg({'ticket_id': 'count'}).mean()
varianza_cliente = df[df['tipo_incidencia'] == 'Fraude'].groupby('cliente').agg({'ticket_id': 'count'}).var()
max_cliente = df[df['tipo_incidencia'] == 'Fraude'].groupby('cliente').agg({'ticket_id': 'count'}).max()
min_cliente = df[df['tipo_incidencia'] == 'Fraude'].groupby('cliente').agg({'ticket_id': 'count'}).min()

print("Mediana por cliente: " + str(mediana_cliente.values[0]))
print("Media por cliente: " + str(media_cliente.values[0]))
print("Varianza por cliente: " + str(varianza_cliente.values[0]))
print("Valor max por cliente: " + str(max_cliente.values[0]))
print("Valor min por cliente: " + str(min_cliente.values[0]))
print()

mediana_dia = df[df['tipo_incidencia'] == 'Fraude'].groupby('dia').agg({'ticket_id': 'count'}).median()
media_dia = df[df['tipo_incidencia'] == 'Fraude'].groupby('dia').agg({'ticket_id': 'count'}).mean()
varianza_dia = df[df['tipo_incidencia'] == 'Fraude'].groupby('dia').agg({'ticket_id': 'count'}).var()
max_dia = df[df['tipo_incidencia'] == 'Fraude'].groupby('dia').agg({'ticket_id': 'count'}).max()
min_dia = df[df['tipo_incidencia'] == 'Fraude'].groupby('dia').agg({'ticket_id': 'count'}).min()

print("Mediana por dia: " + str(mediana_dia.values[0]))
print("Media por dia: " + str(media_dia.values[0]))
print("Varianza por dia: " + str(varianza_dia.values[0]))
print("Valor max por dia: " + str(max_dia.values[0]))
print("Valor min por dia: " + str(min_dia.values[0]))