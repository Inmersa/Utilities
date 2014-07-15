
DELETE FROM planet_gestion.Articulos;
INSERT INTO `planet_gestion`.`Articulos` SELECT * FROM `biomundo_gestion`.`Articulos`;

DELETE FROM planet_gestion.Empresas_articulos;
INSERT INTO `planet_gestion`.`Empresas_articulos` SELECT * FROM `biomundo_gestion`.`Empresas_articulos`;

DELETE FROM planet_gestion.Marcas;
INSERT INTO `planet_gestion`.`Marcas` SELECT * FROM `biomundo_gestion`.`Marcas` WHERE id_marca = 0;
UPDATE `planet_gestion`.`Marcas` set id_marca=0 where id_marca=LAST_INSERT_ID();
INSERT INTO `planet_gestion`.`Marcas` SELECT * FROM `biomundo_gestion`.`Marcas` WHERE id_marca != 0;

DELETE FROM planet_gestion.Localizacion_articulos;
INSERT INTO `planet_gestion`.`Localizacion_articulos` SELECT * FROM `biomundo_gestion`.`Localizacion_articulos`;

DELETE FROM planet_gestion.Compra_articulos;
INSERT INTO `planet_gestion`.`Compra_articulos` SELECT * FROM `biomundo_gestion`.`Compra_articulos`;

REPLACE INTO planet_gestion.Compra_articulos 
(id_articulo,id_proveedor,precio,PV_oficial,PVP_oficial,referencia)
SELECT Ea.id_articulo,1,Ea.precio_standard,Ea.precio_standard,Ea.precio_venta,Ea.id_articulo 
FROM biomundo_gestion.Empresas_articulos Ea WHERE Ea.fecha_baja IS NULL AND Ea.id_empresa = 1;

UPDATE planet_gestion.Marcas SET wwwactivo = 0 WHERE id_marca = 0 OR id_marca = 1 OR
id_marca = 33 OR id_marca = 36 OR id_marca = 38 OR id_marca = 53 OR
id_marca = 56 OR id_marca = 71 OR id_marca = 80 OR id_marca = 81 OR
id_marca = 100 OR id_marca = 101 OR id_marca = 103 OR id_marca = 108 OR
id_marca = 114 OR id_marca = 118 OR id_marca = 172 OR id_marca = 173;

