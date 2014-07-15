SELECT A.id_articulo,A.nombre as "Articulo", M.nombre as "Marca", ROUND(SUM(Ld.cantidad),0) as "Cantidad Pedida",ROUND(SUM(Ld.monto_total),0) as "Importe"
FROM Lineas_detalle Ld JOIN Articulos A ON (Ld.id_articulo=A.id_articulo)
JOIN Marcas M ON (A.id_marca=M.id_marca)
JOIN Pedidos P ON (Ld.id_pedido=P.id_pedido)
LEFT JOIN Albaranes Al ON (P.id_pedido=Al.id_pedido)
WHERE Al.id_pedido IS NULL and 
P.fecha >= DATE_SUB('2005-10-11',INTERVAL 1 DAY) AND P.fecha <= '2005-10-11 23:59:59'
AND (P.id_proveedor = 0 OR P.id_proveedor IS NULL) AND P.residual > 0
GROUP BY A.id_articulo
ORDER BY M.nombre,A.nombre
