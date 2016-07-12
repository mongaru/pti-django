import json
import pprint
import calendar
import math
import csv
import decimal
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
from django.http import HttpResponse

from analisis_variables.models import Station, Record
from django.db.models import Q
from django.db import connection


def reporte_anual_generacion(request):
    
	formato = request.GET.get('formato', 'tabla')

	idEstaciones = request.GET.get('estaciones', '1')
	idEstaciones = idEstaciones.split('-')

	desde = request.GET.get('desde', datetime.today().strftime("%Y-%m-%d"))
	desde = datetime.today().strftime("%Y-%m-%d") if desde == '' else desde
	desde = datetime.strptime(desde, '%Y-%m-%d')
	desde = desde.replace(hour=00, minute=01)

	fechaHastaDefault = datetime.today() - timedelta(days=10)
	hasta = request.GET.get('hasta', fechaHastaDefault.strftime("%Y-%m-%d"))
	hasta = fechaHastaDefault.strftime("%Y-%m-%d") if hasta == '' else hasta
	hasta = datetime.strptime(hasta, '%Y-%m-%d')
	hasta = hasta.replace(hour=23, minute=59)

	titulos = None
	valores = []

	for id_estacion in idEstaciones:
		valoresEstacion = _generar_reporte_anual_estacion(desde, hasta, id_estacion)

		if (len(valoresEstacion) > 0 and titulos == None):
			titulos = valoresEstacion['titulos']

		if (len(valoresEstacion) > 0):
			valores.append(valoresEstacion['valores'])
		else:
			valores.append(valoresEstacion)


	dataToRender = {
		'datosExportar' : valores,
		'titulos' : titulos
	}

	if (formato == 'tabla'):
		return render_to_response('reporte_anual_tabla.html', dataToRender)
	
	if (formato == 'csv'):
		# Create the HttpResponse object with the appropriate CSV header.
	    response = HttpResponse(content_type='text/csv')
	    response['Content-Disposition'] = 'attachment; filename="reporte_anual.csv"'

	    writer = csv.writer(response)

	    writer.writerow(titulos)
	    
	    for fila in valores:
	    	writer.writerow(fila)

	    return response

    # return render_to_response('home.html', dict(respuestaData.items() + _getUserData(request).items()))

