set character_set_connection=utf8;
set character_set_filesystem=utf8;
SELECT
A.id_articulo,
CONVERT(A.nombre USING utf8) as 'nombre',
CONCAT( REPLACE(CONVERT(A.descripcion USING utf8),'
\n',' ')
,' ',REPLACE(CONVERT(Ea.descripcion USING utf8),'
',' ')) as descripcion,
REPLACE(A.codigo_barras,'
','') as 'codigo_barras',
IF(ISNULL(A.peso_unidad),0,A.peso_unidad) as "peso",
DATE_FORMAT(IF(ISNULL(Ea.fecha_alta),DATE_SUB(NOW(),INTERVAL 1 YEAR),Ea.fecha_alta),"%d/%m/%Y") as 'fecha_alta',
DATE_FORMAT(IF(ISNULL(Ea.ultima_modificacion),NOW(),Ea.ultima_modificacion),"%d/%m/%Y") as "ultima_modificacion",
CONVERT(M.nombre USING utf8) as "Marca",
Ea.unidades_bulto,
'04/09/2010' as 'precio_desde',
IF(ISNULL(Ea.precio_venta),0,Ea.precio_venta) as 'precio_venta',
F.id_familia as categoria_de_producto,
'I' as 'ProductType',
-- 'E' as 'ProductType - Gasto',
-- 'R' as 'ProductType - Recurso',
-- 'S' as 'ProductType - Servicio',
-- classification es un mero agrupador, un caracter, de A - Z
IF(ISNULL(unidades_bulto*bultos_capa_palet*capas_palet),0,(unidades_bulto*bultos_capa_palet*capas_palet)) as 'UnitsPerPallet',
IF(ISNULL(Ea.precio_costo),0,Ea.precio_costo) as 'precio_costo',
IF(!Ca.nombre OR ISNULL(Ca.nombre),'',CONCAT('http://iempresa.biomundo/catalogo/',Ca.nombre)) as 'img_url',
CONCAT(Ea.id_almacen_logico,'-',Ea.planta,':',Ea.pasillo,':',Ea.fila,':',Ea.columna) as 'localizacion_defecto',
A.id_iva 
FROM Articulos A JOIN Empresas_articulos Ea ON (A.id_articulo=Ea.id_articulo AND Ea.id_empresa=1)
JOIN Marcas M on (M.id_marca=A.id_marca) JOIN Familia_articulos F ON (A.id_familia=F.id_familia)
LEFT JOIN Catalogo_imagenes Ca ON (A.id_imagen=Ca.id_imagen) 
WHERE Ea.id_empresa = 1 AND Ea.fecha_baja IS NULL
ORDER BY Ea.ultima_modificacion desc 
INTO OUTFILE '/Library/WebServer/Documents/planetdata/products.csv'
FIELDS TERMINATED BY '\t'
-- ENCLOSED BY '"'
LINES TERMINATED BY '\n'
