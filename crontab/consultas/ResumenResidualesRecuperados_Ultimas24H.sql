SELECT 
MIN(P.fecha) as "F Primera",
MAX(P.fecha) as "F Ultima",
COUNT(DISTINCT P.id_pedido) as "NumPedidos",
ROUND(SUM(Ld.monto_total),2) as "Bruto",
COUNT(DISTINCT F.id_factura) as "NumFras",
ROUND(SUM(Fd.importe),2) as "BrutoFra",
MIN(IF(MONTH(F.fecha)=MONTH(P.fecha),P.fecha,NULL)) as "F Primera Mes",
MAX(IF(MONTH(F.fecha)=MONTH(P.fecha),P.fecha,NULL)) as "F Ultima Mes",
COUNT(DISTINCT IF(MONTH(F.fecha)=MONTH(P.fecha),P.id_pedido,0))-1 as "NumPedidos Mes",
ROUND(SUM(IF(MONTH(F.fecha)=MONTH(P.fecha),Ld.monto_total,0)),2) as "Bruto Mes",
COUNT(DISTINCT IF(MONTH(F.fecha)=MONTH(P.fecha),F.id_factura,0))-1 as "NumFras Mes",
ROUND(SUM(IF(MONTH(F.fecha)=MONTH(P.fecha),Fd.importe,0)),2) as "BrutoFra Mes",
MIN(IF(MONTH(F.fecha)!=MONTH(P.fecha),P.fecha,NULL)) as "F Primera Anterior",
MAX(IF(MONTH(F.fecha)!=MONTH(P.fecha),P.fecha,NULL)) as "F Ultima Anterior",
COUNT(DISTINCT IF(MONTH(F.fecha)!=MONTH(P.fecha),P.id_pedido,0))-1 as "NumPedidos Anterior",
ROUND(SUM(IF(MONTH(F.fecha)!=MONTH(P.fecha),Ld.monto_total,0)),2) as "Bruto Anterior",
COUNT(DISTINCT IF(MONTH(F.fecha)!=MONTH(P.fecha),F.id_factura,0))-1 as "NumFras Anterior",
COUNT(DISTINCT F.id_cliente) as "NumClientes",
ROUND(SUM(IF(MONTH(F.fecha)!=MONTH(P.fecha),Fd.importe,0)),2) as "BrutoFra Anterior"
FROM Facturas F JOIN Facturas_detalle Fd ON (Fd.id_factura=F.id_factura)
JOIN Lineas_detalle Ld ON (Ld.id_detalle=Fd.id_detalle)
JOIN Pedidos P ON (Ld.id_pedido=P.id_pedido)
LEFT JOIN Pedidos PAnt ON (P.id_pedido=PAnt.id_pedido_incompleto)
WHERE F.fecha >= DATE_SUB(NOW(),INTERVAL 1 DAY)
AND (F.id_proveedor = 0 OR F.id_proveedor IS NULL) AND P.residual > 0
