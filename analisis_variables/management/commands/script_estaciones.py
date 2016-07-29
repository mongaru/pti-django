from django.core.management.base import BaseCommand, CommandError
# from polls.models import Question as Poll

from analisis_variables.models import Station, Record
# from parser import ParserUno
from _parser_mis import ParserMIS
from _parser_arc import ParserARC
from _parser_tech import ParserTech
# from parser_rainwise import ParserRainwise
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import loader, Context
from datetime import datetime, timedelta, date, time
import pprint


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

    def handle(self, *args, **options):

        pprint.pprint('======= Inicio script de estaciones =======')

        estacion_id = options['estacion_id']

        estaciones = Station.objects.all()

        # arreglo para guardar las estaciones con errores para luego notificar
        estacionesConErrores = []

        for estacion in estaciones:

            registrosConErrores = []

            # si indica una estacion id en el parametro al ejecutar el script entonces solo se cargan los datos de esa estacion
            if (estacion_id != None and estacion.pk != int(estacion_id)):
                continue

            # if (estacion.type.mark == 'Campbell'):
            #     parser = ParserUno(estacion)
            #     # ejecutar el parser y obtener el listado de registros con errores para el reporte
            #     registrosConErrores = parser.runParser()

            # if (estacion.type.mark == 'MIS'):
            #     parser = ParserMIS(estacion)
            #     # ejecutar el parser y obtener el listado de registros con errores para el reporte
            #     registrosConErrores = parser.runParser()

            if (estacion.type.mark == 'ARC'):
                parser = ParserARC(estacion)
                # ejecutar el parser y obtener el listado de registros con errores para el reporte
                registrosConErrores = parser.runParser()

            if (estacion.type.mark == 'Tech'):
                parser = ParserTech(estacion)
                # ejecutar el parser y obtener el listado de registros con errores para el reporte
                registrosConErrores = parser.runParser()

            # if (estacion.type.mark == 'Rainwise'):
            #     parser = ParserRainwise(estacion)
            #     # ejecutar el parser y obtener el listado de registros con errores para el reporte
            #     registrosConErrores = parser.runParser()

            # if (estacion.pk == 16):
            #     parser = ParserMIS(estacion)
            #     # ejecutar el parser y obtener el listado de registros con errores para el reporte
            #     registrosConErrores = parser.runParser()

            # en caso de haber registros con errores se agrega la estacion
            if (len(registrosConErrores) > 0):
                estacionesConErrores.append({'estacion' : estacion.name, 'cantidad' : len(registrosConErrores)})

        # notificar al adminitrador
        if (len(estacionesConErrores) > 0):

            # template = loader.get_template('email-estacion-reporte-diario-errores.html')
            # fecha = datetime.today().strftime("%d/%m/%Y")

            # c = Context({ 'fecha': fecha, 'estaciones' : estacionesConErrores})
            # rendered = template.render(c)

            # subject = 'Agroclima, registros con errores'
            # from_email = 'teddy@amediacreative.com'
            # to = settings.AGROCLIMA_ADMIN_EMAIL
            # text_content = 'Agroclima, registros con errores.'

            # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            # msg.attach_alternative(rendered, "text/html")
            # msg.send()
            self.stdout.write(self.style.SUCCESS('- Cantidad de estaciones con errores %i' % len(estacionesConErrores)))

        self.stdout.write(self.style.SUCCESS('====== Fin Script Estaciones "%s"' % '======'))

        