from flask import Flask, render_template, abort
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.io as pio
app = Flask(__name__)

def update_fecha_cierre(df):
    df['fecha_c'] = df.groupby('ticket_id')['fecha_atencion_ticket'].transform('max')
    return df

def get_df():
    results = []
    con = sqlite3.connect('test.db')
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
    df['dia'] = df['fecha_a'].dt.day_name()

    return df

def res_ej2():
    df = get_df()

    total_muestras = df.shape[0]

    df_mayor_5 = df[df['satisfaccion_cliente'] >= 5]
    cuenta_incidentes = df_mayor_5.groupby('cliente').size()
    media_incidentes = cuenta_incidentes.mean()
    std_incidentes = cuenta_incidentes.std()

    incidentes_por_cliente = df.groupby('cliente').size()
    media_incidentes_cliente = incidentes_por_cliente.mean()
    std_incidentes_cliente = incidentes_por_cliente.std()

    horas_por_tiquet = df.groupby('ticket_id')['tiempo'].sum().reset_index()
    media_horas = horas_por_tiquet['tiempo'].mean()
    std_horas = horas_por_tiquet['tiempo'].std()

    horas_por_empleado = df.groupby('empleado')['tiempo'].sum().reset_index()
    min_horas = horas_por_empleado['tiempo'].min()
    max_horas = horas_por_empleado['tiempo'].max()

    df['tiempo_incidente'] = (df['fecha_c'] - df['fecha_a']).dt.total_seconds() / 3600
    min_tiempo = df['tiempo_incidente'].min()
    max_tiempo = df['tiempo_incidente'].max()

    incidentes_por_empleado = df.groupby('empleado').size()
    min_incidentes = incidentes_por_empleado.min()
    max_incidentes = incidentes_por_empleado.max()

    results = {
        "total_muestras": total_muestras,
        "media_incidentes": media_incidentes,
        "std_incidentes": std_incidentes,
        "media_incidentes_cliente": media_incidentes_cliente,
        "std_incidentes_cliente": std_incidentes_cliente,
        "media_horas": media_horas,
        "std_horas": std_horas,
        "min_horas": min_horas,
        "max_horas": max_horas,
        "min_tiempo": min_tiempo,
        "max_tiempo": max_tiempo,
        "min_incidentes": min_incidentes,
        "max_incidentes": max_incidentes
    }
    return results

def res_ej3():
    df = get_df()

    df_por_empleado_fraude = df[df['tipo_incidencia'] == 'Fraude'].groupby('empleado').agg({'ticket_id': 'count'}).reset_index().rename(columns={'ticket_id': 'count'})
    df_por_nivel_fraude = df[df['tipo_incidencia'] == 'Fraude'].groupby('nivel_empleado').agg({'ticket_id': 'count'}).reset_index().rename(columns={'ticket_id': 'count'})
    df_por_cliente_fraude = df[df['tipo_incidencia'] == 'Fraude'].groupby('cliente').agg({'ticket_id': 'count'}).reset_index().rename(columns={'ticket_id': 'count'})
    df_por_tipo_incidencia = df.groupby('tipo_incidencia').agg({'ticket_id': 'count'}).reset_index().rename(columns={'ticket_id': 'count'})
    df_por_dia_fraude = df[df['tipo_incidencia'] == 'Fraude'].groupby('dia').agg({'ticket_id': 'count'}).reset_index().rename(columns={'ticket_id': 'count'})

    df_contactos_empleado = df[df['tipo_incidencia'] == 'Fraude'].groupby('empleado').agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})
    df_contactos_empleado_por_nivel = df[df['tipo_incidencia'] == 'Fraude'].groupby(['nivel_empleado']).agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})
    df_contactos_cliente = df[df['tipo_incidencia'] == 'Fraude'].groupby(['cliente']).agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})
    df_contactos_tipo_incidencia = df.groupby('tipo_incidencia').agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})
    df_contactos_por_dia = df[df['tipo_incidencia'] == 'Fraude'].groupby('dia').agg({'fecha_atencion_ticket': 'count'}).reset_index().rename(columns={'fecha_atencion_ticket': 'count'})

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

    results = {
        "df_por_empleado_fraude": df_por_empleado_fraude.to_html(),
        "df_por_nivel_fraude": df_por_nivel_fraude.to_html(),
        "df_por_cliente_fraude": df_por_cliente_fraude.to_html(),
        "df_por_tipo_incidencia": df_por_tipo_incidencia.to_html(),
        "df_por_dia_fraude": df_por_dia_fraude.to_html(),
        "df_contactos_empleado": df_contactos_empleado.to_html(),
        "df_contactos_empleado_por_nivel": df_contactos_empleado_por_nivel.to_html(),
        "df_contactos_cliente": df_contactos_cliente.to_html(),
        "df_contactos_tipo_incidencia": df_contactos_tipo_incidencia.to_html(),
        "df_contactos_por_dia": df_contactos_por_dia.to_html(),
        "estadisticas_empleado": estadisticas_empleado.to_html(),
        "estadisticas_nivel": estadisticas_nivel.to_html(),
        "estadisticas_cliente": estadisticas_cliente.to_html(),
        "estadisticas_tipo_incidencia": estadisticas_tipo_incidencia.to_html(),
        "estadisticas_dia": estadisticas_dia.to_html()
    }
    return results

