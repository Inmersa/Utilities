SELECT L.id_articulo,A.nombre,M.nombre as "Marca",
DATE_FORMAT(L.fecha_caducidad,'%d/%m/%Y %H:%i') as "Fecha Caducidad",
L.cantidad as "Cantidad",
CONCAT(AL.nombre,"-> P:",L.planta," Ps:",L.pasillo," C:",L.columna," F:",L.fila) as "Localizacion",
DATE_FORMAT(L.fecha_alta,'%d/%m/%Y %H:%i') as "Fecha Alta"
FROM Localizacion_articulos L JOIN Articulos A ON (L.id_articulo=A.id_articulo) JOIN Almacenes_logicos AL ON (L.id_almacen_logico=AL.id_almacen_logico)
JOIN Marcas M ON (A.id_marca=M.id_marca)
WHERE L.id_articulo IN (
select L.id_articulo 
FROM Localizacion_articulos L JOIN Empresas_articulos Ea ON (L.id_articulo=Ea.id_articulo) 
WHERE Ea.fecha_baja IS NULL 
AND L.cantidad < 0
) ORDER BY M.nombre,L.id_articulo,L.cantidad asc,L.planta,L.pasillo,L.columna,L.fila
