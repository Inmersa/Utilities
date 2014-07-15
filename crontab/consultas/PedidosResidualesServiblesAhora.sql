
SELECT P.referencia,P.fecha,
#SUM(I.monto) as "BaseImponible",
C.razon_social,D.nombre
FROM Pedidos P LEFT JOIN Pedidos_facturas PF ON (P.id_pedido=PF.id_pedido)
JOIN Direcciones_entrega D ON (P.id_direccion=D.id_direccion) JOIN Clientes C ON (D.id_cliente=C.id_cliente)
#JOIN IVAs I ON (I.id_pedido=P.id_pedido) 
JOIN Lineas_detalle Ld ON (P.id_pedido=Ld.id_pedido)
WHERE PF.id_pedido IS NULL AND P.fecha >= DATE_SUB(NOW(),INTERVAL 20 DAY) AND
P.residual = 1 AND Ld.id_articulo IN (
SELECT Ld.id_articulo
FROM Albaranes A JOIN Detalles_albaran Da ON (Da.id_albaran=A.id_albaran)
JOIN Lineas_detalle Ld ON (Da.id_detalle=Ld.id_detalle)
WHERE A.fecha between DATE_SUB(DATE_SUB(NOW(),INTERVAL 10 HOUR ),INTERVAL 10 MINUTE) AND NOW()
)
#GROUP BY P.id_pedido
Tiempo:

SELECT P.referencia,P.fecha
FROM Pedidos P LEFT JOIN Pedidos_facturas PF ON (P.id_pedido=PF.id_pedido)
JOIN Lineas_detalle Ld ON (P.id_pedido=Ld.id_pedido)
WHERE P.residual = 1 AND P.fecha >= DATE_SUB(NOW(),INTERVAL 20 DAY) AND
PF.id_pedido IS NULL AND Ld.id_articulo IN (
SELECT Ld.id_articulo
FROM Albaranes A JOIN Detalles_albaran Da ON (Da.id_albaran=A.id_albaran)
JOIN Lineas_detalle Ld ON (Da.id_detalle=Ld.id_detalle)
WHERE A.fecha between DATE_SUB(DATE_SUB(NOW(),INTERVAL 10 HOUR ),INTERVAL 10 MINUTE) AND NOW()
)
Tiempo:

SELECT P.referencia,P.fecha
FROM Pedidos P LEFT JOIN Pedidos_facturas PF ON (P.id_pedido=PF.id_pedido)
JOIN Lineas_detalle Ld ON (P.id_pedido=Ld.id_pedido)
WHERE P.residual = 1 AND P.fecha >= DATE_SUB(NOW(),INTERVAL 20 DAY) AND
PF.id_pedido IS NULL AND Ld.id_articulo = 1691
Tiempo: 0.95

SELECT P.referencia,P.fecha,C.razon_social,D.nombre
FROM Pedidos P LEFT JOIN Pedidos_facturas PF ON (P.id_pedido=PF.id_pedido)
JOIN Direcciones_entrega D ON (P.id_direccion=D.id_direccion) JOIN Clientes C ON (D.id_cliente=C.id_cliente)
JOIN Lineas_detalle Ld ON (P.id_pedido=Ld.id_pedido)
WHERE P.residual = 1 AND P.fecha >= DATE_SUB(NOW(),INTERVAL 20 DAY) AND
PF.id_pedido IS NULL AND Ld.id_articulo = 2021
Tiempo: 1.92



