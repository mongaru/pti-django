from analisis_variables.models import *
from django.contrib import admin

# Register your models here.
admin.site.register(Station, StationAdmin)
admin.site.register(TypeStation, TypeStationAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Control, ControlAdmin)
