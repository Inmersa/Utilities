SELECT STRAIGHT_JOIN 
P.referencia as "Referencia de Pedido",P.fecha as "Fecha de Pedido",C.razon_social as "Cliente",
D.nombre as "Nombre De Direccion", A.id_articulo as "ID Articulo" ,A.nombre as "Articulo" ,M.nombre as "Marca",
ROUND(Ld.cantidad) as "Falta", SUM(L.cantidad) as "Existencias"
FROM Pedidos P JOIN Lineas_detalle Ld ON (P.id_pedido=Ld.id_pedido)
JOIN Articulos A ON (Ld.id_articulo=A.id_articulo)
JOIN Marcas M ON (A.id_marca=M.id_marca)
JOIN Localizacion_articulos L ON (L.id_articulo=A.id_articulo)
LEFT JOIN Pedidos_facturas PF ON (P.id_pedido=PF.id_pedido)
JOIN Direcciones_entrega D ON (P.id_direccion=D.id_direccion)
JOIN Clientes C ON (C.id_cliente=D.id_cliente)
WHERE P.fecha >= DATE_SUB(NOW(),INTERVAL 1 MONTH) AND P.residual > 0 AND L.cantidad != 0 AND PF.id_factura IS NULL AND P.preparado = 0
GROUP BY Ld.id_detalle
HAVING Existencias > 0
ORDER BY C.razon_social,P.fecha asc
