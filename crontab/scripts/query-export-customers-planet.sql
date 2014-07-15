set character_set_connection=utf8;
set character_set_filesystem=utf8;
SELECT 
C.id_cliente as 'id_cliente',
CONVERT(C.direccion_facturacion USING utf8) as 'Address1',
CONVERT(C.poblacion USING utf8) as 'Address2',
C.cif as 'cif',
CONVERT(C.nombre USING utf8) as 'nombre',
CONVERT(C.razon_social USING utf8) as 'razon_social',
CONCAT(CONVERT(C.apellidos USING utf8),' ',C.web) as 'info',
C.telefono1 as 'telefono1',
C.telefono2 as 'telefono2',
C.fax as 'fax',
C.email as 'email',
IF(ISNULL(C.persona_contacto) OR LENGTH(TRIM(C.persona_contacto))=0,'',CONCAT(CONVERT(C.persona_contacto USING utf8),'  ',CONVERT(IF(ISNULL(C.cargo_persona_contacto) OR LENGTH(TRIM(C.cargo_persona_contacto))=0,'',CONCAT('[',C.cargo_persona_contacto,']')) USING utf8))) as 'persona_contacto_uno',
IF(ISNULL(CE.persona_contacto) OR LENGTH(TRIM(CE.persona_contacto))=0,'',CONCAT(CONVERT(CE.persona_contacto USING utf8),' / ',CONVERT(IF(ISNULL(CE.cargo_persona_contacto),'',CE.cargo_persona_contacto) USING utf8))) as 'persona_contacto_dos',
CONVERT(IF(ISNULL(C.poblacion),'',C.poblacion) USING utf8) as 'poblacion',
C.cp as 'codigo_postal',
CONVERT(P.nombre USING utf8) as 'provincia',
-- CE.observaciones as 'observaciones',
CONCAT( REPLACE(CONVERT(CE.observaciones USING utf8),'
\n',' ') ) as 'observaciones',
DATE_FORMAT(IF(ISNULL(CE.fecha_alta),DATE_SUB(NOW(),INTERVAL 1 YEAR),CE.fecha_alta),"%d/%m/%Y") as 'fecha_alta',
DATE_FORMAT(IF(ISNULL(CE.ultima_modificacion),NOW(),CE.ultima_modificacion),"%d/%m/%Y") as "ultima_modificacion"
FROM Clientes C JOIN Clientes_empresas CE ON (CE.id_cliente=C.id_cliente AND CE.id_empresa=1)
LEFT JOIN Provincias P ON (C.id_provincia=P.id_provincia)
JOIN Agentes_clientes AC ON (C.id_cliente=AC.id_cliente AND AC.id_agente=7)
WHERE CE.fecha_baja IS NULL
ORDER BY CE.ultima_modificacion desc 
INTO OUTFILE '/Library/WebServer/Documents/planetdata/customers.csv'
FIELDS TERMINATED BY '\t'
-- ENCLOSED BY '"'
LINES TERMINATED BY '\n'
