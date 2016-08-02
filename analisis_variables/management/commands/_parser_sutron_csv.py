from analisis_variables.models import Station, Record, Control
from django.conf import settings
from datetime import datetime, timedelta, date, time
from os import listdir
from os.path import isfile, join
import csv
import pprint
import os.path
import re
from datetime import datetime, timedelta, date, time
from pytz import timezone

class ParserSutronCSV():

    def __init__(self, station):
        self.station = station

    def runParser(self):
        # arreglo para los registros con inconsistencias, se retorna este arreglo
        registrosConErrores = []

        # cargar el archivo mis de acuerdo a la configuracion de la estacion
        mis_filepathname = settings.ESTACION_DATO_CARPETA + self.station.path_db

        pprint.pprint('lee carpeta - ' + mis_filepathname)

        # verificar que archivo existe, en realidad se deberia enviar un error o hacer un log.
        if (os.path.isdir(mis_filepathname) == False):
            return registrosConErrores

        # se leen los archivos en la carpeta indicada
        archivos = [ f for f in listdir(mis_filepathname) if isfile(join(mis_filepathname,f)) ]

        pprint.pprint(archivos)

        # datos.sort(key=lambda x: obtenerFechaDeTexto(x['date_rain']), reverse=False)
        archivos = sorted(archivos)

        # por cada archivo hay que analizar si los datos ya estan cargados de acuerdo al nombre del archivo
        for archivo in archivos:
            if ".csv" in archivo:
                mis_file = mis_filepathname + '/' + archivo

                # obtener el ultimo registro de la bd que es el dato mas actualizado de modo a insertar solo los nuevos
                try:
                    ultimoRegistro = Record.objects.filter(station=self.station).latest('datetime')
                except Record.DoesNotExist:
                    ultimoRegistro = None

                registrosConErrores = self.procesarArchivo(registrosConErrores, mis_file, ultimoRegistro)


        return registrosConErrores

    def procesarArchivo(self, registrosConErrores, mis_filepathname, ultimoRegistro):

        # verificar que archivo existe, en realidad se deberia enviar un error o hacer un log.
        if (os.path.isfile(mis_filepathname) == False):
            return registrosConErrores

        pprint.pprint('lee archivo' + mis_filepathname)

        controlesDict = self.getControles()
        estacion = self.station

        # cargar el archivo csv de acuerdo a la configuracion de la estacion
        # csv_filepathname = settings.ESTACION_DATO_CARPETA + self.station.path_db
        # dataReader = csv.reader(open(mis_filepathname), delimiter='\t', quotechar='"')

        # "TIMESTAMP","RECORD","SlrW_Avg","SlrMJ_Tot","WS_ms_Avg","WindDir","BattV"

        with open(mis_filepathname, "rb") as csvfile:
            datareader = csv.reader(csvfile, delimiter=',', quotechar='"')
            rowCount = 1
            registrosCount = 0
            registrosLista = []

            for row in datareader:

                if (rowCount > 2):

                    registro = Record()

                    # fila 0 - fecha
                    fechaRegistro = self.getDatetimeValue(row[0])

                    # verificar que la fecha del registro sea mayor a la del ultimo registro en la bd antes de insertar
                    if (fechaRegistro != None and ultimoRegistro != None and fechaRegistro <= ultimoRegistro.datetime):
                        continue
                        rowCount = rowCount + 1
                   
                    pprint.pprint(fechaRegistro)

                    registro.datetime = fechaRegistro
                    registro.usunits = 1
                    registro.interval = 1
                    registro.station = self.station

                    # 0001 - intensidad del Viento
                    registro.windspeed = self.parseFloat(row[1])
                    # 0002 - Direccion del Viento
                    registro.winddir = self.parseFloat(row[2])
                    # 0003 - Precipitacion
                    registro.rain = self.parseFloat(row[3])
                    # 0004 - Humedad Relativa
                    registro.outhumidity = self.parseFloat(row[4])
                    # 0005 - intensidad del viento maxima
                    registro.winddir = self.parseFloat(row[5])
                    # 0006 - direccion viento maxima
                    registro.winddir = self.parseFloat(row[6])
                    # 0007 - temperatura del suelo
                    registro.soiltemp1 = self.parseFloat(row[7])
                    # 0008 - temperatura del aire
                    registro.outtemp = self.parseFloat(row[8])
                    # 0009 - Temp. Min del Aire
                    # 0010 - presion atmosferica
                    registro.pressure = self.parseFloat(row[10])
                    # 0011 - temp suelo virtual
                    # 0012 - temp maxima del aire del dia
                    # 0013 - radiacion global
                    registro.radiation = self.parseFloat(row[13])
                    # 0014 - radiacion indirecta
                    # 0015 - intensidad del viento knot
                    # 0016 - Presion de Vapor (calculo)
                    # 0017 - Punto de Rocio
                    registro.dewpoint = self.parseFloat(row[17])
                    # 0018 - Intensidad de Viento en Km/h
                    # 0019 - Presion Atmosfer.  a nivel de mar ( QNH)
                    # 0020 - Reservado
                    # 0021 - Reservado
                    # 0022 - Reservado
                    # 0023 - Reservado
                    # 0024 - Reservado
                    # 0025 - Reservado
                    # 0026 - Reservado
                    # 0027 - Horas de Sol
                    # 0028 - Intensidad Media del Viento
                    # 0029 - Direccion Media del Viento
                    # 0030 - Reservado
                    # 0031 - Precipitacion acumulada 24 hs.
                    # 0032 - Alimentacion

                    registrosLista.append(registro)
                    registrosCount = registrosCount + 1

                    if (len(registrosLista) > 10):
                        Record.objects.bulk_create(registrosLista)
                        registrosLista = []
                        registrosCount = 0

                rowCount = rowCount + 1

            if (len(registrosLista) > 0):
                Record.objects.bulk_create(registrosLista)

        return registrosConErrores

    def getValor(self, row, indice, columnas):

        if (indice in columnas):
            if (row[columnas[indice]] == "NULL"):
                return None

            return row[columnas[indice]]

        return None

    def parseFloat(self, valor):

        if (valor == None):
            return None

        try:
            retorno = float(valor)
        except ValueError:
            retorno = None

        return retorno

    def getDatetimeValue(self, fecha):

        try:
            # d = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
            d = datetime.strptime(fecha, "%Y-%m-%d %H:%M")

            # indicar el timezone de la hora parseada para que se pueda comparar
            asuncion = timezone('America/Asuncion')
            utc = timezone('UTC')

            d = d.replace(tzinfo=utc)
            return d
        except ValueError:
            return None

    def getRegistroEsConsistente(self, registro, controlesDict):

        if (registro.datetime == None):
            return False

        for campoNombre in controlesDict:

            controles = controlesDict[campoNombre]

            for validadores in controles:
                controlNombre = self._getControlNombre(validadores.control_var)

                if (controlNombre == 'NONE' and self.validateNoneControl(registro.__dict__[campoNombre]) == False):
                    #pprint.pprint('falla none')
                    #pprint.pprint('falla none: ' + validadores.valor + " ++ " + controlNombre + " ++ " + registro.__dict__[campoNombre])
                    return False

                # en el caso de que el valor que esta cargado sea None y no se valida 'None' entonces retornar True para que no marque
                # como inconsistente con los otros controles
                if (registro.__dict__[campoNombre] == None):
                    return True

                if (controlNombre == 'MINIMO' and self.validateMinimoControl(registro.__dict__[campoNombre], self.parseFloat(validadores.valor)) == False):
                    # pprint.pprint(format(validadores.valor, 'f'))
                    # pprint.pprint('falla minimo: ' + validadores.valor + " ++ " + controlNombre + " ++ " + str(registro.__dict__[campoNombre]))
                    return False

                if (controlNombre == 'MAXIMO' and self.validateMaximoControl(registro.__dict__[campoNombre], self.parseFloat(validadores.valor)) == False):
                    # pprint.pprint('falla maximo: ' + validadores.valor + " ++ " + controlNombre + " ++ " + str(registro.__dict__[campoNombre]))
                    #pprint.pprint('falla maximo')
                    return False


        return True

        # campoControles = controlesDict[campo]

        # for metodoControl in campoControles:


        # listadoCampos = ['pressure', 'outtemp','outhumidity', 'windspeed', 'winddir', 'rain',
        #                  'dewpoint', 'windchill', 'radiation','radiation_total', 'txbatterystatus', 'intempbatterystatus']

        # for campo in listadoCampos:
        #     valor = registro.__dict__[campo]

        #     if (valor == None):
        #         return False

        # listadoCamposNumeros = ['pressure',  'outtemp', 'outhumidity','windspeed', 'winddir',
        #                         'rain', 'dewpoint', 'windchill', 'radiation', 'radiation_total',
        #                         'txbatterystatus', 'intempbatterystatus']

        # for campo in listadoCamposNumeros:
        #     valor = registro.__dict__[campo]

        #     if (valor < -20 or valor > 500):
        #         return False

        # return True

    def getControles(self):

        controles = Control.objects.all()
        controlesDict = {}

        for control in controles:
            varNombre = self._getVariableNombre(control.variable)
            controlNombre = self._getControlNombre(control.control_var)

            if (varNombre in controlesDict):
                controlesDict[varNombre].append(control)
            else:
                controlesDict[varNombre] = [control]


        return controlesDict

    # def esValidoRegistro(self, registro):

    #     controles = Control.objects.all()
    #     controlesDict = {}

    #     for controles in control:
    #         varNombre = self._getVariableNombre(control.variable)
    #         controlNombre = self._getControlNombre(control.control_var)

    #         if (varNombre in controlesDict):
    #             controlesDict[varNombre].append(control)
    #         else
    #             controlesDict[varNombre] = [control]




    def validateNoneControl(self, valor):
        if (valor == None):
            return False

        return True

    def validateMaximoControl(self, valor, maximo):
        if (valor > maximo):
            return False

        return True

    def validateMinimoControl(self, valor, minimo):
        # pprint.pprint('falla minimo: ' + minimo)
        if (valor < minimo):
            return False

        return True

    def _getVariableNombre(self, indice):

        for ctrl in Control.VARIABLES:
            if (str(ctrl[0]) == str(indice)):
                return ctrl[1]


    def _getControlNombre(self, indice):

        for ctrl in Control.CONTROL:
            if (str(ctrl[0]) == str(indice)):
                return ctrl[1]
