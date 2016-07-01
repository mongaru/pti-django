jQuery(document).ready(function($){
    EstacionGrafico.inicializar();
});

Highcharts.setOptions({
	lang: {
		months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
		shortMonths: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',  'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
		weekdays: ['Domingo', 'Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado']
	}
});

var Util = {
    getFechaActual : null,
    getFechaActualResta : null
};

/**
 * Obtiene la fecha actual
 * @return {String}
 */
Util.getFechaActual = function()
{
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth() + 1; //January is 0!
    var yyyy = today.getFullYear();
    if (dd < 10) {
        dd = '0' + dd;
    }
    if (mm < 10) {
        mm = '0' + mm;
    }
    var today = yyyy + '-' + mm + '-' + dd;
    return today;
};

Util.cargarFechaUltimoRegistro = function()
{
    var year = parseInt(jQuery('#mainContainer').data('year'));
    var month = parseInt(jQuery('#mainContainer').data('month'));
    var day = parseInt(jQuery('#mainContainer').data('day'));

    var today = new Date(year, month - 1, day); //January is 0!

    Util._fechaBase = today;
};


Util.getFechaUltimoRegistro = function()
{
    // var year = parseInt(jQuery('#mainContainer').data('year'));
    // var month = parseInt(jQuery('#mainContainer').data('month'));
    // var day = parseInt(jQuery('#mainContainer').data('day'));

    var year = jQuery('#mainContainer').data('year');
    var month = jQuery('#mainContainer').data('month');
    var day = jQuery('#mainContainer').data('day');

    //var today = new Date(year, month - 1, day); //January is 0!

    var today = year + '-' + month + '-' + day;
    return today;
};

/**
 * Obtiene la fecha actual menos la cantidad de dias
 * @param dias
 */
Util.getFechaActualResta = function(dias)
{
    //var today = new Date();
    var today = Util._fechaBase;
    var minus = new Date(today.getTime() - (dias * 24 * 3600 * 1000));


    var dd = minus.getDate();
    var mm = minus.getMonth() + 1; //January is 0!
    var yyyy = minus.getFullYear();
    if (dd < 10) {
        dd = '0' + dd;
    }
    if (mm < 10) {
        mm = '0' + mm;
    }
    var minus = yyyy + '-' + mm + '-' + dd;
    return minus;

};


var Loader = {
    showLoader : null,
    removeLoader : null,
    addLoaderElement : null,
    removeLoaderElement : null
};

// extender de HomeCharts para tener la implementacion de los metodos que se comparten
var HighCharts = {
    _loader : Loader,
    graficoLinea : null
};

HighCharts.graficoLinea = function(elementoSelector, datos, titulos, titulo, labelValor)
{
    jQuery(elementoSelector).highcharts({
        chart: {
            zoomType: 'x'
        },
        title: {
            text: titulo
        },
        subtitle: {
            text: document.ontouchstart === undefined ?
                    'Haga click y arrastre en el grafico para mayor zoom' :
                    'Pinch the chart to zoom in'
        },
        xAxis: {
            categories: titulos,
            //minRange: 14 * 24 * 3600000 // fourteen days
            labels: {
                rotation: -90,
                style: {
                    fontSize: '13px',
                    fontFamily: 'Verdana, sans-serif'
                }
            }
        },
        // yAxis: {
        //     title: {
        //         text: 'Exchange rate'
        //     }
        // },
        legend: {
            enabled: false
        },
        plotOptions: {
            area: {
                // fillColor: {
                //     linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                //     stops: [
                //         [0, Highcharts.getOptions().colors[0]],
                //         [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                //     ]
                // },
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            }
        },
        series: [{
            name: labelValor,
            //pointInterval: 24 * 3600 * 1000,
            //pointStart: Date.UTC(2006, 0, 1),
            data: datos,
            turboThreshold: 1000000000
        }]
    });
};

HighCharts.graficoLineaMultiple = function(elementoSelector, datos, titulos, titulo, labelValor)
{
    jQuery(elementoSelector).highcharts({
        chart: {
            zoomType: 'x'
        },
        title: {
            text: titulo
        },
        subtitle: {
            text: document.ontouchstart === undefined ?
                    'Haga click y arrastre en el grafico para mayor zoom' :
                    'Pinch the chart to zoom in'
        },
        xAxis: {
            categories: titulos,
            //minRange: 14 * 24 * 3600000 // fourteen days
            labels: {
                rotation: -90,
                style: {
                    fontSize: '13px',
                    fontFamily: 'Verdana, sans-serif'
                }
            }
        },
        // yAxis: {
        //     title: {
        //         text: 'Exchange rate'
        //     }
        // },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        plotOptions: {
            area: {
                // fillColor: {
                //     linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                //     stops: [
                //         [0, Highcharts.getOptions().colors[0]],
                //         [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                //     ]
                // },
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            }
        },
        series: datos
    });
};

