# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from analisis_variables.models import Station, Record, TypeStation
from _parser_mis import ParserMIS
from _parser_arc import ParserARC
from _parser_tech import ParserTech
from _parser_sutron_csv import ParserSutronCSV
from _parser_dinac import ParserDinac
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import loader, Context
from datetime import datetime, timedelta, date, time
import pprint

import urllib, json

class Command(BaseCommand):
    # help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        # python manage.py script_estaciones --estacion=1

        # parametro requerido 
        # parser.add_argument('estacion_id', nargs='+', type=int)

        # Named (optional) arguments
        parser.add_argument(
            '--estacion',
            # action='store_true', # no activar esta opcion para que sea opcional o ver a que se refiere
            dest='estacion_id',
            default=None,
            help='Indique la estacion que desea cargar',
        )

    def _get_departamento(self, texto):

        for dpto in Station.DEPTOS:
            if (dpto[1] == texto):
                return dpto[0]

        return 1

    def _get_fabricante(self, texto):

        for dpto in Station.FABRICANTES:
            if (dpto[1] == texto):
                return dpto[0]

        return 1

    def handle(self, *args, **options):

        pprint.pprint('======= Inicio script sincronizacion de estaciones DINAC =======')

        # http://emas.demo-staging.com:8098/api/station_data?station_id=1&start_date=2016-01-01&end_date=2016-01-01

        # http://emas.demo-staging.com:8098/api/station
        # http://emas.demo-staging.com:8098/api/station/1
        # http://emas.demo-staging.com:8098/api/hidro_station
        # http://emas.demo-staging.com:8098/api/hidro_station/1

        url = "http://emas.demo-staging.com:8098/api/station"
        
        try:
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            
            estacionesDinac = data['data']

            tipoEstacionDinac = TypeStation.objects.get(mark='DINAC_API')

            for estacionRemota in estacionesDinac:

                # solo las estaciones de tipo meteorologico se deben sincronizar
                if (estacionRemota['tipo'] != 'meteorologico'):
                    continue

                try:
                    estacion = Station.objects.get(dinac_id=estacionRemota['id'])
                except Station.DoesNotExist:
                    estacion = None

                # creamos nuevo si ya no existe, en caso de que si exista entonces se actualizan los datos en caso de que cambien en DINAC
                if (estacion == None):
                    estacion = Station()

                # {
                #   "id": 19,
                #   "nombre": "Aeropuerto de Coronel Oviedo",
                #   "tipo": "meteorologico",
                #   "ubicacion": {
                #     "ciudad": "Coronel Oviedo",
                #     "departamento": "Caaguazú"
                #   },
                #   "elevacion": {
                #     "valor": 150,
                #     "descripcion": "150 mts."
                #   },
                #   "geolocalizacion": {
                #     "latitud": -25.51535877,
                #     "longitud": -56.40837226
                #   },
                #   "tipo_estacion": "OTT",
                #   "ultima_observacion": {
                #     "utc": "2016-08-04T18:40:00+0000",
                #     "local": "2016-08-04T14:40:00-0400"
                #   },
                #   "url": {
                #     "web": "http://emas.demo-staging.com:8098/station/19",
                #     "api": "http://emas.demo-staging.com:8098/api/station/19"
                #   }
                # }

                # FABRICANTES = ((1, 'Davis'), (2, 'Sutron'), (3, 'OTT'),)
                # PROPIETARIOS = ((1, 'DINAC'), (2, 'PTI'), (3, 'FECOPROD'),)
                

                estacion.name = estacionRemota['nombre']
                estacion.fabricante = self._get_fabricante(estacionRemota['tipo_estacion'])
                estacion.elevation = estacionRemota['elevacion']['valor']
                estacion.lat = estacionRemota['geolocalizacion']['latitud']
                estacion.lg = estacionRemota['geolocalizacion']['longitud']
                estacion.type = tipoEstacionDinac
                estacion.departamento = self._get_departamento(estacionRemota['ubicacion']['departamento'])
                estacion.obs = '-'
                estacion.dinac_id = estacionRemota['id']
                estacion.date_installation = datetime.today().strftime("%Y-%m-%d")

                pprint.pprint(estacion.name + " - guardada")
                
                estacion.save()
            
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        except ValueError as e:
            print('JSON Decode error.')
            print('Reason: ', e.reason)


        pprint.pprint('======= Fin script sincronizacion de estaciones DINAC =======')

        