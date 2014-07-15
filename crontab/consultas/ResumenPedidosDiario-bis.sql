SELECT
DATE_SUB(NOW(),INTERVAL 1 DAY) as "Desde",NOW() as "Hasta",
COUNT(DISTINCT IF(!P.residual,P.id_pedido,0))-1 as "NPed IN",
ROUND(SUM(IF(!P.residual,I.bruto,0)),0) as "TotalBruto Pedido",
ROUND(SUM(IF(!P.residual,I.monto,0)),0) as "BaseImponible Pedido",
ROUND(SUM(IF(!P.residual,I.recargo_iva,0)),0) as "Impuestos Pedido",
ROUND(SUM(IF(!P.residual,I.recargo_equivalente,0)),0) as "RecargoImpuestos Pedido",
COUNT( DISTINCT IF(P.residual AND !PAnt.residual,P.id_pedido,0))-1 as "NPed Res. Puros",
ROUND(SUM(IF(P.residual AND !PAnt.residual,I.bruto,0)),0) as "TotalBruto Residual Puro",
ROUND(SUM(IF(P.residual AND !PAnt.residual,I.monto,0)),0) as "BaseImponible Residual Puro",
ROUND(SUM(IF(P.residual AND !PAnt.residual,I.recargo_iva,0)),0) as "Impuestos Residual Puro",
ROUND(SUM(IF(P.residual AND !PAnt.residual,I.recargo_equivalente,0)),0) as "RecargoImpuestos Residual Puro",
COUNT( DISTINCT IF(P.residual AND PAnt.residual,P.id_pedido,0))-1 as "NPed Res. Reincidentes",
ROUND(SUM(IF(P.residual AND PAnt.residual,I.bruto,0)),0) as "TotalBruto Residual Reincidente",
ROUND(SUM(IF(P.residual AND PAnt.residual,I.monto,0)),0) as "BaseImponible Residual Reincidente",
ROUND(SUM(IF(P.residual AND PAnt.residual,I.recargo_iva,0)),0) as "Impuestos Residual Reincidente",
ROUND(SUM(IF(P.residual AND PAnt.residual,I.recargo_equivalente,0)),0) as "RecargoImpuestos Residual Reincidente"
FROM Pedidos P JOIN IVAs I ON (I.id_pedido=P.id_pedido)
JOIN Pedidos PAnt ON (PAnt.id_pedido_incompleto=P.id_pedido)
WHERE (P.id_proveedor = 0 OR P.id_proveedor IS NULL) AND
P.fecha between DATE_SUB('2005-10-11',INTERVAL 1 DAY) 
and '2005-10-11 23:59:59'