HighCharts.graficoBarra = function(elementoSelector, datosX, datosY, titulo, labelValor)
{
    jQuery(elementoSelector).highcharts({
        chart: {
            type: 'column'
        },
        title: {
            text: titulo
        },
        // subtitle: {
        //     text: 'Source: WorldClimate.com'
        // },
        xAxis: {
            categories: datosX
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Valores'
            }
        },
        // tooltip: {
        //     headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
        //     pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
        //         '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
        //     footerFormat: '</table>',
        //     shared: true,
        //     useHTML: true
        // },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        series: [{
            name: labelValor,
            data: datosY
        }]
    });
};

HighCharts.graficoPolarGrados = function(elementoSelector, datosX, datosY, titulo, labelValor)
{
    jQuery(elementoSelector).highcharts({
        chart: {
            polar: true
        },

        title: {
            text: titulo
        },

        pane: {
            startAngle: 0,
            endAngle: 360
        },

        xAxis: {
            tickInterval: 22.5,
            min: 0,
            max: 360,
            labels: {

                formatter: function () {
                    var dir = {0 : 'N', 22.5 : 'NNE', 45 : 'NE', 67.5 : 'ENE', 90 : 'E', 112.5 : 'ESE', 135 : 'SE', 157.5 : 'SSE', 180 : 'S', 202.5 : 'SSW', 225 : 'SW', 247.5 : 'WSW', 270 : 'W', 292.5 : 'WNW', 315 : 'NW', 337.5 : 'NNW'};
                    return dir[this.value];
                    //return this.value + ' °';
                }
            }
        },

        yAxis: {
            min: 0
        },

        plotOptions: {
            series: {
                pointStart: 0,
                pointInterval: 22.5
            },
            column: {
                pointPadding: 0,
                groupPadding: 0
            }
        },

        series: [
            {
                type: 'line',
                name: labelValor,
                data: datosY
            }
        ]
    });
};

var EstacionGrafico = {
    _loader : Loader,
    _graficos : HighCharts,
    _fechaInicio : null,
    _fechaFin : null,
    _fechaDiezDiasInicio : null,
    temperaturaHistorico : null,
    velocidadHistorico : null,
    vientoHistorico : null,
    lluviaHistorico : null,
    graficoLinea : null,
    cargarDatosSincrono : null,
    inicializar : null
};

EstacionGrafico.inicializar = function()
{
    return;

    // verificar si se esta cargando una pagina de estaciones
    if (jQuery('#mainContainer').data('estacion') == undefined)
        return;

    Util.cargarFechaUltimoRegistro();
    EstacionGrafico._fechaInicio = Util.getFechaActualResta(45);
    EstacionGrafico._fechaFin =  Util.getFechaUltimoRegistro();
    EstacionGrafico._fechaDiezDiasInicio = Util.getFechaActualResta(10);
    EstacionGrafico._estacionId = jQuery('#mainContainer').data('estacion');

    if (jQuery('.chart-evolucion-horaria').length)
        EstacionGrafico.temperaturaHistorico('.chart-evolucion-horaria');

    if (jQuery('.chart-humedad-promedio').length)
        EstacionGrafico.humedadHistorico('.chart-humedad-promedio');

    if (jQuery('.chart-daily-precipitation').length)
        EstacionGrafico.precipitacionHistorico('.chart-daily-precipitation');

    if (jQuery('.chart-accumulated-precipitation').length)
        EstacionGrafico.precipitacionMensual('.chart-accumulated-precipitation');

    if (jQuery('.chart-radiation').length)
        EstacionGrafico.radiacionHistorico('.chart-radiation');

    if (jQuery('.chart-pressure').length)
        EstacionGrafico.presionHistorico('.chart-pressure');

    if (jQuery('.chart-wind').length)
        EstacionGrafico.vientoHistorico('.chart-wind');
};

EstacionGrafico.cargarDatosSincrono = function(url, desde, hasta)
{
    var resultDatos;

    jQuery.ajax({
        url : url + "?desde=" + desde + "&hasta=" + hasta,
        type : "GET",
        async : false,
        dataType : "json",
        success : function (response) {
            resultDatos = response.data;
        }
    });

    return resultDatos;
};


