INSERT INTO Citas (id_cita,id_recorrido,id_cliente,id_medio_cto,id_pedido,h_inicio,h_fin_sys,h_fin_ag)
SELECT NULL,R.id_recorrido,D.id_cliente,6,P.id_pedido,TIME(P.fecha),TIME(P.fecha),TIME(P.fecha)
FROM Pedidos P JOIN Direcciones_entrega D ON (P.id_direccion=D.id_direccion), Recorridos R
WHERE D.id_cliente = 1571
AND P.fecha >= DATE_FORMAT(NOW(),"%Y-%m-%d") AND P.fecha <= DATE_FORMAT(NOW(),"%Y-%m-%d 23:59")
AND R.id_agente = 1 AND R.fecha = NOW()
ORDER BY P.fecha asc;
