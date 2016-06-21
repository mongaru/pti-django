import json
import pprint
import calendar
import math
from datetime import datetime, timedelta

from django.db.models import Min, Max, Sum
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext

from analisis_variables.models import Station, Record
from django.db.models import Q
from django.db import connection

def home(request):
    return render(request, 'home.html')

def reporte_anual(request):

    estaciones = Station.objects.all()
    
    dataToRender = {
        'estaciones' : estaciones
    }

    return render_to_response('reporte_anual.html', dataToRender)


def potencial_estacion(request, id_estacion=0):
    try:
        station = Station.objects.get(pk=id_estacion)
    except Station.DoesNotExist:
        response_data = {}
        response_data['status'] = 'error'
        response_data['message'] = 'No existe la estacion indicada'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    desde = request.GET.get('desde', datetime.today().strftime("%Y-%m-%d"))
    desde = datetime.strptime(desde, '%Y-%m-%d')
    desde = desde.replace(hour=00, minute=01)
    pprint.pprint(desde)

    fechaHastaDefault = datetime.today() - timedelta(days=10)
    hasta = request.GET.get('hasta', fechaHastaDefault.strftime("%Y-%m-%d"))
    hasta = datetime.strptime(hasta, '%Y-%m-%d')
    hasta = hasta.replace(hour=23, minute=59)
    pprint.pprint(hasta)

    str_desde = desde.strftime("%Y-%m-%d %H:%M:%S")
    str_hasta = hasta.strftime("%Y-%m-%d %H:%M:%S")

    #valores anuales

    anualVel10 = _calculo_anual(str_desde, str_hasta, 'barometer')
    estacionVel10 = _calculo_por_estacion_anio(desde, hasta, 'barometer')

    estacionVel10Titulos = []
    for resultadoEstacion in estacionVel10:
        estacionVel10Titulos.append('estacionVel10 - ' + resultadoEstacion['estacion'])

    mensualVel10 = _calculo_mensual(desde, hasta, 'barometer')

    mensualVel10Titulos = []
    for resultadoMes in mensualVel10:
        mensualVel10Titulos.append('mensualVel10 - ' + _nombre_mes(resultadoMes['month']))

    datosExportar = [
        {'campo' : 'anualVel10Max', 'valor' : anualVel10['max']},
        {'campo' : 'anualVel10Med', 'valor' : anualVel10['min']},
        {'campo' : 'anualVel10Min', 'valor' : anualVel10['avg']}
    ]

    for resultadoEstacion in estacionVel10:
        datosExportar.append({'campo' : 'estacionVel10_' + resultadoEstacion['estacion'], 'valor' : resultadoEstacion['avg']['avg']})

    for resultadoMes in mensualVel10:
        datosExportar.append({'campo' : 'mensualVel10_' + _nombre_mes(resultadoMes['month']), 'valor' : resultadoMes['avg']['avg']})

    dataToRender = {
        'datosExportar' : datosExportar,
        'estacionVel10Titulos' : estacionVel10Titulos,
        'mensualVel10Titulos' : mensualVel10Titulos
    }

    return render_to_response('reporte_anual_tabla.html', dataToRender)
    # return render_to_response('home.html', dict(respuestaData.items() + _getUserData(request).items()))

# montesqie
# john love
# maquiavelo
# lenin




def _calculo_anual(fecha_desde, fecha_hasta, variable):
    # select to_char(a."dateTime", 'YYYY-MM-DD-HH24') as fechaIndice, avg(a.barometer), avg(a."outTemp") from stations_data as a where a.id < 11000 group by fechaIndice order by fechaIndice asc
    query = 'select min(a.'+variable+'), max(a.'+variable+'), avg(a.'+variable+') from analisis_variables_record as a where a."dateTime" > %s and a."dateTime" < %s'
    cursor = connection.cursor()
    cursor.execute(query, [fecha_desde, fecha_hasta])
    rows = _fields_to_dict(cursor)

    return rows[0]
    # rows = cursor.fetchall()

    # for row in rows:
    #     pprint.pprint(row)

def _calculo_mensual(fecha_inicio, fecha_fin, variable):

    fecha_desde = fecha_inicio
    ultimo_dia = calendar.monthrange(fecha_desde.year, fecha_desde.month)[1]
    fecha_hasta = fecha_desde.replace(day=ultimo_dia)

    # pprint.pprint(fecha_desde)
    # pprint.pprint(fecha_hasta)
    # pprint.pprint("inicia while")

    resultadosMes = []
    
    while (fecha_desde < fecha_fin):

        # cargar datos
        str_desde = fecha_desde.strftime("%Y-%m-%d %H:%M:%S")
        str_hasta = fecha_hasta.strftime("%Y-%m-%d %H:%M:%S")

        query = 'select avg(a.'+variable+') from analisis_variables_record as a where a."dateTime" > %s and a."dateTime" < %s'
        cursor = connection.cursor()
        cursor.execute(query, [str_desde, str_hasta])
        rows = _fields_to_dict(cursor)

        resultadosMes.append({'month' : fecha_desde.month, 'year' : fecha_desde.year, 'avg' : rows[0]})


        # aumentar la fecha - sumar un mes
        fecha_desde = _sumar_mes(fecha_desde)
        fecha_desde = fecha_desde.replace(day=1)
        # obtener el ultimo dia del mes
        ultimo_dia = calendar.monthrange(fecha_desde.year, fecha_desde.month)[1]
        fecha_hasta = fecha_desde.replace(day=ultimo_dia, hour=23, minute=59)

        # pprint.pprint(fecha_desde)
        # pprint.pprint(fecha_hasta)

    # pprint.pprint(resultadosMes)
    return resultadosMes

