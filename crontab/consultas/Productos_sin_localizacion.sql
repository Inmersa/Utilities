SELECT A.id_articulo, A.nombre, M.nombre as "Marca"
FROM Empresas_articulos Ea JOIN Articulos A ON (Ea.id_articulo=A.id_articulo)
LEFT JOIN Localizacion_articulos La ON (La.id_articulo=A.id_articulo) 
JOIN Marcas M ON (A.id_marca=M.id_marca)
WHERE La.id_articulo IS NULL AND Ea.id_empresa = 1 AND Ea.fecha_baja IS NULL
