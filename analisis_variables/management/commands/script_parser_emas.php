<?php
/*
* Authors: @juliancpy Julian Caceres and Teddy Limousin.
* 
* Sistema de conversiones para las unidades registradas por el Datalogger 
* Las unidades de los datos obtenidos difieren de las unidades del SI. Por ello
* se tendra que realizar diversas conversinoes.
*  
	barometer	" Hg	x	33,86388	=	HPa
	pressure	" Hg	x	33,86388	=	HPa
	altimeter	" Hg	x	33,86388	=	HPa		
	intemp		°F		°C = (°F-32)/1,8	=	°C
	outtemp		°F		°C = (°F-32)/1,8	=	°C
	inhumidity	 %		% = %	%
	outhumidity	 %		% = %	%
	windspeed	mph		0,44704	m/s
	winddir		°		° = °	°
	windgust			
	windgustdir			
	rainrate	"/h		x	25,40000	=	mm/h
	rain		"		x	25,40000	=	mm
	dewpoint	°F		°C = (°F-32)/1,8	=	°C
	windchill	°F		°C = (°F-32)/1,8	=	°C
	heatindex	°F		°C = (°F-32)/1,8	=	°C
	et			"		25,40000			=	mm
	radiation	w/m²	w/m² = w/m²	=		=	w/m²
	uv			
	extratemp1	°F		°C = (°F-32)/1,8	=	°C
*
*/
// $LOG = "/home/vagrant/Code/migdb.log";
$USER_MYSQL = "homestead";
$PASSWD_MYSQL = "secret";
$BD_MYSQL = "pti_pesepy";
// $PATH_SQLITE_DB = "/home/vagrant/Code/svn-agroclima/";
	// error_log('Inicio del proceso de migracion.'.date('D, d M Y H:i:s T')."\n",3,$LOG);

	// arreglo que contiene el nombre de las estaciones y el path de las base de datos.
	//$estaciones = array(
	//	'encarnacion' => '$PATH_HOME/Downloads/wview-archive.sdb',
	//);
	
	$estaciones = array();
	
	// $path = $PATH_SQLITE_DB; // '.' el directorio actual
	//foreach (new DirectoryIterator($path) as $file)
	//{
	//	if($file->isDot()) continue;

	//	if($file->isDir())
	//	{
	//		$estaciones[strtolower($file->getFilename())] = $path.$file->getFilename().'/wview-archive.sdb';
	//	}
	//}
	
	$db_usuario = $USER_MYSQL;
	$db_pass = $PASSWD_MYSQL;
	$db_nombre = $BD_MYSQL;

	try 
	{
		// conexion a la base de datos local
		// $conn = new PDO('mysql:host=127.0.0.1;dbname='.$db_nombre, $db_usuario, $db_pass);
		$conn = new PDO('pgsql:host=127.0.0.1;dbname='.$db_nombre, $db_usuario, $db_pass);
		$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
		// verificamos a que estacion corresponde, comparando los nombres de carpetas establecidos.
		$stmt0 = $conn->prepare('SELECT * FROM analisis_variables_station');
		$stmt0->execute();
		
		while($row = $stmt0->fetch(PDO::FETCH_OBJ)) 
			{
				if($row->type_id == '2'){
					$estaciones[$row->path_db] = $path.$row->path_db.'/wview-archive.sdb';
				}
			}
			
		// por cada estacion en el listado de base de datos. Realizamos la migracion
		
		foreach($estaciones as $indice => $db)
		{
			// error_log('-->Migrando datos de estacion '.$indice."\n",3,$LOG);
			echo '-->Migrando datos de estacion '.$indice."\n";

			// verificamos a que estacion corresponde, comparando los nombres de carpetas establecidos.
			$stmt0 = $conn->prepare('SELECT * FROM analisis_variables_station where path_db = :estacion order by id desc limit 1');
			$stmt0->execute(array(':estacion' => $indice));
			while($row = $stmt0->fetch(PDO::FETCH_OBJ)) 
			{
					$id = $row->id;
			}			
			// verificamos el dato mas reciente
			$stmt = $conn->prepare('SELECT * FROM analisis_variables_record where station_name = :estacion order by id desc limit 1');

			$stmt->execute(array(':estacion' => $indice));
			
			// variable para guardar la fecha mas reciente
			$ultima_fecha = '';

			// verificamos si hay registros y si los hay obtenemos la fecha
			while($row = $stmt->fetch(PDO::FETCH_OBJ)) 
			{
				$ultima_fecha = $row->dateTime;
			}
			
			// conexion a la base de datos de la estacion
			$dbh = new PDO("sqlite:".$db);

			echo var_dump($db);
			
			// variable para guardar la consulta a realizar a la base de datos de la estacion
			$stmt2 = null;
			
			if ($ultima_fecha == '') // si la base de datos no tiene datos recientes entonces cargamos todos los datos
			{
				$stmt2 = $dbh->prepare("SELECT datetime(dateTime, 'unixepoch', 'localtime') as time, * FROM archive order by dateTime asc;");
				$stmt2->execute();
			}
			else
			{
				// si la base de datos tiene datos recientes entonces indicamos la fecha desde donde buscar los datos
				$stmt2 = $dbh->prepare("SELECT datetime(dateTime, 'unixepoch', 'localtime') as time, * FROM archive where time > :ultima_fecha order by dateTime asc;");
				$stmt2->execute(array(':ultima_fecha' => $ultima_fecha));
			}
			 
			// recorremos los datos obtenidos e insertamos en la base de datos
			while($row = $stmt2->fetch(PDO::FETCH_OBJ)) 
			{
				// el query de insercion
				$stmt = $conn->prepare('INSERT INTO analisis_variables_record VALUES(default , :dateTime , :usUnits , 
:interval , :barometer , :pressure , :altimeter , '.
								':inTemp , :outTemp , :inHumidity , :outHumidity , :windSpeed , :windDir , :windGust , '.
								':windGustDir , :rainRate , :rain, :dewpoint , :windchill , :heatindex , :ET , :radiation , 0 , '.
								':UV , :extraTemp1 , :extraTemp2 , :extraTemp3 , :soilTemp1 , :soilTemp2 , :soilTemp3 , :soilTemp4 , '.
								':leafTemp1 , :leafTemp2 , :extraHumid1 , :extraHumid2 , :soilMoist1 , :soilMoist2 ,:soilMoist3, '.
								':soilMoist4 , :leafWet1 , :leafWet2 , :rxCheckPercent , :txBatteryStatus , :consBatteryVoltage , :hail , '.
								':hailRate , :heatingTemp , :heatingVoltage , :supplyVoltage , :referenceVoltage , :windBatteryStatus , '.
								':rainBatteryStatus , :outTempBatteryStatus , :inTempBatteryStatus, :estacion, '.$id.', \'si\' )');
				
				// asignamos los datos y ejecutamos insercion
				$stmt->execute(array( 
					':estacion' => $indice,					
					':dateTime' => $row->time,
					':usUnits' => $row->usUnits ,
					':interval' => $row->interval,
					':barometer' => ($row->barometer != 'None' ) ? $row->barometer*33.86388 : -999,
					':pressure' => ($row->pressure != 'None') ? ($row->pressure*33.86388) : -999 ,
					':altimeter' => ($row->altimeter != 'None') ? ($row->altimeter*33.86388) : -999, 
					':inTemp' => ($row->inTemp != 'None') ? (($row->inTemp-32)*5/9) : -999, 
					':outTemp' => ($row->outTemp != 'None') ? (($row->outTemp-32)*5/9) : -999, 
					':inHumidity' => $row->inHumidity ,
					':outHumidity' => $row->outHumidity, 
					':windSpeed' => ($row->windSpeed!='None') ? ($row->windSpeed*0.44704) : -999 ,
					':windDir' => $row->windDir ,
					':windGust' => ($row->windGust != 'None') ? ($row->windGust*0.44704) : -999, 
					':windGustDir' => $row->windGustDir ,
					':rainRate' => ($row->rainRate != 'None') ? ($row->rainRate*25.40000) : -999 ,
					':rain' => ($row->rain!='None') ? ($row->rain*25.40000) : -999  ,
					':dewpoint' => ($row->dewpoint != 'None') ? (($row->dewpoint-32)*5/9) : -999 ,
					':windchill' => ($row->windchill != 'None') ? (($row->windchill-32)*5/9) : -999, 
					':heatindex' => ($row->heatindex != 'None') ? (($row->heatindex-32)*5/9) : -999 ,
					':ET' => ($row->ET != 'None') ? ($row->ET*25.40000) : -999  ,
					':radiation' => $row->radiation ,
					':UV' => $row->UV ,
					':extraTemp1' => $row->extraTemp1 ,
					':extraTemp2' => $row->extraTemp2 ,
					':extraTemp3' => $row->extraTemp3 ,
					':soilTemp1' => $row->soilTemp1 ,
					':soilTemp2' => $row->soilTemp2 ,
					':soilTemp3' => $row->soilTemp3 ,
					':soilTemp4' => $row->soilTemp4 ,
					':leafTemp1' => $row->leafTemp1 ,
					':leafTemp2' => $row->leafTemp2 ,
					':extraHumid1' => $row->extraHumid1 ,
					':extraHumid2' => $row->extraHumid2 ,
					':soilMoist1' => $row->soilMoist1 ,
					':soilMoist2' => $row->soilMoist2 ,
					':soilMoist3' => $row->soilMoist3 ,
					':soilMoist4' => $row->soilMoist4 ,
					':leafWet1' => $row->leafWet1 ,
					':leafWet2' => $row->leafWet2 ,
					':rxCheckPercent' => $row->rxCheckPercent ,
					':txBatteryStatus' => $row->txBatteryStatus, 
					':consBatteryVoltage' => $row->consBatteryVoltage ,
					':hail' => $row->hail ,
					':hailRate' => $row->hailRate ,
					':heatingTemp' => $row->heatingTemp ,
					':heatingVoltage' => $row->heatingVoltage ,
					':supplyVoltage' => $row->supplyVoltage ,
					':referenceVoltage' => $row->referenceVoltage ,
					':windBatteryStatus' => $row->windBatteryStatus, 
					':rainBatteryStatus' => $row->rainBatteryStatus ,
					':outTempBatteryStatus' => $row->outTempBatteryStatus ,
					':inTempBatteryStatus' => $row->inTempBatteryStatus
				));

			}
			
			// error_log('-->Fin de migracion de datos datos de estacion '.$indice."\n",3,$LOG);
			echo '-->Fin de migracion de datos datos de estacion '.$indice."\n";
		}
		// error_log('Fin del proceso de Migracion. '.date('D, d M Y H:i:s T')."\n",3,$LOG);
		echo 'Fin del proceso de Migracion. '.date('D, d M Y H:i:s T')."\n";
	}
	catch(PDOException $e)
	{
		//TODO
		// cambiar la impresion de errores por logs
		echo $e->getMessage();
	}
	
	// Codigo de prueba
	// SELECT datetime(dateTime, 'unixepoch', 'localtime') as time  FROM archive where time > '2012-04-01 10:10:00'
	
?>
