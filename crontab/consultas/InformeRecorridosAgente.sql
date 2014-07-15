SELECT C.id_cliente, C.razon_social as "RazonSocial", R.id_agente as id_ag,
A.nombre as Agente, R.id_recorrido, R.id_ruta, Rt.nombre as Nombre_Ruta, R.id_medio_cto, Mc.nombre as Medio_cto, R.fecha as F_recorrido, R.id_dia, D.nombre as Dia_Sem, 
DATE_FORMAT(R.fecha,'%d') as Dia, DATE_FORMAT(R.fecha,'%m') as Mes, DATE_FORMAT(R.fecha,'%Y') as Anyo, R.h_inicio, R.h_fin, 
IF(R.observaciones IS NULL,'',R.observaciones) as Observ_recorrido, 
IF(R.prox_fecha IS NULL,'',R.prox_fecha) AS Prox_F_recorrido, Ct.id_cita, IF(Ct.id_pedido IS NULL,'',Ct.id_pedido) as id_pedido, IF(Ct.visitado=0,'NO','SI') as Visitado,
IF(Ct.observaciones IS NULL,'',Ct.observaciones) as Observ_cita, IF(Ct.prox_fecha IS NULL,'',Ct.prox_fecha) as Prox_cita,
IF(Ct.prox_id_medio_cto IS NULL,'',Mc.nombre) as Prox_medio_cto, IF(Ct.prox_comentario IS NULL,'',Ct.prox_comentario) AS Prox_cita_cometario
FROM Citas Ct LEFT JOIN Recorridos R ON (R.id_recorrido=Ct.id_recorrido) LEFT JOIN Agentes A ON (R.id_agente=A.id_agente) LEFT JOIN Clientes C ON (Ct.id_cliente=C.id_cliente)
LEFT JOIN Rutas Rt ON (Rt.id_ruta=R.id_ruta) LEFT JOIN Medios_contacto Mc ON (Mc.id_medio_cto=Ct.id_medio_cto) LEFT JOIN Dias D ON (D.id_dia=R.id_dia)
WHERE A.id_empresa=1 
AND R.fecha= DATE_SUB(CURDATE(),INTERVAL 1 DAY)