def _generar_reporte_anual_estacion(desde, hasta, id_estacion):

	try:
		station = Station.objects.get(pk=id_estacion)
	except Station.DoesNotExist:
		return []

	#valores anuales
	anualVel10 = _calculo_anual(desde, hasta, '"windSpeed"', station)
	anualWindDir10 = _calculo_anual(desde, hasta, '"windDir"', station)

	anualVel50 = _calculo_anual(desde, hasta, '"windSpeed"', station)
	anualWindDir50 = _calculo_anual(desde, hasta, '"windDir"', station)

	anualVel80 = _calculo_anual(desde, hasta, '"windSpeed"', station)
	anualWindDir80 = _calculo_anual(desde, hasta, '"windDir"', station)

	anualPresion = _calculo_anual(desde, hasta, 'pressure', station)
	anualRadiacion = _calculo_anual(desde, hasta, 'radiation', station)
	anualHumedad = _calculo_anual(desde, hasta, '"outHumidity"', station)
	anualDensidad = _calculo_anual(desde, hasta, 'rain', station)
	anualTemp2 = _calculo_anual(desde, hasta, '"outTemp"', station)

	estacionVel10 = _calculo_por_estacion_anio(desde, hasta, '"windSpeed"', station)
	estacionVel50 = _calculo_por_estacion_anio(desde, hasta, '"windSpeed"', station)
	estacionRadiacion = _calculo_por_estacion_anio(desde, hasta, 'radiation', station)
	
	mensualVel10 = _calculo_mensual(desde, hasta, '"windSpeed"', station)
	mensualRadiacion = _calculo_mensual(desde, hasta, 'radiation', station)

	# colecta de titulos para las columnas
	titulosExportar = [
		'#', 'Estacion', 'Latitud', 'Longitud', 'Departamento', 'Elevacion', 'Tipo Archivo',
		'anualVel10Max', 'anualVel10Med', 'anualVel10Min',
		'anualDir10Max', 'anualDir10Med', 'anualDir10Min',
		'anualVel50Max', 'anualVel50Med', 'anualVel50Min',
		'anualDir50Max', 'anualDir50Med', 'anualDir50Min',
		'anualVel80Max', 'anualVel80Med', 'anualVel80Min',
		'anualDir80Max', 'anualDir80Med', 'anualDir80Min',
		'anualPresionMax', 'anualPresionMed', 'anualPresionMin',
		'anualRadiacionMax', 'anualRadiacionMed', 'anualRadiacionMin',
		'anualHumedadMax', 'anualHumedadMed', 'anualHumedadMin',
		'anualDensidadMax', 'anualDensidadMed', 'anualDensidadMin',
		'anualTemp2Max', 'anualTemp2Med', 'anualTemp2Min'
	]

	for resultadoEstacion in estacionVel10:
		titulosExportar.append('estacionVel10 - ' + resultadoEstacion['estacion'])

	for resultadoEstacion in estacionVel50:
		titulosExportar.append('estacionVel50 - ' + resultadoEstacion['estacion'])

	for resultadoEstacion in estacionRadiacion:
		titulosExportar.append('estacionRadiacion - ' + resultadoEstacion['estacion'])

	for resultadoMes in mensualVel10:
		# titulosExportar.append('mensualVel10 - ' + _nombre_mes(resultadoMes['month']))
		titulosExportar.append('mensualVel10 - ' + resultadoMes['month'])

	for resultadoMes in mensualRadiacion:
		# titulosExportar.append('mensualRadiacion - ' + _nombre_mes(resultadoMes['month']))
		titulosExportar.append('mensualRadiacion - ' + resultadoMes['month'])


	# colecta de valores en el mismo orden de los titulos para la exportacion a csv
	datosExportar = [
		station.pk, station.name, station.lat, station.lg, station.departamento, station.elevation, station.type.type,
		anualVel10['max'], anualVel10['avg'], anualVel10['min'],
		anualWindDir10['max'], anualWindDir10['avg'], anualWindDir10['min'],
		anualVel50['max'], anualVel50['avg'], anualVel50['min'],
		anualWindDir50['max'], anualWindDir50['avg'], anualWindDir50['min'],
		anualVel80['max'], anualVel80['avg'], anualVel80['min'],
		anualWindDir80['max'], anualWindDir80['avg'], anualWindDir80['min'],
		anualPresion['max'], anualPresion['avg'], anualPresion['min'],
		anualRadiacion['max'], anualRadiacion['avg'], anualRadiacion['min'],
		anualHumedad['max'], anualHumedad['avg'], anualHumedad['min'],
		anualDensidad['max'], anualDensidad['avg'], anualDensidad['min'],
		anualTemp2['max'], anualTemp2['avg'], anualTemp2['min']
	]

	for resultadoEstacion in estacionVel10:
		datosExportar.append(resultadoEstacion['avg']['avg'])

	for resultadoEstacion in estacionVel50:
		datosExportar.append(resultadoEstacion['avg']['avg'])

	for resultadoEstacion in estacionRadiacion:
		datosExportar.append(resultadoEstacion['avg']['avg'])

	for resultadoMes in mensualVel10:
		datosExportar.append(resultadoMes['avg']['avg'])

	for resultadoMes in mensualRadiacion:
		datosExportar.append(resultadoMes['avg']['avg'])

	for i in range(0, len(datosExportar)):
		# no imprimir los titulos
		if (i < 7):
			continue

		datosExportar[i] = _redondeo(datosExportar[i])


	datosResultados = {
		'titulos' : titulosExportar,
		'valores' : datosExportar
	}

	return datosResultados


def _calculo_anual(fecha_desde, fecha_hasta, variable, station):

	fecha_desde = fecha_desde.strftime("%Y-%m-%d %H:%M:%S")
	fecha_hasta = fecha_hasta.strftime("%Y-%m-%d %H:%M:%S")

	# select to_char(a."dateTime", 'YYYY-MM-DD-HH24') as fechaIndice, avg(a.barometer), avg(a."outTemp") from stations_data as a where a.id < 11000 group by fechaIndice order by fechaIndice asc
	# query = 'select min(a.'+variable+'), max(a.'+variable+'), avg(a.'+variable+') from analisis_variables_record as a where a."dateTime" > %s and a."dateTime" < %s and a.station_id = %s'
	query = 'select min(a1.'+'min'+'), max(a1.'+'max'+'), avg(a1.'+'avg'+') from (' + 'select to_char(a."dateTime", \'MM-DD-HH\') as fechaIndice, min(a.'+variable+'), max(a.'+variable+'), avg(a.'+variable+') from analisis_variables_record as a where a.station_id = %s group by fechaIndice '+'order by fechaIndice asc) a1'

	cursor = connection.cursor()
	cursor.execute(query, [station.pk])
	rows = _fields_to_dict(cursor)

	return rows[0]

