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


// extender de HomeCharts para tener la implementacion de los metodos que se comparten
var HighCharts = {
    // _loader : Loader,
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
            // title: {
            //     text: labelValor
            // }
        },
        yAxis: {
            title: {
                text: labelValor
            }
        },
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
        yAxis: {
            title: {
                text: labelValor
            }
        },
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
    // _loader : Loader,
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

            $('.form-loader').css("display", "none");
        }
    });
}

EstacionGrafico.graficarVariable = function(elementoSelector, datos, variable)
{
    // var datos = EstacionGrafico.cargarDatosSincrono('/temperatura/historico/' + EstacionGrafico._estacionId, EstacionGrafico._fechaDiezDiasInicio, EstacionGrafico._fechaFin);

    var serie = [];
    var titulos = [];

    var tituloGrafico = 'Registros de variable en periodo';
    var tituloEje = 'Valores';  

    // preparar los datos
    for (var i = 0; i < datos.length; i++)
    {
        var fila = {x: datos[i].fecha, name: datos[i].fecha};

        if (variable == "winddir")
        {
            fila['y'] = datos[i].winddir;
            tituloGrafico = 'Registros de direccion de viento';
            tituloEje = "Valores en grados";
        }

        if (variable == "windspeed")
        {
            fila['y'] = datos[i].windspeed;
            tituloGrafico = 'Registros de velocidad de viento';
            tituloEje = "Valores en m\\s";
        }

        if (variable == "presion")
        {
            fila['y'] = datos[i].presion;
            tituloGrafico = 'Registros de presion atmosferica';
            tituloEje = "Valores en hectopascales";
        }

        if (variable == "temperatura")
        {
            fila['y'] = datos[i].temperatura;
            tituloGrafico = 'Registros de temperatura';
            tituloEje = "Valores en grados celcius";
        }

        if (variable == "radiation")
        {
            fila['y'] = datos[i].radiation;
            tituloGrafico = 'Registros de radiacion';
            tituloEje = "Valores";
        }

        if (variable == "winddir50")
        {
            fila['y'] = datos[i].winddir50;
            tituloGrafico = 'Registros de direccion de viento a 50 metros';
            tituloEje = "Valores en grados";
        }

        if (variable == "windspeed50")
        {
            fila['y'] = datos[i].windspeed50;
            tituloGrafico = 'Registros de velocidad de viento a 50 metros';
            tituloEje = "Valores en m\\s";
        }
        
        // serie.push(fila);
        serie.push(fila['y']);
        titulos.push(datos[i].fecha);
    }

    EstacionGrafico._graficos.graficoLinea(elementoSelector, serie, titulos, tituloGrafico, tituloEje);
};

EstacionGrafico.graficarVariablePorAnio = function(elementoSelector, datos, nombreVariable)
{
    var valores = [];
    var tituloGrafico = 'Registros de variable en periodo';
    var tituloEje = 'Valores';  

    for (key in datos['valores'])
    {
        var filas = datos['valores'][key];
        var valoresAnio = [];

        for (var i = 0; i < filas.length; i++)
        {
            var variables = filas[i];

            if (EstacionGrafico.isEmpty(variables))
            {
                valoresAnio.push(-10);
                continue;
            }

            if (nombreVariable == "winddir")
            {
                valoresAnio.push(variables['winddir']);
                tituloGrafico = 'Registros de direccion de viento';
                tituloEje = "Valores en grados";
            }

            if (nombreVariable == "windspeed")
            {
                valoresAnio.push(variables['windspeed']);
                tituloGrafico = 'Registros de velocidad de viento';
                tituloEje = "Valores en m\\s";
            }

            if (nombreVariable == "presion")
            {
                valoresAnio.push(variables['presion']);
                tituloGrafico = 'Registros de presion atmosferica';
                tituloEje = "Valores en hectopascales";
            }

            if (nombreVariable == "temperatura")
            {
                valoresAnio.push(variables['temperatura']);
                tituloGrafico = 'Registros de temperatura';
                tituloEje = "Valores en grados celcius";
            }

            if (nombreVariable == "radiation")
            {
                valoresAnio.push(variables['radiation']);
                tituloGrafico = 'Registros de radiacion';
                tituloEje = "Valores";
            }

            if (nombreVariable == "winddir50")
            {
                valoresAnio.push(variables['winddir50']);
                tituloGrafico = 'Registros de direccion de viento a 50 metros';
                tituloEje = "Valores en grados";
            }

            if (nombreVariable == "windspeed50")
            {
                valoresAnio.push(variables['windspeed50']);
                tituloGrafico = 'Registros de velocidad de viento a 50 metros';
                tituloEje = "Valores en m\\s";
            }
                
        }

        valores.push({name : key, data : valoresAnio});
    }

    EstacionGrafico._graficos.graficoLineaMultiple(elementoSelector, valores, datos['columnas'], tituloGrafico, tituloEje);
};

EstacionGrafico.isEmpty = function( o ) {
    for ( var p in o ) { 
        if ( o.hasOwnProperty( p ) ) { return false; }
    }
    return true;
}