EstacionGrafico.graficoPorEstacion = function(url, tipoGrafico, variable)
{
    jQuery.ajax({
        url : url,
        type : "GET",
        dataType : "json",
        success : function (response) {
            if (tipoGrafico == 'grafico')
                EstacionGrafico.graficarVariable('.chart-panel', response.data, variable);

            if (tipoGrafico == 'graficoPorAnio')
                EstacionGrafico.graficarVariablePorAnio('.chart-panel', response.data, variable);
        }
    });
}

EstacionGrafico.graficarVariable = function(elementoSelector, datos, variable)
{
    // var datos = EstacionGrafico.cargarDatosSincrono('/temperatura/historico/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    var serie = [];
    var titulos = [];

    // preparar los datos
    for (var i = 0; i < datos.length; i++)
    {
        var fila = {x: datos[i].fecha, name: datos[i].fecha};

        if (variable == "winddir")
            fila['y'] = datos[i].winddir;

        if (variable == "windspeed")
            fila['y'] = datos[i].windspeed;

        if (variable == "presion")
            fila['y'] = datos[i].presion;

        if (variable == "temperatura")
            fila['y'] = datos[i].temperatura;
        
        // serie.push(fila);
        serie.push(fila['y']);
        titulos.push(datos[i].fecha);
    }

    EstacionGrafico._graficos.graficoLinea(elementoSelector, serie, titulos, 'Registros de variable en periodo', 'Valores');
};

EstacionGrafico.graficarVariablePorAnio = function(elementoSelector, datos, nombreVariable)
{
    // var datos = EstacionGrafico.cargarDatosSincrono('/temperatura/historico/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    var titulos = [];
    var cargoTitulos = false;
    var valores = [];

    for (key in datos['valores'])
    {
        var filas = datos['valores'][key];
        var valoresAnio = [];

        for (var i = 0; i < filas.length; i++)
        {
            // if (cargoTitulos == false)
            // {
            //     titulos.push(columna);
            // }

            var variables = filas[i];

            if (isEmpty(variables))
            {
                valoresAnio.push(-10);
                continue;
            }

            if (nombreVariable == "winddir")
                valoresAnio.push(variables['winddir']);

            if (nombreVariable == "windspeed")
                valoresAnio.push(variables['windspeed']);

            if (nombreVariable == "presion")
                valoresAnio.push(variables['presion']);

            if (nombreVariable == "temperatura")
                valoresAnio.push(variables['temperatura']);
                
        }

        cargoTitulos = true;

        valores.push({name : key, data : valoresAnio});
    }

    EstacionGrafico._graficos.graficoLineaMultiple(elementoSelector, valores, datos['columnas'], 'Registros de variable en periodo', 'Valores');
};

EstacionGrafico.graficarVariablePorAnio2 = function(elementoSelector, datos, nombreVariable)
{
    // var datos = EstacionGrafico.cargarDatosSincrono('/temperatura/historico/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    var titulos = [];
    var cargoTitulos = false;
    var valores = [];

    for (key in datos)
    {
        var filas = datos[key];
        var valoresAnio = [];

        for (columna in filas)
        {
            if (cargoTitulos == false)
            {
                titulos.push(columna);
            }

            var variables = filas[columna];

            if (isEmpty(variables))
            {
                valoresAnio.push(-10);
                continue;
            }

            if (nombreVariable == "winddir")
                valoresAnio.push(variables['winddir']);

            if (nombreVariable == "windspeed")
                valoresAnio.push(variables['windspeed']);

            if (nombreVariable == "presion")
                valoresAnio.push(variables['presion']);

            if (nombreVariable == "temperatura")
                valoresAnio.push(variables['temperatura']);
                
        }

        cargoTitulos = true;

        valores.push({name : key, data : valoresAnio});
    }

    EstacionGrafico._graficos.graficoLineaMultiple(elementoSelector, valores, titulos, 'Registros de variable en periodo', 'Valores');
};


function isEmpty( o ) {
    for ( var p in o ) { 
        if ( o.hasOwnProperty( p ) ) { return false; }
    }
    return true;
}

