from django.core.management.base import BaseCommand, CommandError
# from polls.models import Question as Poll

from analisis_variables.models import Station, Record
# from parser import ParserUno
from _parser_mis import ParserMIS
from _parser_arc import ParserARC
# from parser_rainwise import ParserRainwise
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import loader, Context
from datetime import datetime, timedelta, date, time

import pprint

from pyexcel_xlsx import get_data
import json

import pyexcel as pe

class Command(BaseCommand):
    # help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
        # python manage.py script_estaciones --estacion=1

        # parametro requerido 
        # parser.add_argument('estacion_id', nargs='+', type=int)

        # Named (optional) arguments
        # parser.add_argument(
        #     '--estacion',
        #     # action='store_true', # no activar esta opcion para que sea opcional o ver a que se refiere
        #     dest='estacion_id',
        #     default=None,
        #     help='Indique la estacion que desea cargar',
        # )

    def handle(self, *args, **options):
    	# ambas librerias usan
    	# https://openpyxl.readthedocs.io/en/default/tutorial.html#loading-from-a-file

        pprint.pprint('======= Inicio script de testeo =======')

        # https://github.com/pyexcel/pyexcel-xls
        # data = get_data("datosarc/catastro-test.xls")

        # pprint.pprint(data['Hoja1'])

        # for fila in data['Hoja2']:
        # 	pprint.pprint("================")
        # 	pprint.pprint(fila)


        # http://pyexcel.readthedocs.io/en/latest/tutorial_file.html
        sheet = pe.get_sheet(file_name="datosarc/catastro-test.xls")

        for row in sheet.row:
        	pprint.pprint(row)







