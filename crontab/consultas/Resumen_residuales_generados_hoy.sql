SELECT DATE_SUB(NOW(),INTERVAL 1 DAY) as "Desde",NOW() as "Hasta", 
COUNT(DISTINCT P.id_pedido) as "N Ped",
ROUND(SUM(I.bruto),0) as "TotalBruto",
ROUND(SUM(I.monto),0) as "BaseImponible",
ROUND(SUM(I.recargo_iva),0) as "Impuestos",
ROUND(SUM(I.recargo_equivalente),0) as "RecargoImpuestos"
FROM Pedidos P JOIN IVAs I ON (I.id_pedido=P.id_pedido)
WHERE P.fecha >= DATE_SUB(NOW(),INTERVAL 1 DAY)
AND (P.id_proveedor = 0 OR P.id_proveedor IS NULL) AND P.residual > 0
