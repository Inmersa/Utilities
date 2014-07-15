SELECT
DATE_SUB(NOW(),INTERVAL 1 DAY) as "Desde",NOW() as "Hasta",
COUNT(DISTINCT IF(!P.residual,P.id_pedido,0))-1 as "NPed IN",
ROUND(SUM(IF(!P.residual,I.bruto,0)),0) as "TotalBruto Pedido",
ROUND(SUM(IF(!P.residual,I.monto,0)),0) as "BaseImponible Pedido",
ROUND(SUM(IF(!P.residual,I.recargo_iva,0)),0) as "Impuestos Pedido",
ROUND(SUM(IF(!P.residual,I.recargo_equivalente,0)),0) as "RecargoImpuestos Pedido",
COUNT( DISTINCT IF(P.residual,P.id_pedido,0))-1 as "NPed Res",
ROUND(SUM(IF(P.residual,I.bruto,0)),0) as "TotalBruto Residual",
ROUND(SUM(IF(P.residual,I.monto,0)),0) as "BaseImponible Residual",
ROUND(SUM(IF(P.residual,I.recargo_iva,0)),0) as "Impuestos Residual",
ROUND(SUM(IF(P.residual,I.recargo_equivalente,0)),0) as "RecargoImpuestos Residual"
FROM Pedidos P JOIN IVAs I ON (I.id_pedido=P.id_pedido)
WHERE (P.id_proveedor = 0 OR P.id_proveedor IS NULL) AND
P.fecha between DATE_SUB(NOW(),INTERVAL 1 DAY) and NOW()
