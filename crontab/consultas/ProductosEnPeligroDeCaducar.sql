SELECT A.id_articulo as "Ref",A.nombre,CONCAT(A.garantia,' Dias') as "Vida" ,M.nombre as "Marca",Al.nombre as "Zona Alm",
L.fecha_caducidad as "Cad.",ROUND(L.cantidad) as "Uds",L.planta,L.pasillo,L.columna,L.fila 
FROM Localizacion_articulos L JOIN Almacenes_logicos Al ON (L.id_almacen_logico=Al.id_almacen_logico) 
JOIN Articulos A ON (L.id_articulo=A.id_articulo) JOIN Marcas M ON (M.id_marca=A.id_marca) 
JOIN Empresas_articulos EA ON (A.id_articulo=EA.id_articulo AND EA.id_empresa = 1) 
WHERE EA.fecha_baja IS NULL AND L.fecha_caducidad != 0 AND L.fecha_caducidad <= DATE_ADD(NOW(),INTERVAL (A.garantia*0.5) DAY) AND L.cantidad > 0
ORDER BY L.fecha_caducidad asc,Al.nombre,M.nombre,A.nombre
