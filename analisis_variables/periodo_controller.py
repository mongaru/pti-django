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


def _generar_reporte_periodo_estacion(desde, hasta, id_estacion, periodo):
	fecha_desde = desde.strftime("%Y-%m-%d %H:%M:%S")
	fecha_hasta = hasta.strftime("%Y-%m-%d %H:%M:%S")

	# mascara por mes del query
	mascaraPeriodo = 'YYYY-MM-DD-HH24'
	if (periodo == 'dia'):
		mascaraPeriodo = 'YYYY-MM-DD'
	if (periodo == 'mes'):
		mascaraPeriodo = 'YYYY-MM'

	query = 'select to_char(a."dateTime", \''+mascaraPeriodo+'\') as fechaIndice, avg(a.barometer) as "presion", avg(a."outTemp") as "temperatura", avg(a."windDir") as "winddir", avg(a."windSpeed") as "windspeed"  from analisis_variables_record as a where a."dateTime" > %s and a."dateTime" < %s and a.station_id = %s group by fechaIndice order by fechaIndice asc'
	cursor = connection.cursor()
	cursor.execute(query, [fecha_desde, fecha_hasta, id_estacion])
	# rows = _fields_to_dict(cursor)
	columns = [col[0] for col in cursor.description]

	return {'titulos' : columns, 'valores' : cursor.fetchall()}

def reporte_periodo_generacion(request):
    
	formato = request.GET.get('formato', 'tabla')
	periodo = request.GET.get('periodo', 'hora')

	id_estacion = request.GET.get('estacion', '1')

	desde = request.GET.get('desde', datetime.today().strftime("%Y-%m-%d"))
	desde = datetime.strptime(desde, '%Y-%m-%d')
	desde = desde.replace(hour=00, minute=01)

	fechaHastaDefault = datetime.today() - timedelta(days=10)
	hasta = request.GET.get('hasta', fechaHastaDefault.strftime("%Y-%m-%d"))
	hasta = datetime.strptime(hasta, '%Y-%m-%d')
	hasta = hasta.replace(hour=23, minute=59)

	titulos = None
	valores = []

	valoresEstacion = _generar_reporte_periodo_estacion(desde, hasta, id_estacion, periodo)

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

@register.filter
def is_numeric(value):

    return isinstance(value, (decimal.Decimal, int, float))
