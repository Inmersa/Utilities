SELECT
IF(F.id_serie=0,1,F.id_serie) as A_tipo_documento,
SUBSTRING(F.referencia,4) as B_NUM_factura,
 F.referencia as C_referencia, DATE_FORMAT(F.fecha,'%d/%m/%Y') as D_fecha, '0' as E_estado, 'GEN' AS F_Almacen, F.id_agente as G_agente, ' ' as H_cod_prov, F.id_cliente as I_id_cliente, C.razon_social AS J_razon_social, C.direccion_facturacion as K_domicilio, C.poblacion as L_poblacion, C.cp as M_cpostal, PR.nombre as N_provincia, C.cif as O_NIF,
IF(TC.aplicar_iva=1,0,1) as P_TipoIva,
IF(TC.aplicar_recargo=1,1,0) as Q_RE,
C.telefono1 as R_telefono,
ROUND(SUM(IF(IV.id_iva=1,IV.monto,0)),2) as S_importe_neto_1,
ROUND(SUM(IF(IV.id_iva=7,IV.monto,0)),2) as T_importe_neto_2,
ROUND(SUM(IF(IV.id_iva=8,IV.monto,0)),2) as U_importe_neto_3,
ROUND(((F.descuento/F.total_bruto)*100),2) as V_porcentaje_dto_1,
'' as W_porc_dto_2, ' ' as X_porc_dto_3,
F.descuento as Y_importe_dto_1, ' ' as Z_importe_dto_2, ' ' as AA_importe_dto_3,
'' as AB_porc_dtopp_1, ' ' as AC_porc_dtoPP_2, ' ' as AD_porc_dtoPP_3,
'' as AE_importe_dtopp_1, ' ' as AF_importe_dtopp_2, ' ' as AG_importe_dtopp_3,
' ' as AH_porc_portes_1, ' ' as AI_porc_portes_2, ' ' as AI_porc_portes_3, ' ' as AK_imp_portes_1, ' ' as AL_imp_portes_2, ' ' as AM_imp_portes_3,
' ' as AN_porc_financ_1, ' ' as AO_porc_financ_2, ' ' as AP_porc_financ_3, ' ' as AQ_imp_financ_1, ' ' as AR_imp_financ_2, ' ' as AS_imp_financ_3,
ROUND(SUM(IF(IV.id_iva=1,IV.monto,0)),2) as AT_BaseImp_1,
ROUND(SUM(IF(IV.id_iva=7,IV.monto,0)),2) as AU_BaseImp_2,
ROUND(SUM(IF(IV.id_iva=8,IV.monto,0)),2) as AV_BaseImp_3,
ROUND(SUM(IF(IV.id_iva=1,'4,00',0)),2) as AW_porcentajeIVA_1,
ROUND(SUM(IF(IV.id_iva=7,'10,00',0)),2) as AX_porcentajeIVA_2,
ROUND(SUM(IF(IV.id_iva=8,'21,00',0)),2) as AY_porcentajeIVA_3,
ROUND(SUM(IF(IV.id_iva=1,IV.recargo_iva,0)),2) as AZ_ImporteIVA_1,
ROUND(SUM(IF(IV.id_iva=7,IV.recargo_iva,0)),2) as BA_ImporteIVA_2,
ROUND(SUM(IF(IV.id_iva=8,IV.recargo_iva,0)),2) as BB_ImporteIVA_3,
ROUND(SUM(IF(IV.id_iva=1,'0.50',0)),2) as BC_porcentajeRE_1,
ROUND(SUM(IF(IV.id_iva=7,'1.40',0)),2) as BD_porcentajeRE_2,
ROUND(SUM(IF(IV.id_iva=8,'5.20',0)),2) as BF_porcentajeRE_3,
ROUND(SUM(IF(IV.id_iva=1,IV.recargo_equivalente,0)),2) as BF_importeRE_1,
ROUND(SUM(IF(IV.id_iva=7,IV.recargo_equivalente,0)),2) as BG_importeRE_2,
ROUND(SUM(IF(IV.id_iva=8,IV.recargo_equivalente,0)),2) as BH_importeRE_3,
IF(F.retenido>0,F.retenido/F.base_imponible,0) as BI_porc_retencion, F.retenido as BJ_imp_retencion,
ROUND(F.monto_total,2) as BK_total, F.id_forma_pago as BL_id_forma_pago, '0' as BM_portes, 'Pagados' as BN_texto_portes, F.referencia_externa as BO_observ_linea_1, ' ' as BP_observ_linea_2, ' ' as QB_obra, ' ' as BR_remitido_por, ' ' as BS_embalado_por, ' ' as BT_att,
F.referencia as BU_referencia, ' '  as BV_num_de_su_pedido, DATE_FORMAT(F.fecha,'%d/%m/%Y') as BW_fecha_de_su_pedido, 0 as BX_cobrado,  1 as BY_tipo_creacion, ' '  as BZ_tipo_de_recibo, ' ' as CA_cod_recibo, 0 as CB_traspasado, F.id_factura as CC_anot_priv_id_fra, ' ' as CD_doc_ext_asociados, 'N' as CE_impresa, ' ' as CF_cod_banco_cli, DATE_FORMAT(F.fecha,'%H:%i') as CG_hora, F.notas as CH_notas, ' ' as CI_usr_creacion_doc, ' ' as CJ_usr_modif_doc, C.fax as CK_fax, ' ' as CL_imagen,
ROUND(SUM(IF(IV.id_iva=5,IV.monto,0)),2) as CM_imp_neto_exento, ' ' as CN_porc_dto_exento, ' ' as CO_imp_dto_exento, ' ' as CP_porc_pp_exento, ' ' as CQ_import_pp_exento, ' ' as CR_porc_portes_exento, ' ' as CS_imp_portes_exento, ' ' as CT_porc_financ_exento, ' ' as CU_imp_financ_exento, ROUND(SUM(IF(IV.id_iva=5,IV.monto,0)),2) as CV_base_imp_exenta, 0 as CW_enviado_email, ' ' as CX_permisos_doc, ' ' as CY_ticket_porc_dto, ' ' as CZ_ticket_imp_dto, ' ' as DA_caja_creacion_doc
FROM ivas IV LEFT JOIN facturas F ON (IV.id_factura=F.id_factura)
LEFT JOIN clientes C ON(F.id_cliente=C.id_cliente) LEFT JOIN clientes_empresas CE ON(C.id_cliente=CE.id_cliente)
LEFT JOIN Tipo_cliente TC ON(TC.id_tipo_cliente=CE.id_tipo_cliente) LEFT JOIN provincias PR ON(C.id_provincia=PR.id_provincia)
WHERE F.id_cliente>=0
AND F.id_serie>=0
AND F.id_serie<=3
AND Fecha >= DATE_SUB(CURDATE(),INTERVAL 1 DAY)
GROUP BY F.id_factura
