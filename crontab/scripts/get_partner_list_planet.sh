echo "Borrando el csv actual ... "
ssh root@bbdd05.biomundo -C "rm /Library/WebServer/Documents/planetdata/customers.csv"
echo -n "lanzando query  "
cat query-export-customers-planet.sql | mysql -u mysql -p34tkote -P 3306 -h bbdd05.biomundo planet_gestion
echo "ok"
#echo "recuperando la lista .. "
#scp root@bbdd4.biomundo:/tmp/customers.csv customers_planet.csv

### POST Importacion de PRODUCTOS
# update m_product set c_taxcategory_id = '7E3FAAFEDFDB403B8416C289158D1BB1' WHERE classification = '3';
# update m_product set c_taxcategory_id = '583950C2E15C4B5CAD5CC8AA8C41572A' WHERE classification = '2';
# update m_product set c_taxcategory_id = 'ED0819D968444B49AA1BAF0FCDBB7950' WHERE classification = '1';
# update m_product set c_taxcategory_id = 'CDFBA09C36874F31A9D5DCFBA1E14E6B' WHERE classification = '5';
# update m_product set c_taxcategory_id = '583950C2E15C4B5CAD5CC8AA8C41572A' WHERE classification = '0';
