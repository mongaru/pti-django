# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from daterange_filter.filter import DateRangeFilter
from django.db.models import Min, Sum, OneToOneField
from django.http import HttpResponse
# from stations.action import export_to_csv
import math

class TypeStation(models.Model):
    type = models.CharField(max_length=255)
    mark = models.CharField(max_length=255)

    def __unicode__(self):
        return self.type

class TypeStationAdmin(admin.ModelAdmin):
    list_display = ('id', 'type','mark')
    list_filter = ('type', 'mark')

class Station(models.Model):
    
    DEPTOS = ((1, 'Concepcion'), (2, 'San Pedro'), (3, 'Coridillera'), (4, 'Guaira'), (5, 'Caaguazu'), (6, 'Caazapa'),
              (7, 'Itapua'),
              (8, 'Misiones'), (9, 'Paraguari'), (10, 'Alto Parana'), (11, 'Central'), (12, 'Neembucu'),
              (13, 'Amambay'), (14, 'Canindeyu'), (15, 'Presidente Hayes'), (16, 'Alto Paraguay'), (17, 'Boqueron'),)
    
    name = models.CharField(max_length=255)
    path_db = models.CharField(max_length=255)
    date_installation = models.DateField(db_column='date')  # Field name made lowercase.
    time_installation = models.TimeField(db_column='hora', null=True)  # Field name made lowercase.
    #departamento = models.IntegerField(unique=True, choices=DEPTOS, default=0)
    departamento = models.IntegerField(choices=DEPTOS, default=0)
    lat = models.FloatField()
    lg = models.FloatField()
    elevation = models.FloatField()
    type = models.ForeignKey(TypeStation)
    obs = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.name

    def decdeg2dms(dd):
        is_positive = dd >= 0
        dd = abs(dd)
        minutes,seconds = divmod(dd*3600,60)
        degrees,minutes = divmod(minutes,60)
        degrees = degrees if is_positive else -degrees
        return (degrees,minutes,seconds)

    def latitudText(self):
        is_positive = self.lat >= 0
        dd = abs(self.lat)
        minutes,seconds = divmod(dd*3600,60)
        degrees,minutes = divmod(minutes,60)
        degrees = degrees if is_positive else -degrees
        return '%.0f' % math.ceil(degrees) + "º " + '%.0f' % math.ceil(minutes) + "’ " + '%.0f' % math.ceil(seconds) + "’’ "

    def longitudText(self):
        is_positive = self.lg >= 0
        dd = abs(self.lat)
        minutes,seconds = divmod(dd*3600,60)
        degrees,minutes = divmod(minutes,60)
        degrees = degrees if is_positive else -degrees
        return '%.0f' % math.ceil(degrees) + "º " + '%.0f' % math.ceil(minutes) + "’ " + '%.0f' % math.ceil(seconds) + "’’ "




class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'departamento', 'path_db', 'lat', 'lg')
    list_filter = ('departamento', 'path_db')


