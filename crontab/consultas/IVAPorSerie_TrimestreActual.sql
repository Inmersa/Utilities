SELECT S.nombre as "Serie",Ti.nombre as "Nombre Impuesto",  
ROUND(SUM(IF(I.recargo_equivalente!=0,0,I.monto)),2) as "BASE I Sin Re", 
Ti.porcentaje as "% IVA", 
ROUND(SUM(IF(I.recargo_equivalente!=0,0,I.recargo_iva)),2) as "Cuota I Sin Re", 
Ti.recargo_equivalente as "% RE *", 
ROUND(SUM(IF(I.recargo_equivalente!=0,0,I.recargo_equivalente)),2) as "C. Re *", 
ROUND(SUM(IF(I.recargo_equivalente!=0,0,I.recargo_iva)) + SUM(IF(I.recargo_equivalente!=0,0,I.recargo_equivalente)),2) as "Total Iva+RE Sin Re *", 
ROUND(SUM(IF(I.recargo_equivalente=0,0,I.monto)),2) as "BASE I con Re", 
Ti.porcentaje as "% IVA", 
ROUND(SUM(IF(I.recargo_equivalente=0,0,I.recargo_iva)),2) as "Cuota Iva con Re", 
Ti.recargo_equivalente as "% RE", 
ROUND(SUM(IF(I.recargo_equivalente=0,0,I.recargo_equivalente)),2) as "C. Re", 
ROUND(SUM(IF(I.recargo_equivalente=0,0,I.recargo_iva)) + SUM(IF(I.recargo_equivalente=0,0,I.recargo_equivalente)),2) as "Total Iva+Re con Re" 
FROM Facturas F JOIN IVAs I ON (I.id_factura=F.id_factura) JOIN Tipos_IVA Ti ON (I.id_iva=Ti.id_iva) JOIN Series_facturacion S ON (F.id_serie=S.id_serie) 
WHERE F.fecha between 
CONCAT(DATE_FORMAT(NOW(),'%Y'),'-',((FLOOR((DATE_FORMAT(NOW(),'%m')-1)/3)+1) *3 - 2),'-','00') AND 
CONCAT(DATE_FORMAT(NOW(),'%Y'),'-',(FLOOR((DATE_FORMAT(NOW(),'%m')-1)/3)+1) *3,'-','31 23:59:59') 
GROUP BY S.id_serie,Ti.id_iva ORDER BY S.ventas desc,S.nombre,Ti.nombre
