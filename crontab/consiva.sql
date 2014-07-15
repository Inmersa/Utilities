SELECT S.nombre as "Serie",Ti.nombre as "Nombre Impuesto",  
SUM(IF(I.recargo_equivalente!=0,0,I.monto)) as "BASE I Sin Re", 
Ti.porcentaje as "% IVA", 
SUM(IF(I.recargo_equivalente!=0,0,I.recargo_iva)) as "Cuota I Sin Re", 
Ti.recargo_equivalente as "% RE *", 
SUM(IF(I.recargo_equivalente!=0,0,I.recargo_equivalente)) as "C. Re *", 
SUM(IF(I.recargo_equivalente!=0,0,I.recargo_iva)) + SUM(IF(I.recargo_equivalente!=0,0,I.recargo_equivalente)) as "Total Iva+RE Sin Re *", 
SUM(IF(I.recargo_equivalente=0,0,I.monto)) as "BASE I con Re", 
Ti.porcentaje as "% IVA", 
SUM(IF(I.recargo_equivalente=0,0,I.recargo_iva)) as "Cuota Iva con Re", 
Ti.recargo_equivalente as "% RE", 
SUM(IF(I.recargo_equivalente=0,0,I.recargo_equivalente)) as "C. Re", 
SUM(IF(I.recargo_equivalente=0,0,I.recargo_iva)) + SUM(IF(I.recargo_equivalente=0,0,I.recargo_equivalente)) as "Total Iva+Re con Re" 
FROM Facturas F JOIN IVAs I ON (I.id_factura=F.id_factura) JOIN Tipos_IVA Ti ON (I.id_iva=Ti.id_iva) JOIN Series_facturacion S ON (F.id_serie=S.id_serie) 
WHERE F.fecha between "2006-01-00 00:00:00" and "2006-03-31 23:59:59"
GROUP BY S.id_serie,Ti.id_iva ORDER BY S.ventas desc,S.nombre,Ti.nombre