def _calculo_mensual(fecha_inicio, fecha_fin, variable, station):

    fecha_desde = fecha_inicio
    ultimo_dia = calendar.monthrange(fecha_desde.year, fecha_desde.month)[1]
    fecha_hasta = fecha_desde.replace(day=ultimo_dia)

    meses = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    resultadosMes = []
    
    for mes in meses:

        # cargar datos
        # str_desde = fecha_desde.strftime("%Y-%m-%d %H:%M:%S")
        # str_hasta = fecha_hasta.strftime("%Y-%m-%d %H:%M:%S")

        # query = 'select avg(a.'+variable+') from analisis_variables_record as a where a."dateTime" > %s and a."dateTime" < %s and a.station_id = %s'
        query = 'select avg(n1.avg) from (select to_char(a."dateTime", \'MM-DD-HH24\') as fechaIndice, avg(a.'+variable+')  '+'from analisis_variables_record as a where a.station_id = %s group by fechaIndice '+'order by fechaIndice asc ) n1 where n1.fechaIndice like \''+mes+'-%%\''

        cursor = connection.cursor()
        cursor.execute(query, [station.pk])
        rows = _fields_to_dict(cursor)

        pprint.pprint(rows)
        resultadosMes.append({'month' : _nombre_mes(int(mes)), 'year' : fecha_desde.year, 'avg' : rows[0]})


        # aumentar la fecha - sumar un mes
        # fecha_desde = _sumar_mes(fecha_desde)
        # fecha_desde = fecha_desde.replace(day=1)
        # obtener el ultimo dia del mes
        # ultimo_dia = calendar.monthrange(fecha_desde.year, fecha_desde.month)[1]
        # fecha_hasta = fecha_desde.replace(day=ultimo_dia, hour=23, minute=59)

    return resultadosMes

def _calculo_por_estacion_anio(fecha_inicio, fecha_fin, variable, station):

    # fechasEstaciones = _fechasParaEstaciones(fecha_inicio, fecha_fin)

    # estaciones = [
    #     {'estacion' : 'verano', 'inicio' : 1221, 'fin' : 1231},
    #     {'estacion' : 'verano', 'inicio' : 101, 'fin' : 320},
    #     {'estacion' : 'otono', 'inicio' : 321, 'fin' : 620},
    #     {'estacion' : 'invierno', 'inicio' : 621, 'fin' : 920},
    #     {'estacion' : 'primavera', 'inicio' : 921, 'fin' : 1220},
    # ]

    # fechas de estaciones en formato MM-DD-HH24
    fechasEstaciones = [
        {'estacion' : 'verano', 'inicio' : '01-01-00', 'fin' : '03-20-24'},
        {'estacion' : 'otono', 'inicio' : '03-21-00', 'fin' : '06-20-24'},
        {'estacion' : 'invierno', 'inicio' : '06-21-00', 'fin' : '09-20-24'},
        {'estacion' : 'primavera', 'inicio' : '09-21-00', 'fin' : '12-20-24'},
        {'estacion' : 'verano', 'inicio' : '12-21-00', 'fin' : '12-31-24'},
    ]

    resultadosMes = []

    for estacion in fechasEstaciones:

        # query = 'select avg(a.'+variable+') from analisis_variables_record as a where a."dateTime" > %s and a."dateTime" < %s and a.station_id = %s'
        query = 'select avg(n1.avg) from (select to_char(a."dateTime", \'MM-DD-HH24\') as fechaIndice, avg(a.'+variable+')  '+'from analisis_variables_record as a where a.station_id = %s group by fechaIndice '+'order by fechaIndice asc ) n1 where n1.fechaIndice >= %s and n1.fechaIndice <= %s'
        
        cursor = connection.cursor()
        cursor.execute(query, [station.pk, estacion['inicio'], estacion['fin']])
        rows = _fields_to_dict(cursor)

        pprint.pprint(rows)

        # resultadosMes.append({'month' : estacion['inicio'].month, 'year' : estacion['inicio'].year, 'avg' : rows[0], 'estacion' : estacion['estacion']})
        resultadosMes.append({'avg' : rows[0], 'estacion' : estacion['estacion']})

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
        {'estacion' : 'verano', 'inicio' : '12-21', 'fin' : '12-31'},
        {'estacion' : 'verano', 'inicio' : '01-01', 'fin' : '03-20'},
        {'estacion' : 'otono', 'inicio' : '03-21', 'fin' : '06-20'},
        {'estacion' : 'invierno', 'inicio' : '06-21', 'fin' : '09-20'},
        {'estacion' : 'primavera', 'inicio' : '09-21', 'fin' : '12-20'},
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

# TODO - solo los que se pueden hacer el math.ceil aceptar si es string retornar el mismo valor nomas
def _redondeo(valorFloat):
	# pprint.pprint(isinstance(valorFloat, (None,)))
	# pprint.pprint(valorFloat)
	# pprint.pprint(isinstance(valorFloat, (None,)))
	if (valorFloat != None):
	    # "{0:.2f}".format(d.outtemp)
	    return math.ceil(valorFloat*100)/100
	else:
		return None
