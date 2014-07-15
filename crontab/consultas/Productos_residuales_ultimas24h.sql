SELECT A.id_articulo AS "Ref.", A.nombre AS  "Articulo", M.nombre AS  "Marca", ROUND( SUM( Ld.cantidad ) , 0  )  AS  "Uds_ped",
ROUND( SUM( Ld.monto_total ) , 0  )  AS  "Euros", ROUND(SUM(La.cantidad),0) AS  "Stock"
FROM Pedidos P JOIN Lineas_detalle Ld ON ( Ld.id_pedido = P.id_pedido )
JOIN Articulos A ON ( Ld.id_articulo = A.id_articulo )
JOIN Localizacion_articulos La ON ( La.id_articulo = A.id_articulo )
JOIN Marcas M ON ( A.id_marca = M.id_marca )
LEFT  JOIN Albaranes Al ON ( P.id_pedido = Al.id_pedido )
WHERE Al.id_pedido IS  NULL  AND
P.fecha >= DATE_SUB( NOW(  ) ,  INTERVAL 1 DAY  )
AND ( P.id_proveedor =0 OR P.id_proveedor IS  NULL  ) AND P.residual >0
GROUP  BY A.id_articulo
ORDER  BY M.nombre, A.nombre;