def _calculo_por_estacion_anio(fecha_inicio, fecha_fin, variable):

    fechasEstaciones = _fechasParaEstaciones(fecha_inicio, fecha_fin)

    pprint.pprint(fechasEstaciones)
    resultadosMes = []

    for estacion in fechasEstaciones:
        # cargar datos
        str_desde = estacion['inicio'].strftime("%Y-%m-%d %H:%M:%S")
        str_hasta = estacion['fin'].strftime("%Y-%m-%d %H:%M:%S")

        query = 'select avg(a.'+variable+') from analisis_variables_record as a where a."dateTime" > %s and a."dateTime" < %s'
        cursor = connection.cursor()
        cursor.execute(query, [str_desde, str_hasta])
        rows = _fields_to_dict(cursor)

        resultadosMes.append({'month' : estacion['inicio'].month, 'year' : estacion['inicio'].year, 'avg' : rows[0], 'estacion' : estacion['estacion']})

    return resultadosMes

def _estacionDelAnio(fecha):

    # verano - 21 de diciembre - 20 de marzo 
    # otono - 21 de marzo - 20 de junio
    # invierno - 21 de junio - 20 de setiembre
    # setiembre - 21 de setiembre - 20 de diciembre

    # se utiliza un formato de mes concatenado al dia y se convierne en numero
    # ejemplo: 01/enero = 101, 05/marzo = 305
    # entonces se compara de manera numerica la estacion de la fecha
    
    estaciones = [
        {'estacion' : 'verano', 'inicio' : 1221, 'fin' : 1231},
        {'estacion' : 'verano', 'inicio' : 101, 'fin' : 320},
        {'estacion' : 'otono', 'inicio' : 321, 'fin' : 620},
        {'estacion' : 'invierno', 'inicio' : 621, 'fin' : 920},
        {'estacion' : 'primavera', 'inicio' : 921, 'fin' : 1220},
    ]

    # obtenes el valor de mes/dia de la fecha indicada
    fechaEstacion = int(fecha.strftime("%m") + fecha.strftime("%d"))

    pprint.pprint(fechaEstacion)

    for estacion in estaciones:
        if (fechaEstacion >= estacion['inicio'] and fechaEstacion <= estacion["fin"]):
            pprint.pprint(estacion['estacion'])
            return estacion['estacion']

    return 'sin estacion'

def _fechasParaEstaciones(fecha_inicio, fecha_fin):

    estacionNombre = _estacionDelAnio(fecha_inicio)
    estacionActual = estacionNombre
    
    # fecha_estacion_inicia = fecha_inicio
    # fecha_estacion_fin = None

    estacionesDisponibles = []
    estacionesDisponibles.append({'estacion' : estacionNombre, 'inicio' : fecha_inicio, 'fin' : None})

    while (fecha_inicio <= fecha_fin):
        # cuando cambie la estacion actual entonces registramos el inicio de una nueva
        if (estacionNombre != estacionActual):
            # guardamos la referencia a la estacion nueva
            estacionActual = estacionNombre
            # indicamos la fecha de fin de la estacion anterior
            fecha_estacion_fin = fecha_inicio - timedelta(days=1)
            fecha_estacion_fin.replace(hour=23, minute=59)
            # cargamos la fecha de fin a la posicion anterior
            estacionesDisponibles[len(estacionesDisponibles) - 1]['fin'] = fecha_estacion_fin
            # cargamos la nueva estacion con la fecha de inicio
            estacionesDisponibles.append({'estacion' : estacionNombre, 'inicio' : fecha_inicio, 'fin' : None})

        # incrementamos el dia y calculamos de nuevo la estacion
        fecha_inicio = fecha_inicio + timedelta(days=1)
        estacionNombre = _estacionDelAnio(fecha_inicio)
        pprint.pprint(fecha_inicio)
        pprint.pprint(estacionNombre)

    # indicamos la fecha de fin al ultimo registro
    estacionesDisponibles[len(estacionesDisponibles) - 1]['fin'] = fecha_fin

    return estacionesDisponibles



def _sumar_mes(fecha):

    # se utiliza este metodo para restar un mes pues la solucion:
    # fecha_desde + timedelta(months=+1)
    # no funciona pues timedelta no acepta el parametro months

    mes = fecha.month
    
    while (fecha.month == mes):
        fecha = fecha + timedelta(days=10)

    return fecha



def _fields_to_dict(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def _nombre_mes(mes):
    nombreMeses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']
    return nombreMeses[mes - 1]
