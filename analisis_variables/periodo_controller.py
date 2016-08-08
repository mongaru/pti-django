import json
import pprint
import calendar
import math
import csv
import numbers
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
from django.template.defaulttags import register

from analisis_variables.models import Station, Record
from django.db.models import Q
from django.db import connection

def reporte_periodo(request):

    estaciones = Station.objects.all()
    
    dataToRender = {
        'estaciones' : estaciones
    }

    return render_to_response('reporte_por_periodo.html', dataToRender)

def reporte_periodo_generacion(request):
    
	formato = request.GET.get('formato', 'tabla')
	periodo = request.GET.get('periodo', 'hora')
	conjuntoDatos = request.GET.get('conjunto', 'porFecha')

	id_estacion = request.GET.get('estacion', '1')

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

	if (conjuntoDatos == 'porFecha'):
		valoresEstacion = _generar_reporte_periodo_estacion(desde, hasta, id_estacion, periodo)

	if (conjuntoDatos == 'porAnioTipo'):
		valoresEstacion = _generar_reporte_anio_tipo(desde, hasta, id_estacion, periodo)

	dataToRender = {
		'titulos' : valoresEstacion['titulos'],
		'datosExportar' : valoresEstacion['valores']
	}

	if (formato == 'tabla'):
		return render_to_response('reporte_por_periodo_tabla.html', dataToRender)
	
	if (formato == 'csv'):
		# Create the HttpResponse object with the appropriate CSV header.
	    response = HttpResponse(content_type='text/csv')
	    response['Content-Disposition'] = 'attachment; filename="reporte_anual.csv"'

	    writer = csv.writer(response)

	    writer.writerow(valoresEstacion['titulos'])
	    
	    for fila in valoresEstacion['valores']:
	    	writer.writerow(fila)

	    return response

	if (formato == 'grafico'):
	    result = []

	    for i in range(0, len(valoresEstacion['valores'])):
	    	fila = {}
	    	for w in range(0, len(valoresEstacion['valores'][i])):
	    		if (w == 0):
	    			fila['fecha'] = valoresEstacion['valores'][i][w]
	    		else:
	    			fila[valoresEstacion['titulos'][w]] = _redondeo(valoresEstacion['valores'][i][w])

	    	result.append(fila)

	    response_data = {}
	    response_data['status'] = 'ok'
	    response_data['data'] = result

	    return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")

	# generar este tipo de graficos solo para datos que no son del anio tipo
	if (formato == 'graficoPorAnio' and conjuntoDatos != 'porAnioTipo'):
	    datosExportar = _generar_reporte_por_anio(valoresEstacion)
	    result = datosExportar

	    response_data = {}
	    response_data['status'] = 'ok'
	    response_data['data'] = result

	    return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")
	        

def _generar_reporte_por_anio(valoresEstacion):
	# formato de salida
	# este era el anterior que no funciono {"2014" : {"01" : {"fecha" : "sss", "temperatura"}, "02" : {"fecha" : "sss", "temperatura"} } }
	# {'columnas' : ['01', '02', '03'], 'valores' : {'2015' : [10, 11, 12], '2016' : [10, 11, 12]}

	columnas = {}
	contador = 0
	columnasNombre = []

	# primero se recorren los datos para poder generar los titulos de columnas, debido a que las fechas tienen que ser en orden
	# para que se carguen de la misma manera en que vienen de la base de datos. En caso de que sean los mismos dias, estos se van 
	# a separar luego por anio pero estaran en la misma posicion por lo que se van a poder comparar
	for i in range(0, len(valoresEstacion['valores'])):
		fila = {}
		posicionValor = valoresEstacion['valores'][i][0]
		posicionValor = posicionValor[5:len(posicionValor)]

		if (posicionValor not in columnas):
			columnas[posicionValor] = contador # obtenemos la clave de la fecha y colocamos el contador para saber su posicion en el arreglo
			columnasNombre.append(posicionValor) # cargamos el arreglo de titulos de columnas para el grafico
			contador = contador + 1
		
		#columnas[posicionValor] = i # obtenemos la clave de la fecha y colocamos el contador para saber su posicion en el arreglo
		# columnasNombre.append(posicionValor) # cargamos el arreglo de titulos de columnas para el grafico

	result = {};

	columnasLista = []

	# se genera un listado de las columnas de datos que se van a necesitar con datos vacios. Luego utilizando la clave de la fecha
	# se obtiene la posicion en donde se debe cargar los datos.
	for i in range(0, len(columnas)):
		columnasLista.append({})

	# pprint.pprint(columnas)

	# se recorren los datos para cargarlos en los anhos que corresponden y en la posicion del arreglo de acuerdo a la columna que corresponden
	for i in range(0, len(valoresEstacion['valores'])):
		fila = {}

		# se obtiene el anho a donde cargar el dato
		fechaAnio = valoresEstacion['valores'][i][0][:4]
		# se obtiene la clave de la fecha sin el anio para poder obtener la hora, el dia o mes
		posicionValor = valoresEstacion['valores'][i][0]
		posicionValor = posicionValor[5:len(posicionValor)]


    		for w in range(0, len(valoresEstacion['valores'][i])):
    			if (w == 0):
    				fila['fecha'] = valoresEstacion['valores'][i][w]
    			else:
    				fila[valoresEstacion['titulos'][w]] = _redondeo(valoresEstacion['valores'][i][w])

    		# en caso de no tener un listado del anho se crea uno
    		if (fechaAnio not in result):

    			result[fechaAnio] = list(columnasLista)

    	# se agrega la fila de datos en el anho y en la posicion del listado de datos de acuerdo a la posicion de la columna
		result[fechaAnio][columnas[posicionValor]] = fila

	return {'columnas' : columnasNombre, 'valores' : result}
	