class Record(models.Model):

	station = models.ForeignKey(Station)
	datetime = models.DateTimeField(db_column='dateTime')  # Field name made lowercase.
	usunits = models.IntegerField(db_column='usUnits')  # Field name made lowercase.
	interval = models.IntegerField()
	barometer = models.DecimalField(blank=True, max_digits=6, decimal_places=1,null=True)
	pressure = models.DecimalField(blank=True, max_digits=6, decimal_places=1,null=True)
	altimeter = models.DecimalField(blank=True, max_digits=6, decimal_places=1, null=True)
	intemp = models.DecimalField(db_column='inTemp',max_digits=3, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
	outtemp = models.DecimalField(db_column='outTemp',max_digits=3, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
	inhumidity = models.DecimalField(db_column='inHumidity', max_digits=4, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
	outhumidity = models.DecimalField(db_column='outHumidity', max_digits=4, decimal_places=1,blank=True, null=True)  # Field name made lowercase.
	windspeed = models.DecimalField(db_column='windSpeed',max_digits=5, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
	winddir = models.DecimalField(db_column='windDir', max_digits=4, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
	windgust = models.DecimalField(db_column='windGust',max_digits=4, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
	windgustdir = models.DecimalField(db_column='windGustDir',max_digits=5, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
	rainrate = models.DecimalField(db_column='rainRate',max_digits=6, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
	rain = models.DecimalField(blank=True, max_digits=6, decimal_places=1, null=True)
	dewpoint = models.DecimalField(blank=True, max_digits=6, decimal_places=1,null=True)
	windchill = models.DecimalField(blank=True, max_digits=6, decimal_places=1,null=True)
	heatindex = models.DecimalField(blank=True, max_digits=6, decimal_places=1,null=True)
	et = models.DecimalField(db_column='ET', max_digits=6, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
	radiation = models.DecimalField(blank=True, max_digits=6, decimal_places=1, null=True)
	radiation_total = models.DecimalField(db_column='radiation_total',max_digits=6, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
	uv = models.DecimalField(db_column='UV', max_digits=6, decimal_places=1,blank=True, null=True)  # Field name made lowercase.
	extratemp1 = models.DecimalField(default=0, db_column='extraTemp1', max_digits=3, decimal_places=1,blank=True, null=True)  # Field name made lowercase.
	extratemp2 = models.DecimalField(default=0, db_column='extraTemp2', max_digits=3, decimal_places=1,blank=True, null=True)  # Field name made lowercase.
	extratemp3 = models.FloatField(default=0, db_column='extraTemp3', blank=True, null=True)  # Field name made lowercase.
	soiltemp1 = models.FloatField(default=0, db_column='soilTemp1', blank=True, null=True)  # Field name made lowercase.
	soiltemp2 = models.FloatField(default=0, db_column='soilTemp2', blank=True, null=True)  # Field name made lowercase.
	soiltemp3 = models.FloatField(default=0, db_column='soilTemp3', blank=True, null=True)  # Field name made lowercase.
	soiltemp4 = models.FloatField(default=0, db_column='soilTemp4', blank=True, null=True)  # Field name made lowercase.
	leaftemp1 = models.FloatField(default=0, db_column='leafTemp1', blank=True, null=True)  # Field name made lowercase.
	leaftemp2 = models.FloatField(default=0, db_column='leafTemp2', blank=True, null=True)  # Field name made lowercase.
	extrahumid1 = models.FloatField(default=0, db_column='extraHumid1', blank=True, null=True)  # Field name made lowercase.
	extrahumid2 = models.FloatField(default=0, db_column='extraHumid2', blank=True, null=True)  # Field name made lowercase.
	soilmoist1 = models.FloatField(default=0, db_column='soilMoist1', blank=True, null=True)  # Field name made lowercase.
	soilmoist2 = models.FloatField(default=0, db_column='soilMoist2', blank=True, null=True)  # Field name made lowercase.
	soilmoist3 = models.FloatField(default=0, db_column='soilMoist3', blank=True, null=True)  # Field name made lowercase.
	soilmoist4 = models.FloatField(default=0, db_column='soilMoist4', blank=True, null=True)  # Field name made lowercase.
	leafwet1 = models.FloatField(default=0, db_column='leafWet1', blank=True, null=True)  # Field name made lowercase.
	leafwet2 = models.FloatField(default=0, db_column='leafWet2', blank=True, null=True)  # Field name made lowercase.
	rxcheckpercent = models.FloatField(default=0, db_column='rxCheckPercent', blank=True, null=True)  # Field name made lowercase.
	txbatterystatus = models.FloatField(default=0, db_column='txBatteryStatus', blank=True,
	                                    null=True)  # Field name made lowercase.
	consbatteryvoltage = models.FloatField(default=0, db_column='consBatteryVoltage', blank=True,
	                                       null=True)  # Field name made lowercase.
	hail = models.FloatField(default=0, blank=True, null=True)
	hailrate = models.FloatField(default=0, db_column='hailRate', blank=True, null=True)  # Field name made lowercase.
	heatingtemp = models.FloatField(default=0, db_column='heatingTemp', blank=True, null=True)  # Field name made lowercase.
	heatingvoltage = models.FloatField(default=0, db_column='heatingVoltage', blank=True, null=True)  # Field name made lowercase.
	supplyvoltage = models.FloatField(default=0, db_column='supplyVoltage', blank=True, null=True)  # Field name made lowercase.
	referencevoltage = models.FloatField(default=0, db_column='referenceVoltage', blank=True,
	                                     null=True)  # Field name made lowercase.
	windbatterystatus = models.FloatField(default=0, db_column='windBatteryStatus', blank=True,
	                                      null=True)  # Field name made lowercase.
	rainbatterystatus = models.FloatField(default=0, db_column='rainBatteryStatus', blank=True,
	                                      null=True)  # Field name made lowercase.
	outtempbatterystatus = models.FloatField(default=0, db_column='outTempBatteryStatus', blank=True,
	                                         null=True)  # Field name made lowercase.
	intempbatterystatus = models.FloatField(default=0, db_column='inTempBatteryStatus', blank=True,
	                                        null=True)  # Field name made lowercase.

	consistente = models.CharField(max_length=255, null=False)

	@property
	def outtemp_celsius(self):
	    temp = self.outtemp
	    new_temp = (temp - 32) * 5 / 9
	    return new_temp

	@property
	def windspeed_kmh(self):
	    temp = self.windspeed
	    new_temp = temp * 1.609
	    return new_temp

	@property
	def rain_mm(self):
	    rain = self.rain / 0.039370
	    return rain

	@property
	def pressure_hpa(self):
	    pressure = self.pressure * 33.86
	    return pressure

	class Meta:
	    ordering = ["datetime"]

	def __unicode__(self):
	    return "%s " % self.datetime

	def get_wdir(self):
	    dir = self.winddir
	    direction = ""
	    if dir >= 11.25 and dir < 33.75:
	        direction = "NNE"
	    elif dir >= 33.75 and dir < 56.25:
	        direction = "NE"
	    elif dir >= 56.25 and dir < 78.75:
	        direction = "ENE"
	    elif dir >= 78.25 and dir < 101.25:
	        direction = "Este"
	    elif dir >= 101.25 and dir < 123.75:
	        direction = "ESE"
	    elif dir >= 123.75 and dir < 146.25:
	        direction = "SE"
	    elif dir >= 146.25 and dir < 168.75:
	        direction = "SSE"
	    elif dir >= 168.75 and dir < 191.25:
	        direction = "S"
	    elif dir >= 191.25 and dir < 213.75:
	        direction = "S"
	    elif dir >= 213.75 and dir < 236.25:
	        direction = "SSW"
	    elif dir >= 236.25 and dir < 258.75:
	        direction = "WSW"
	    elif dir >= 258.75 and dir < 281.25:
	        direction = "W"
	    elif dir >= 281.25 and dir < 303.75:
	        direction = "WNW"
	    elif dir >= 303.75 and dir < 326.25:
	        direction = "NW"
	    elif dir >= 326.25 and dir < 348.75:
	        direction = "NNW"
	    else:
	        direction = "N"
	    return "%s" % direction
	#    class Meta:
	#    	ordering = ["-datetime"]


class RecordAdmin(admin.ModelAdmin):
    fields = ('datetime', 'usunits', 'interval', 'barometer', 'pressure', 'outtemp', 'outhumidity', 'windspeed', 'winddir', 'rain', 'dewpoint',  'et', 'radiation', 'radiation_total', 'uv', 'station', 'consistente')
    list_display = ('station', 'datetime', 'outtemp', 'outhumidity', 'rain', 'windspeed', 'winddir')
    list_filter = (
        'station',
        ('datetime', DateRangeFilter),
    )
    #actions = [export_to_csv]
    list_per_page = 40

class Control(models.Model):
    VARIABLES = ((1, 'pressure'), (2, 'outtemp'), (3, 'outhumidity'), (4, 'windspeed'), (5, 'winddir'), (6, 'rain'),
              (7, 'dewpoint'),(8, 'windchill'), (9, 'et'),(10, 'radiation'), (11, 'radiation_total'), (12, 'txbatterystatus'),
              (13, 'intempbatterystatus'))
    CONTROL = ((0,' '),(1,'NONE'),(2,'MINIMO'),(3,'MAXIMO'))
    
    variable = models.IntegerField(choices=VARIABLES, default=0, db_column='variable')
    control_var = models.IntegerField(choices=CONTROL, default=0,db_column='control_var')
    valor = models.CharField(max_length=255, null=True)

class ControlAdmin(admin.ModelAdmin):
    list_display = ('id','variable','control_var','valor')
    list_filter = ('variable','control_var')