EstacionGrafico.temperaturaHistorico = function(elementoSelector)
{
    var datos = EstacionGrafico.cargarDatosSincrono('/temperatura/historico/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    var serie = [];

    // preparar los datos
    for (var i = 0; i < datos.length; i++)
    {
        serie.push({x: datos[i].datetime * 1000, y: datos[i].outtemp, name: datos[i].datetime  * 1000});
    }

    EstacionGrafico._graficos.graficoLinea(elementoSelector, serie, 'Registros de Temperatura por dia', 'Temperatura');
};

EstacionGrafico.humedadHistorico = function(elementoSelector)
{
    var datos = EstacionGrafico.cargarDatosSincrono('/humedad/historico/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    var serie = [];

    // preparar los datos
    for (var i = 0; i < datos.length; i++)
    {
        serie.push({x: datos[i].datetime * 1000, y: datos[i].outhumidity, name: datos[i].datetime  * 1000});
    }

    EstacionGrafico._graficos.graficoLinea(elementoSelector, serie, 'Registros de Humedad por dia', 'Humedad');
};

EstacionGrafico.vientoHistorico = function(elementoSelector)
{
    var datos = EstacionGrafico.cargarDatosSincrono('/viento/historico/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    var serie = [];

    // preparar los datos
    for (var i = 0; i < datos.length; i++)
    {
        serie.push({x: datos[i].datetime, y: datos[i].windspeed, name: datos[i].datetime});
    }

    EstacionGrafico._graficos.graficoLinea(elementoSelector, serie, 'Registros de Velocidad del Viento por dia', 'Velocidad');
};

EstacionGrafico.vientoDireccionHistorico = function(elementoSelector)
{
    var datos = EstacionGrafico.cargarDatosSincrono('/viento/conteo_direccion/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    EstacionGrafico._graficos.graficoPolarGrados(elementoSelector, datos['direcciones'], datos['valores'], 'Lecturas de Direccion del Viento', 'Cantidad de Lecturas');
};

EstacionGrafico.precipitacionHistorico = function(elementoSelector)
{
    var datos = EstacionGrafico.cargarDatosSincrono('/precipitacion/acumulado_dia/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    EstacionGrafico._graficos.graficoBarra(elementoSelector, datos['dias'], datos['valores'], 'Precipitacion Acumulada por dia', 'Lluvia (mm)');
};

EstacionGrafico.precipitacionMensual = function(elementoSelector)
{
    var datos = EstacionGrafico.cargarDatosSincrono('/precipitacion/acumulado_mensual/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    EstacionGrafico._graficos.graficoBarra(elementoSelector, datos['meses'], datos['valores'], 'Precipitacion Mensual Acumulada', 'Lluvia (mm)');
};

EstacionGrafico.radiacionHistorico = function(elementoSelector)
{
    var datos = EstacionGrafico.cargarDatosSincrono('/radiacion/historico/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    var serie = [];

    // preparar los datos
    for (var i = 0; i < datos.length; i++)
    {
        serie.push({x: datos[i].datetime, y: datos[i].radiation, name: datos[i].datetime});
    }

    EstacionGrafico._graficos.graficoLinea(elementoSelector, serie, 'Registros de Radiacion por dia', 'Radiacion');
};

EstacionGrafico.presionHistorico = function(elementoSelector)
{
    var datos = EstacionGrafico.cargarDatosSincrono('/presion/historico/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    var serie = [];

    // preparar los datos
    for (var i = 0; i < datos.length; i++)
    {
        serie.push({x: datos[i].datetime, y: datos[i].pressure, name: datos[i].datetime});
    }

    EstacionGrafico._graficos.graficoLinea(elementoSelector, serie, 'Registros de Presion Atmosferica por dia', 'Presion');
};

var Dashboard = {
    _idEstacion : null,
    inicializar : null,
    temperaturaTabListener : null,
    vientoTabListener : null
};

Dashboard.inicializar = function()
{
    EstacionGrafico.inicializar();
    Dashboard._idEstacion = 1;
    Dashboard.temperaturaTabListener();

    //EstacionGrafico._fechaFin = '2014-11-14';
    //EstacionGrafico._fechaInicio = '2014-11-25';
    //EstacionGrafico._fechaDiezDiasInicio = '2014-11-22';
};

Dashboard.temperaturaTabListener = function()
{
    jQuery("#btnGrafTemp").click(function(){
        // es el valor antes de terminar la transicion por lo que todavia no se ve
        if (jQuery('#collapse-temperature').is(':hidden'))
        {
            EstacionGrafico.temperaturaHistorico("#temp-tab1");
        }
    });

    jQuery("#btnGrafVientoVel").click(function(){
        // es el valor antes de terminar la transicion por lo que todavia no se ve
        if (jQuery('#collapse-wind-speed').is(':hidden'))
        {
            EstacionGrafico.vientoHistorico("#wind-speed-tab1");
        }
    });

    jQuery("#btnGrafVientoDir").click(function(){
        // es el valor antes de terminar la transicion por lo que todavia no se ve
        if (jQuery('#collapse-winddir').is(':hidden'))
        {
            EstacionGrafico.vientoDireccionHistorico("#winddir-tab1");
        }
    });

    jQuery("#btnGrafPrecipitaciones").click(function(){
        // es el valor antes de terminar la transicion por lo que todavia no se ve
        if (jQuery('#collapse-rainfall').is(':hidden'))
        {
            EstacionGrafico.precipitacionHistorico("#rainfall-tab1");
        }
    });
};

Reporte1 = {
    generarReporte : null
};

Reporte1.generarReporte = function()
{
    var estaciones = [];

    jQuery('#select-estacion li a').each(function(){
        if (!jQuery(this).hasClass('select-all') && jQuery(this).hasClass('selected'))
            estaciones.push(jQuery(this).attr('id'));
    });

    var campos = [];

    jQuery('#select-medicion li a').each(function(){
        if (!jQuery(this).hasClass('select-all')  && jQuery(this).hasClass('selected'))
            campos.push(jQuery(this).attr('id'));
    });

    var informe = jQuery('#select-informe li a.selected').attr('id');

    var intervalo_desde = jQuery('#select-intervalo li a.selected').attr('data-desde');
    var intervalo_hasta = jQuery('#select-intervalo li a.selected').attr('data-hasta');

    var data = {'rep_estaciones' : estaciones.join(','), 'rep_atributos' : campos.join(','), 'rep_informe' : informe, 'rep_desde' : intervalo_desde, 'rep_hasta' : intervalo_hasta};

    console.log(data);

    jQuery.ajax({
        url : '/reporte/generar',
        type : "POST",
        data : data,
        async : true,
        dataType : "json",
        success : function (response)
        {
            //$('#tablent-report').removeClass('hidden');
            jQuery('#tabla-report-container').html(response.data);
        }
    });

}

function pronos()
{
    var filas = jQuery('#climaContent').find('table tr');
    var pronoFecha = jQuery('#climaContent').find('div.Estilo8').text();
    var dia = jQuery(jQuery(filas.get(3)).find('td').get(0)).text();
    var icono = jQuery(jQuery(filas.get(4)).find('td').get(0)).find('div').html();
    var pronostico = jQuery(jQuery(filas.get(5)).find('td').get(0)).find('div span').html();
    var temperaturas = jQuery(jQuery(filas.get(6)).find('td').get(0)).find('strong');
    var minima = jQuery(temperaturas.get(0)).text();
    var maxima = jQuery(temperaturas.get(1)).text();

    icono = jQuery(icono).attr('src', 'http://www.meteorologia.gov.py/' + jQuery(icono).attr('src')).attr('title', pronostico);

    jQuery('#pronosDate').html(pronoFecha);
    jQuery('#cellDia1').html(dia);
    jQuery('#cellIcono1').html(icono);
    jQuery('#cellMinima1').html( minima);
    jQuery('#cellMaxima1').html( maxima);

    dia = jQuery(jQuery(filas.get(3)).find('td').get(2)).text();
    icono = jQuery(jQuery(filas.get(4)).find('td').get(2)).find('div').html();
    pronostico = jQuery(jQuery(filas.get(5)).find('td').get(2)).find('div span').html();
    temperaturas = jQuery(jQuery(filas.get(6)).find('td').get(2)).find('strong');
    minima = jQuery(temperaturas.get(0)).text();
    maxima = jQuery(temperaturas.get(1)).text();

    icono = jQuery(icono).attr('src', 'http://www.meteorologia.gov.py/' + jQuery(icono).attr('src')).attr('title', pronostico);

    jQuery('#cellDia2').html(dia);
    jQuery('#cellIcono2').html(icono);
    jQuery('#cellMinima2').html(minima);
    jQuery('#cellMaxima2').html(maxima);

    dia = jQuery(jQuery(filas.get(3)).find('td').get(4)).text();
    icono = jQuery(jQuery(filas.get(4)).find('td').get(4)).find('div').html();
    pronostico = jQuery(jQuery(filas.get(5)).find('td').get(4)).find('div span').html();
    temperaturas = jQuery(jQuery(filas.get(6)).find('td').get(4)).find('strong');
    minima = jQuery(temperaturas.get(0)).text();
    maxima = jQuery(temperaturas.get(1)).text();

    icono = jQuery(icono).attr('src', 'http://www.meteorologia.gov.py/' + jQuery(icono).attr('src')).attr('title', pronostico);

    jQuery('#cellDia3').html(dia);
    jQuery('#cellIcono3').html(icono);
    jQuery('#cellMinima3').html(minima);
    jQuery('#cellMaxima3').html(maxima);
    jQuery('#pronostico').show();
}