def _generar_reporte_periodo_estacion(desde, hasta, id_estacion, periodo):
	fecha_desde = desde.strftime("%Y-%m-%d %H:%M:%S")
	fecha_hasta = hasta.strftime("%Y-%m-%d %H:%M:%S")

	# mascara por mes del query
	mascaraPeriodo = 'YYYY-MM-DD-HH24'
	if (periodo == 'dia'):
		mascaraPeriodo = 'YYYY-MM-DD'
	if (periodo == 'mes'):
		mascaraPeriodo = 'YYYY-MM'

	query = 'select to_char(a."dateTime", \''+mascaraPeriodo+'\') as fechaIndice, avg(a.barometer) as "presion", avg(a."outTemp") as "temperatura", avg(a."windDir") as "winddir", avg(a."windSpeed") as "windspeed", avg(a."radiation") as "radiation", avg(a."windSpeed50") as "windspeed50", avg(a."windDir50") as "winddir50"  from analisis_variables_record as a where a."dateTime" > %s and a."dateTime" < %s and a.station_id = %s group by fechaIndice order by fechaIndice asc'
	cursor = connection.cursor()
	cursor.execute(query, [fecha_desde, fecha_hasta, id_estacion])
	# rows = _fields_to_dict(cursor)
	columns = [col[0] for col in cursor.description]

	return {'titulos' : columns, 'valores' : cursor.fetchall()}

def _generar_reporte_anio_tipo(desde, hasta, id_estacion, periodo):
	# fecha_desde = desde.strftime("%Y-%m-%d %H:%M:%S")
	# fecha_hasta = hasta.strftime("%Y-%m-%d %H:%M:%S")

	# mascara por mes del query
	mascaraPeriodo = 'MM-DD-HH24'
	if (periodo == 'dia'):
		mascaraPeriodo = 'MM-DD'
	if (periodo == 'mes'):
		mascaraPeriodo = 'MM'

	query = 'select to_char(a."dateTime", \''+mascaraPeriodo+'\') as fechaIndice, avg(a.barometer) as "presion", avg(a."outTemp") as "temperatura", avg(a."windDir") as "winddir", avg(a."windSpeed") as "windspeed", avg(a."radiation") as "radiation", avg(a."windSpeed50") as "windspeed50", avg(a."windDir50") as "winddir50"  from analisis_variables_record as a where a.station_id = %s group by fechaIndice order by fechaIndice asc'
	cursor = connection.cursor()
	cursor.execute(query, [id_estacion])
	# rows = _fields_to_dict(cursor)
	columns = [col[0] for col in cursor.description]

	return {'titulos' : columns, 'valores' : cursor.fetchall()}


def _redondeo(valorFloat):
	if (valorFloat != None):
	    # "{0:.2f}".format(d.outtemp)
	    return math.ceil(valorFloat*100)/100
	else:
		return None

@register.filter
def is_numeric(value):
	return isinstance(value, (decimal.Decimal, float))
