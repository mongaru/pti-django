jQuery(document).ready(function($){
    Inicio.inicializar();
});

Inicio = {
	inicializar : null,
	mapa : null,
	// infowindow : null
}

Inicio.inicializar = function()
{
	Inicio.cargarMapa();
	Inicio.cargarPuntos();
}

Inicio.cargarPuntos = function()
{
	jQuery.ajax({
        url : '/estacion/listadoInicio',
        type : "GET",
        dataType : "json",
        success : function (response) {
            var estaciones = response.data;

            for (var i = 0; i < estaciones.length; i++) {
            	var estacion = estaciones[i];

            	var latLng = new google.maps.LatLng(estacion.lat, estacion.lg);
                var nombre = estacion.name;
                var url = estacion.detailsUrl;

        	    Inicio.crearMarker(latLng, nombre, url);
            };
        }
    });
}

Inicio.crearMarker = function(latLng, nombre, url)
{
    var _marker_selector = new google.maps.Marker({
        position: latLng,
        title: nombre,
        map: Inicio.mapa,
        // draggable: true,
        infoNombre : nombre,
        // infoCodigo : id,
        infoLink : url
        // icon : '/static/image/icon-orange.png'
    });

    google.maps.event.addListener(_marker_selector, 'click', function() {
        var _infowindow = new google.maps.InfoWindow({
            content: '<div id="content"><h4 id="firstHeading" class="firstHeading">'+_marker_selector.infoNombre+'</h4></div>'
        });
        
        _infowindow.open(Tabla.mapa, _marker_selector);
    });
}


Inicio.cargarMapa = function()
{
    // verificar si existe el contenedor del mapa en la paigna
    if (jQuery("#map-canvas").length == 0)
        return;
    
	var latLng = new google.maps.LatLng(-25.28294542863535, -57.558564025878906);

    var map = new google.maps.Map(document.getElementById('map-canvas'), {
        zoom: 6,
        center: latLng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    // var infowindow = new google.maps.InfoWindow();

    Inicio.mapa = map;
    // Inicio.infowindow = infowindow;

    // _marker_selector = new google.maps.Marker({
    //     position: latLng,
    //     title: 'Seleccione la ubicacion',
    //     map: map,
    //     draggable: true
    // });

    // google.maps.event.addListener(_marker_selector, 'dragend', function() {

    //     $('#map_latitud').val(Math.round(_marker_selector.getPosition().lat()*1000)/1000);
    //     $('#map_longitud').val(Math.round(_marker_selector.getPosition().lng()*1000)/1000);
    //     var ll4 = new LatLng(_marker_selector.getPosition().lat(), _marker_selector.getPosition().lng());
    //     var utm = ll4.toUTMRef();
    //     $('#map_norte').val( parseFloat(Math.round(utm.northing*100)/100));
    //     $('#map_este').val(parseFloat(Math.round(utm.easting*100)/100));
    //     var zonaUTM = utm.lngZone + utm.latZone;
    //     $('#map_zona').val(zonaUTM);

    // });

    // $("#modalSlideUp").on("shown.bs.modal", function(e) {
    //   google.maps.event.trigger(map, "resize");
    //   return map.setCenter(latLng);
    // });
}