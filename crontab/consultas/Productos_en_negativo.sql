select L.id_articulo as "data[id_articulo]",
7 as "data[num_dias]", SUM(L.cantidad) as "Stock", A.nombre as "Nombre"
FROM Localizacion_articulos L JOIN Empresas_articulos Ea ON (L.id_articulo=Ea.id_articulo) JOIN Articulos A ON (L.id_articulo=A.id_articulo)
WHERE Ea.fecha_baja IS NULL 
GROUP BY L.id_articulo HAVING Stock < 0
