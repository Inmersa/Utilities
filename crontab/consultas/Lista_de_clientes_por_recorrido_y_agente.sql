SELECT C.id_cliente as "data[id_cliente]", C.razon_social as "RazonSocial",
A.email as email 
FROM Agentes A JOIN Recorridos R ON (R.id_agente=A.id_agente) JOIN Citas Ct ON (R.id_recorrido=Ct.id_recorrido) JOIN Clientes C ON (Ct.id_cliente=C.id_cliente)
WHERE A.email is not null 
AND R.fecha = DATE_SUB(CURDATE(),INTERVAL 1 DAY)
