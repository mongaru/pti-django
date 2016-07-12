jQuery(document).ready(function($){
    Tabla.inicializar();
});

Tabla = {
    inicializar : null,
    mapa : null,
    infowindow : null,
    marcadores : []
}

Tabla.inicializar = function()
{
    Tabla.cargarMapa();
    Tabla.cargarPuntos();
}

Tabla.cargarPuntos = function()
{
    $('th.estacionRow').each(function(){
        
        var latLng = new google.maps.LatLng($(this).data('latitud'), $(this).data('longitud'));

        _marker_selector = new google.maps.Marker({
            position: latLng,
            title: $(this).data('nombre'),
            map: Tabla.mapa,
            // draggable: true,
            infoNombre : $(this).data('nombre'),
            infoCodigo : $(this).data('id'),
            // infoLink : estacion.detailsUrl
            icon : '/static/image/icon-orange.png'
        });

        _marker_selector.addListener('click', function() {
            // var contenido = '<div id="content"><h1 id="firstHeading" class="firstHeading">'+_marker_selector.infoNombre+'</h1><p>'+_marker_selector.infoLink+'</p></div>'
            var contenido = '<div id="content"><h4 id="firstHeading" class="firstHeading">'+_marker_selector.infoNombre+'</h4></div>'
            Tabla.infowindow.setContent(contenido);
            Tabla.infowindow.open(Tabla.mapa, _marker_selector);
        });

        Tabla.marcadores.push(_marker_selector);
    });
}

Tabla.cargarMapa = function()
{
    // verificar si existe el contenedor del mapa en la paigna
    if (jQuery("#map-filtro").length == 0)
        return;
    
    var latLng = new google.maps.LatLng(-25.28294542863535, -57.558564025878906);

    var map = new google.maps.Map(document.getElementById('map-filtro'), {
        zoom: 6,
        center: latLng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    var infowindow = new google.maps.InfoWindow();

    Tabla.mapa = map;
    Tabla.infowindow = infowindow;
}

Tabla.filtrarMapa = function()
{
    for (var i = 0; i < Tabla.marcadores.length; i++) {
        var codigo = Tabla.marcadores[i].infoCodigo;

        if ($('[data-id="'+codigo+'"]').is(":visible"))
        {
            Tabla.marcadores[i].setVisible(true);            
        }
        else
        {
            Tabla.marcadores[i].setVisible(false);
        }
    };
}

Tabla.marcarMapa = function()
{
    for (var i = 0; i < Tabla.marcadores.length; i++) {
        var codigo = Tabla.marcadores[i].infoCodigo;

        if ($('[data-id="'+codigo+'"] input[type="checkbox"]').is(":checked"))
        {
            Tabla.marcadores[i].setIcon('/static/image/icon-blue.png');
        }
        else
        {
            Tabla.marcadores[i].setIcon('/static/image/icon-orange.png')
        }
    };
}

