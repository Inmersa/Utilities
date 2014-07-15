SELECT A.numero, A.nombre as "Asiento",A.saldo_debe as "Debe" ,A.saldo_haber as "Haber",A.saldo as "Saldo",
A.fecha_apertura as "Fecha", Ej.nombre as "Ejercicio", E.razon_social as "Empresa"         
FROM Asiento A JOIN Ejercicios Ej ON (Ej.id_ejercicio=A.id_ejercicio) JOIN Empresas E ON (Ej.id_empresa=E.id_empresa)
WHERE saldo_debe != saldo_haber 
ORDER BY Ej.id_empresa, Ej.fecha_inicio asc
