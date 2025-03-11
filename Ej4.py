import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


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
df['fecha_c'] = pd.to_datetime(df['fecha_c'])

df['tiempo_resolucion'] = (df['fecha_c'] - df['fecha_a']).dt.total_seconds() / 86400  # Convertir segundos a días

# Calcular la media por tipo de mantenimiento con pandas
media_tiempo_mantenimiento = df.groupby('es_mantenimiento')['tiempo_resolucion'].mean()

media_tiempo_mantenimiento.plot(kind='bar', color=['blue', 'orange'])
plt.xlabel("¿Es mantenimiento?")
plt.ylabel("Tiempo medio de resolución (días)")
plt.title("Tiempo medio de resolución por tipo de mantenimiento")
plt.xticks(ticks=[0, 1], labels=['No', 'Sí'], rotation=0)
plt.show()

# Calcular percentiles 5% y 90% por tipo de incidente con pandas
percentiles = df.groupby('tipo_incidencia')['tiempo_resolucion'].quantile([0.05, 0.90]).unstack()

print(percentiles)

df.boxplot(column='tiempo_resolucion', by='tipo_incidencia', grid=False, showfliers=False)
plt.xlabel("Tipo de Incidente")
plt.ylabel("Tiempo de Resolución (días)")
plt.title("Distribución de tiempos de resolución por tipo de incidente (Percentiles 5%-90%)")
plt.suptitle("")  # Eliminar título automático extra
plt.xticks(rotation=45)

# Dibujar líneas de percentiles 5% y 90%
for i, tipo in enumerate(df['tipo_incidencia'].unique()):
    p5 = percentiles.loc[tipo, 0.05]
    p90 = percentiles.loc[tipo, 0.90]
    plt.plot([i+1, i+1], [p5, p90], color='red', linewidth=2, linestyle='dashed')

plt.show()