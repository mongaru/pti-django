"""pti_pesepy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
# from vialidad.views import (home, login, register)
from analisis_variables import views as analisisVariablesViews
from analisis_variables import periodo_controller as analisisVariablesPeriodo
from analisis_variables import anio_tipo_controller as analisisVariablesAnioTipo

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^reporte/anual/tipo/tabla', analisisVariablesAnioTipo.reporte_anual_generacion),
    url(r'^reporte/anual/tabla', analisisVariablesViews.reporte_anual_generacion),
    url(r'^reporte/anual', analisisVariablesViews.reporte_anual),

    url(r'^estacion/listadoInicio', analisisVariablesViews.estacion_listado_inicio),
    
    url(r'^reporte/periodo/tabla', analisisVariablesPeriodo.reporte_periodo_generacion),
    url(r'^reporte/periodo', analisisVariablesPeriodo.reporte_periodo),

    # comentar las url para las vistas de registro que trae django auth
    # url(r'^accounts/profile/',  RedirectView.as_view(url='/', permanent=False)),
    # url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^$', analisisVariablesViews.home, name='home'),
    # url(r'^register', register, name='register'),

    # url(r'^contact/add', vialidadViews.contactoAdd, name='contactoAdd'),

    # url(r'^login', vialidadViews.loginUser),
    # url(r'^register', 'vialidad.views.registerUser'),
    # url(r'^logout', vialidadViews.logoutUser),
    # url(r'^about', views.about),
]
