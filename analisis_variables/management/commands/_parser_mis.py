from analisis_variables.models import Station, Record, Control
from django.conf import settings
from datetime import datetime, timedelta, date, time
from pytz import timezone
from os import listdir
from os.path import isfile, join
import csv
import pprint
import os.path
import re

class ParserMIS():

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

        lastUpdatedFile = self._get_last_update_file()

        archivos = [a for a in archivos if self._filtrar_por_archivo(lastUpdatedFile, a)]

        # por cada archivo hay que analizar si los datos ya estan cargados de acuerdo al nombre del archivo
        for archivo in archivos:
            if ".MIS" in archivo:

                mis_file = mis_filepathname + '/' + archivo

                # obtener el ultimo registro de la bd que es el dato mas actualizado de modo a insertar solo los nuevos
                try:
                    ultimoRegistro = Record.objects.filter(station=self.station).latest('datetime')
                except Record.DoesNotExist:
                    ultimoRegistro = None

                registrosConErrores = self.procesarArchivo(registrosConErrores, mis_file, archivo, ultimoRegistro, mis_filepathname)


        return registrosConErrores

    def procesarArchivo(self, registrosConErrores, mis_filepathname, misFileName, ultimoRegistro, fileFolderPath):

        # verificar que archivo existe, en realidad se deberia enviar un error o hacer un log.
        if (os.path.isfile(mis_filepathname) == False):
            return registrosConErrores

        pprint.pprint('lee archivo' + mis_filepathname)

        lastUpdatedFile = self._get_last_update_file()

        # en caso de que el nombre del archivo sea menor al ultimo leido entonces no procesar dicho archivo
        if (lastUpdatedFile != None and lastUpdatedFile >= misFileName):
            return registrosConErrores

        controlesDict = self.getControles()
        estacion = self.station

        lines = [line.rstrip('\n') for line in open(mis_filepathname)]
        lines = [line.rstrip('\r') for line in lines]

        registros = []
        columnaContador = 0
        registrosContador = 0

        # <STATION>000000H001</STATION><SENSOR>0010</SENSOR><DATEFORMAT>YYYYMMDD</DATEFORMAT>
        # 20160428;190000;0.98
        # 20160428;191000;0.98
        # 20160428;192000;0.98
        # <STATION>000000H001</STATION><SENSOR>0032</SENSOR><DATEFORMAT>YYYYMMDD</DATEFORMAT>
        # 20160428;190000;13.0
        # 20160428;191000;14.0
        # 20160428;192000;14.2


        # sensor [datos]

        # 20160428;192000 => [{sensor, valor}, {sensor, valor}, {sensor, valor}, {sensor, valor}

        leerDato = False # variable que indica si ya se leyo una cabecera de sensor y se esperan datos
        sensorActual = None
        registrosConSensores = {}

        for line in lines:

            # En caso de que se empiece con la cabecera del sensor, se guarda una referencia y se continua a los datos o siguiente sensor
            if (line.startswith('<STATION>')):
                # leerDato = True
                sensorActual = line
                continue;

            else: # leer datos

                datoSensor = line.split(';')

                fechaTexto = datoSensor[0] + datoSensor[1].replace(":", "")

                fechaRegistro = self.getDatetimeValue(fechaTexto)

                # verificar que la fecha del registro sea mayor a la del ultimo registro en la bd antes de insertar
                if (fechaRegistro != None and ultimoRegistro != None and fechaRegistro <= ultimoRegistro.datetime):
                    continue

                if (fechaTexto not in registrosConSensores):
                    registrosConSensores[fechaTexto] = []

                sensorCodigo = re.sub(r".*\<SENSOR\>", "", sensorActual)
                sensorCodigo = re.sub(r"\<\/SENSOR\>.*", "", sensorCodigo)

                registrosConSensores[fechaTexto].append({'sensor' : sensorCodigo, 'valor' : datoSensor[2]})


        registrosGuardar = []
        for claveFecha in registrosConSensores:

            registro = self.procesarRegistro(claveFecha, registrosConSensores[claveFecha])

            registro.usunits = 1
            registro.interval = 1
            registro.station = estacion
            # registro.station_name = estacion.name

            # si el dato no tuvo problemas en el parser (procesarRegistro) de valores entonces si validar
            if (registro.consistente == None):
                if (self.getRegistroEsConsistente(registro, controlesDict)):
                    registro.consistente = 'si'
                else:
                    registro.consistente = 'no'

            if (registro.datetime == None):
                registro.datetime = datetime.now()
                registro.consistente = 'no'

            # pprint.pprint(registro.barometer)
            # pprint.pprint(isinstance(registro.barometer, float))
            
            # registro.save()
            registrosGuardar.append(registro)

            if (registro.consistente == 'no'):
                registrosConErrores.append(registro)

        # se guarda todo en un solo insert, para performance
        if (len(registrosGuardar) > 0):
            Record.objects.bulk_create(registrosGuardar)

        # se actualiza el ultimo archivo cargado
        self._write_last_update_file(misFileName)

        return registrosConErrores

    def procesarRegistro(self, fechaTexto, datos):

        fechaRegistro = self.getDatetimeValue(fechaTexto)

        registro = Record()
        registro.datetime = fechaRegistro

        for dato in datos:

            valor = dato['valor']

            # pprint.pprint(valor)

            try:
                valor = float(valor)
            except ValueError:
                valor = None
                registro.consistente = 'no'

            sensor = dato['sensor']

            # pprint.pprint(sensor)
            # pprint.pprint(valor)


            if (sensor == '0001'):
                registro.windspeed = valor
            elif (sensor == '0002'):
                registro.winddir = valor
            elif (sensor == '0003'):
                registro.rain = valor
            elif (sensor == '0004'):
                registro.outhumidity = valor
            elif (sensor == '0007'):
                registro.soiltemp1 = valor
            elif (sensor == '0008'):
                registro.outtemp = valor
            elif (sensor == '0010'): #sensor que lee los datos de presion en QNF
                registro.barometer = valor
            elif (sensor == '0011'):
                registro.soiltemp2 = valor
            elif (sensor == '0013'):
                registro.radiation = valor
            elif (sensor == '0016'):
                registro.leafweat1 = valor
            elif (sensor == '0017'):
                registro.dewpoint = valor
            elif (sensor == '0019'):
                registro.pressure = valor

        return registro

    def procesarRegistro2(self, datos):

        columnaContador = 0
        registrosContador = 0
        fechaRegistro = None

        registro = Record()

        # obtener el objeto datetime
        for dato in datos:
            datosFila = dato['datos'].split(';')

            fecha = datosFila[0] + datosFila[1].replace(":", "")

            fechaRegistro = self.getDatetimeValue(fecha)

            break

        registro.datetime = fechaRegistro

        for dato in datos:
            datosFila = dato['datos'].split(';')

            valor = datosFila[2]

            try:
                valor = float(valor)
            except ValueError:
                valor = None
                registro.consistente = 'no'

            sensor = re.sub(r".*\<SENSOR\>", "", dato['cabecera'])
            sensor = re.sub(r"\<\/SENSOR\>.*", "", sensor)

            if (sensor == '0001'):
                registro.windspeed = valor
            elif (sensor == '0002'):
                registro.winddir = valor
            elif (sensor == '0003'):
                registro.rain = valor
            elif (sensor == '0004'):
                registro.outhumidity = valor
            elif (sensor == '0007'):
                registro.soiltemp1 = valor
            elif (sensor == '0008'):
                registro.outtemp = valor
            elif (sensor == '0010'): #sensor que lee los datos de presion en QNF
                registro.barometer = valor
            elif (sensor == '0011'):
                registro.soiltemp2 = valor
            elif (sensor == '0013'):
                registro.radiation = valor
            elif (sensor == '0016'):
                registro.leafweat1 = valor
            elif (sensor == '0017'):
                registro.dewpoint = valor
            elif (sensor == '0019'):
                registro.pressure = valor

        return registro

    def getDatetimeValue(self, fecha):

        try:
            # d = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
            d = datetime.strptime(fecha, "%Y%m%d%H%M%S")

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
                    # pprint.pprint('falla none')
                    return False

                # en el caso de que el valor que esta cargado sea None y no se valida 'None' entonces retornar True para que no marque
                # como inconsistente con los otros controles
                if (registro.__dict__[campoNombre] == None):
                    return True

                if (controlNombre == 'MINIMO' and self.validateMinimoControl(registro.__dict__[campoNombre], self.parseFloat(validadores.valor)) == False):
                    # pprint.pprint('falla minimo: ' + validadores.valor + " ++ " + controlNombre)
                    return False

                if (controlNombre == 'MAXIMO' and self.validateMaximoControl(registro.__dict__[campoNombre], self.parseFloat(validadores.valor)) == False):
                    #pprint.pprint('falla maximo: ' + validadores.valor + " ++ " + controlNombre + " ++ " + registro.__dict__[campoNombre])
                    #pprint.pprint('falla maximo')
                    return False


        return True

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

    def parseFloat(self, valor):

        if (valor == None):
            return None

        try:
            retorno = float(valor)
        except ValueError:
            retorno = None

        return retorno

    def _getVariableNombre(self, indice):

        for ctrl in Control.VARIABLES:
            if (str(ctrl[0]) == str(indice)):
                return ctrl[1]


    def _getControlNombre(self, indice):

        for ctrl in Control.CONTROL:
            if (str(ctrl[0]) == str(indice)):
                return ctrl[1]

    def _filtrar_por_archivo(self, ultimoArchivo, archivoActual):
        
        if ultimoArchivo == None:
            return True

        if (ultimoArchivo >= archivoActual):
            return False

        return True

    def _write_last_update_file(self, content):
        f2 = open(self.station.pk+'-last-update-file.txt', 'w')
        f2.write(content)
        f2.close()

    def _get_last_update_file(self):
        if (isfile(self.station.pk+"-last-update-file.txt")):
            lines = [line.rstrip('\n') for line in open(self.station.pk+"-last-update-file.txt")]

            for line in lines:
                return line
        else:
            return None