#SELECT A.id_articulo as "ID Articulo", A.nombre as "Producto", M.nombre as "Marca",
#P.nombre as "Nombre", P.cantidad as "Cant Minima"
#FROM Promociones P JOIN Articulos A ON (P.id_articulo=A.id_articulo)
#JOIN Marcas M ON (M.id_marca=A.id_marca)
#WHERE P.fecha_inicio <= DATE_ADD(NOW(),INTERVAL 5 DAY) AND P.fecha_fin >=  DATE_ADD(NOW(),INTERVAL 5 DAY)
SELECT A.id_articulo as "Referencia", A.codigo_barras, A.nombre as "Producto", M.nombre as "Marca", TRUNCATE((EA.precio_6),2) as "PVP sin iva", TI.nombre as "Tipo_Iva", TRUNCATE((EA.precio_6 + EA.precio_6 * TI.porcentaje/100),2) as "PVP rec",
P.id_promocion as "id_promo",P.nombre as "Promocion", ROUND(P.cantidad) as "Cant Minima", P.descuento, P.fecha_fin, P.monto 
FROM Promociones P JOIN Articulos A ON (P.id_articulo=A.id_articulo)
JOIN Marcas M ON (M.id_marca=A.id_marca)
JOIN Empresas_articulos EA ON (A.id_articulo=EA.id_articulo) JOIN Tipos_IVA TI ON (A.id_iva=TI.id_iva)
WHERE P.fecha_inicio <= DATE_SUB(CURDATE(),INTERVAL 1 DAY) AND P.fecha_fin >=  DATE_ADD(NOW(),INTERVAL 1 DAY)