def res_ej4():
    df = get_df()

    df['tiempo_resolucion'] = (df['fecha_c'] - df['fecha_a']).dt.total_seconds() / 86400

    # Gráfico 1
    media_tiempo_mantenimiento = df.groupby('es_mantenimiento')['tiempo_resolucion'].mean().reset_index()
    media_tiempo_mantenimiento['es_mantenimiento'] = media_tiempo_mantenimiento['es_mantenimiento'].map({0: 'No', 1: 'Sí'})
    fig1 = px.bar(media_tiempo_mantenimiento, x='es_mantenimiento', y='tiempo_resolucion',
                  color='es_mantenimiento',
                  labels={'es_mantenimiento':'Es mantenimiento?', 'tiempo_resolucion':'Tiempo medio de resolución (días)'},
                  title='Tiempo medio de resolución por tipo de mantenimiento')
    grafico1 = pio.to_html(fig1, full_html=False, include_plotlyjs='cdn')

    # Gráfico 2
    df_ticket = df.groupby('ticket_id').agg(tiempo_resolucion=('tiempo_resolucion', 'sum'), tipo_incidencia=('tipo_incidencia', 'first')).reset_index()
    percentiles = df_ticket.groupby('tipo_incidencia')['tiempo_resolucion'].quantile([0.05, 0.90]).unstack()
    fig2 = px.box(df_ticket, x='tipo_incidencia', y='tiempo_resolucion',
                  labels={'tiempo_resolucion':'Tiempo de Resolución (días)', 'tipo_incidencia':'Tipo de Incidente'},
                  title='Tiempos de resolución por tipo de incidente (Percentiles 5%-90%)')
    for tipo in percentiles.index:
        p5 = percentiles.loc[tipo, 0.05]
        p90 = percentiles.loc[tipo, 0.90]
        fig2.add_shape(
            type="line",
            x0=tipo, x1=tipo,
            y0=p5, y1=p90,
            line=dict(color="red", width=2, dash="dash"),
            xref="x", yref="y"
        )
    grafico2 = pio.to_html(fig2, full_html=False, include_plotlyjs=False)

    # Gráfico 3
    df_mantenimiento = df[(df['es_mantenimiento'] == 1) & (df['tipo_incidencia'] != '1')]
    clientes_criticos = df_mantenimiento.groupby('cliente')['ticket_id'].nunique().sort_values(ascending=False).head(5).reset_index()

    fig3 = px.bar(clientes_criticos, x='cliente', y='ticket_id',
                  labels={'ticket_id':'Número de Incidentes', 'cliente':'Cliente'},
                  title='Top 5 Clientes Más Críticos')
    grafico3 = pio.to_html(fig3, full_html=False, include_plotlyjs=False)

    # Gráfico 4
    actuaciones_empleados = df.groupby('empleado')['ticket_id'].nunique().sort_values(ascending=False).reset_index()
    fig4 = px.bar(actuaciones_empleados, x='empleado', y='ticket_id',
                  labels={'empleado':'Empleado', 'ticket_id':'Número de Actuaciones'},
                  title='Total de Actuaciones Realizadas por los Empleados')
    grafico4 = pio.to_html(fig4, full_html=False, include_plotlyjs=False)

    df['fecha_atencion_ticket'] = pd.to_datetime(df['fecha_atencion_ticket'])
    df['day'] = df['fecha_atencion_ticket'].dt.day_name()
    dias = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    df['day'] = df['day'].map(dias)
    df['day'] = pd.Categorical(df['day'], categories=['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'], ordered=True)
    actuaciones_dias = df['day'].value_counts().sort_index().reset_index()
    actuaciones_dias.columns = ['day', 'count']
    fig5 = px.bar(actuaciones_dias, x='day', y='count',
                  labels={'day':'Día de la Semana', 'count':'Actuaciones Realizadas'},
                  title='Actuaciones por día de la semana')
    grafico5 = pio.to_html(fig5, full_html=False, include_plotlyjs=False)

    results = {
        'grafico1': grafico1,
        'grafico2': grafico2,
        'grafico3': grafico3,
        'grafico4': grafico4,
        'grafico5': grafico5
    }
    return results

@app.route('/<string:ejercicio>')
def ejercicios(ejercicio):
    if ejercicio == 'ej2':
        results = res_ej2()
        return render_template('ej2.html', results=results)
    elif ejercicio == 'ej3':
        results = res_ej3()
        return render_template('ej3.html', results=results)
    elif ejercicio == 'ej4':
        results = res_ej4()
        return render_template('ej4.html', results=results)
    else:
        abort(404)
@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run()