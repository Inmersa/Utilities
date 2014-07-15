#ACTUALIZAR Pedidos PS a pedidos residuales

UPDATE `Pedidos` SET residual=1 WHERE `referencia_externa` LIKE '%ps%' AND `fecha` >= '2013-09-01';
UPDATE `Pedidos` SET residual=1 WHERE `referencia_externa` LIKE '%residual%' AND `fecha` >= '2013-09-01';
