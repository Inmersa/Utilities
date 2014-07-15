SELECT
COUNT(DISTINCT F.id_cliente) as "Numero de clientes activos para el mes en curso"
FROM Facturas F
WHERE F.fecha between
CONCAT(DATE_FORMAT(NOW(),'%Y'),'-',FLOOR(DATE_FORMAT(NOW(),'%m')+0),'-','00') AND
CONCAT(DATE_FORMAT(NOW(),'%Y'),'-',FLOOR(DATE_FORMAT(NOW(),'%m')+1),'-','00 00:00:00')
AND F.id_cliente >= 0
