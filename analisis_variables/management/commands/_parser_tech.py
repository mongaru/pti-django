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

class ParserTech():

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
            if ".dat" in archivo:
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

                if (rowCount == 2):
                    columnas = []
                    for columnName in row:
                        columnas.append(columnName)

                if (rowCount > 4):

                    registro = Record()

                    # pprint.pprint(row[0])
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

                    for i in xrange(2,len(columnas)):
                        nombreColumna = columnas[i]

                        if (nombreColumna == "SlrW_Avg"):
                            registro.heatindex = row[i]

                        if (nombreColumna == "WS_ms_Avg"):
                            registro.windspeed = row[i]

                        if (nombreColumna == "WindDir"):
                            registro.winddir = row[i]

                        if (nombreColumna == "SlrMJ_Tot"):
                            registro.radiation = row[i]

                        if (nombreColumna == "BattV"):
                            registro.supplyvoltage = row[i]

                        if (nombreColumna == "BP_mbar_Avg"):
                            registro.pressure = row[i]

                        if (nombreColumna == "AirTC_Avg"):
                            registro.outtemp = row[i]

                        if (nombreColumna == "RH"):
                            registro.outhumidity = row[i]

                        if (nombreColumna == "Rain_mm_Tot"):
                            registro.rain = row[i]

                        if (nombreColumna == "PTemp_C_Avg"):
                            registro.intempbatterystatus = row[i]

                        if (nombreColumna == "BattV_Avg"):
                            registro.referencevoltage = row[i]

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
            d = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")

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
