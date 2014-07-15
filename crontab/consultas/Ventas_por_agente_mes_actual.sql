SELECT 
SF.id_serie as SF_id_serie, SF.nombre as SF_Serie, ME.num as NumMes, ME.nombre as Mes, AN.id_anyo, AN.numero as Anyo, 
AG.id_agente as Cli_id_ag, AG.nombre as Agente,
ROUND(SUM(IF(F.id_serie=6,-1*F.total_bruto,F.total_bruto)),2) as Total_bruto, 
ROUND(SUM(IF(F.id_serie=6,-1*F.descuento,F.descuento)),2) as Total_dto,
ROUND(SUM(IF(F.id_serie=6,-1*F.base_imponible,F.base_imponible)),2) as Total_Base_Imponible,
ROUND(SUM(IF(F.id_serie=6,-1*F.total_impuestos,F.total_impuestos)),2) as Total_impuestos,
ROUND(SUM(IF(F.id_serie=6,-1*F.monto_total,F.monto_total)),2) as Total_factura
FROM Series_facturacion SF LEFT JOIN Facturas F ON (SF.id_serie=F.id_serie) LEFT JOIN Dias DI ON(DATE_FORMAT(F.fecha,'%Y-%m-%d')=DI.fecha) LEFT JOIN Semanas SE ON(DI.id_semana=SE.id_semana)
LEFT JOIN Meses ME ON(DI.id_mes=ME.id_mes) LEFT JOIN Anyos AN ON(ME.id_anyo=AN.id_anyo) 
LEFT JOIN Clientes C ON(C.id_cliente=F.id_cliente) LEFT JOIN Clientes_empresas CE ON(C.id_cliente=CE.id_cliente) LEFT JOIN Agentes AG ON(F.id_agente=AG.id_agente)
WHERE 
SF.ventas=1
AND F.id_serie!=4
AND F.id_serie!=20
#AND F.fecha >= "2014-06-01" AND F.fecha < "2014-07-00"
AND F.fecha between
CONCAT(DATE_FORMAT(NOW(),'%Y'),'-',FLOOR(DATE_FORMAT(NOW(),'%m')+0),'-','00') AND
CONCAT(DATE_FORMAT(NOW(),'%Y'),'-',FLOOR(DATE_FORMAT(NOW(),'%m')+1),'-','00 00:00:00')
GROUP BY SF.id_serie,F.id_agente ORDER BY SF.id_serie desc, Ag.nombre asc, C.nombre
