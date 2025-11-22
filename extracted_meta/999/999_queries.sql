-- SQL Queries for Dashboard: DOD_GMV_Chargeable
-- Dashboard ID: 999
-- Total Charts: 2
================================================================================

-- Chart 1: DOD_GMV (ID: 4838)
-- Chart Type: pivot_table_v2
-- Dataset: DOD_GMV_SB
-- Database: Trino
--------------------------------------------------------------------------------
SELECT "Days" AS "Days", SUM(TOTAL_GMV)/1e7 AS "Total GMV(in Cr)", SUM((CC_GMV)+(DC_GMV)+(EMI_GMV)+(UPI_CC_GMV)+(CS70_UPI_CC_GMV))/1e7 AS "CARD_GMV", SUM(AGG_GMV_EXCLUDING_UPI)/1e7 AS "Chargeable GMV (in Cr)", ((SUM(AGG_GMV_EXCLUDING_UPI)) / (SUM(CC_GMV+DC_GMV+EMI_GMV+UPI_CC_GMV+CS70_UPI_CC_GMV)))*100 AS "Chargeable %" 
FROM (WITH CTE AS (
select DATE(dt) dt,
CASE WHEN UPPER(COALESCE(transaction_bank_settled,'FALSE')) IN ('TRUE') THEN 'POS' ELSE 'AGG' END POSPROVIDER_FLAG,
case
when lower(requesttype) = 'edc' and lower(payment_mode) = 'credit_card' and final_emitype not in ('Brand EMI full swipe','Bank_full_swipe_EMI')  then 'CREDIT_CARD'
when lower(requesttype) = 'edc' and lower(payment_mode) = 'debit_card' and final_emitype not in ('Brand EMI full swipe','Bank_full_swipe_EMI')  then 'DEBIT_CARD'
when final_emitype  in ('Brand EMI','Brand EMI full swipe','Bank_EMI','Bank_full_swipe_EMI') then'EMI'
when final_emitype  not in ('Brand EMI','Brand EMI full swipe','Bank_EMI','Bank_full_swipe_EMI') and payment_mode = 'UPI' AND requesttype = 'DYNAMIC_QR' AND upi_sub_type = 'UPI_CREDIT_CARD' then 'UPI_CC'
when final_emitype  not in ('Brand EMI','Brand EMI full swipe','Bank_EMI','Bank_full_swipe_EMI') and payment_mode = 'UPI' AND requesttype = 'DYNAMIC_QR' AND COALESCE(upi_sub_type,'OTHERS') NOT IN ('UPI_CREDIT_CARD') then 'UPI'
when final_emitype  not in ('Brand EMI','Brand EMI full swipe','Bank_EMI','Bank_full_swipe_EMI') and payment_mode = 'UPI' AND requesttype = 'SEAMLESS_3D_FORM' AND upi_sub_type = 'UPI_CREDIT_CARD' then 'CS70_UPI_CC'
when final_emitype  not in ('Brand EMI','Brand EMI full swipe','Bank_EMI','Bank_full_swipe_EMI') and payment_mode = 'UPI' AND requesttype = 'SEAMLESS_3D_FORM' AND COALESCE(upi_sub_type,'OTHERS') NOT IN ('UPI_CREDIT_CARD') then 'CS70_UPI'
ELSE 'OTHERS' END AS Final_payment_mode,
sum(gtv + coalesce(gtv_ad,0)) as EDC_GMV, sum(pg_comm+coalesce(pg_comm_ad,0)) mdr
from cdo.business_edc_txn_base_snapshot_v3
where gtv/txn>1
and device_serial_no is not null
and date(dt) >=date_trunc('month',current_date - interval '1' day) and dl_last_updated >=date_trunc('month',current_date - interval '1' day)
and lower(mid) in (select distinct lower(mid)
from cdo.edc_final_business_base_snapshot_v3 t1
left join user_paytm_payments.offline_channel_mapping_for_ra ra
on lower(t1.mid) = lower(ra.pg_mid)
where length(trim(t1.device_serial_no))<16
and upper(ra.channel) in ('SEMI ORGANISED','BANKING','ONLINE','RETAIL_EDC','RETAIL_MM')) group by 1,2,3)

SELECT DAY(DT) AS Days,
SUM(COALESCE(EDC_GMV,0)) AS TOTAL_GMV,
SUM(case when final_payment_mode = 'CREDIT_CARD' THEN  COALESCE(EDC_GMV,0) END) AS CC_GMV,
SUM(case when final_payment_mode = 'DEBIT_CARD' THEN  COALESCE(EDC_GMV,0) END) AS DC_GMV,
SUM(case when final_payment_mode = 'EMI' THEN  COALESCE(EDC_GMV,0) END) AS EMI_GMV,
SUM(case when final_payment_mode = 'UPI_CC' THEN  COALESCE(EDC_GMV,0) END) AS UPI_CC_GMV,
SUM(case when final_payment_mode = 'UPI' THEN  COALESCE(EDC_GMV,0) END) AS UPI_GMV,
SUM(case when final_payment_mode = 'CS70_UPI_CC' THEN  COALESCE(EDC_GMV,0) END) AS CS70_UPI_CC_GMV,
SUM(case when final_payment_mode = 'CS70_UPI' THEN  COALESCE(EDC_GMV,0) END) AS CS70_UPI_GMV,
SUM(case when final_payment_mode = 'OTHERS' THEN  COALESCE(EDC_GMV,0) END) AS REST_GMV,
SUM(COALESCE(MDR,0)) AS TOTAL_REVENUE,
SUM(case when final_payment_mode = 'CREDIT_CARD' THEN  COALESCE(MDR,0) END) AS CC_MDR,
SUM(case when final_payment_mode = 'DEBIT_CARD' THEN  COALESCE(MDR,0) END) AS DC_MDR,
SUM(case when final_payment_mode = 'EMI' THEN  COALESCE(MDR,0) END) AS EMI_MDR,
SUM(case when final_payment_mode = 'UPI_CC' THEN  COALESCE(MDR,0) END) AS UPI_CC_MDR,
SUM(case when final_payment_mode = 'UPI' THEN  COALESCE(MDR,0) END) AS UPI_MDR,
SUM(case when final_payment_mode = 'CS70_UPI_CC' THEN  COALESCE(MDR,0) END) AS CS70_UPI_CC_MDR,
SUM(case when final_payment_mode = 'CS70_UPI' THEN  COALESCE(MDR,0) END) AS CS70_UPI_MDR,
SUM(CASE WHEN POSPROVIDER_FLAG = 'AGG' THEN COALESCE(EDC_GMV,0) END) AS AGG_GMV,
SUM(CASE WHEN POSPROVIDER_FLAG = 'AGG' AND FINAL_PAYMENT_MODE NOT IN ('UPI','CS70_UPI') THEN COALESCE(EDC_GMV,0) END) AS AGG_GMV_EXCLUDING_UPI,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'CREDIT_CARD' THEN  COALESCE(EDC_GMV,0) END) AS AGG_CC_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'DEBIT_CARD' THEN  COALESCE(EDC_GMV,0) END) AS AGG_DC_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'EMI' THEN  COALESCE(EDC_GMV,0) END) AS AGG_EMI_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'UPI_CC' THEN  COALESCE(EDC_GMV,0) END) AS AGG_UPI_CC_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'UPI' THEN  COALESCE(EDC_GMV,0) END) AS AGG_UPI_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'CS70_UPI_CC' THEN  COALESCE(EDC_GMV,0) END) AS AGG_CS70_UPI_CC_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'CS70_UPI' THEN  COALESCE(EDC_GMV,0) END) AS AGG_CS70_UPI_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'OTHERS' THEN  COALESCE(EDC_GMV,0) END) AS AGG_REST_GMV
FROM CTE
GROUP BY 1
ORDER BY  DAYS
) AS virtual_table GROUP BY "Days" ORDER BY "Total GMV(in Cr)" DESC
LIMIT 1000;



================================================================================

-- Chart 2: DOD_GMV (ID: 4838)
-- Chart Type: pivot_table_v2
-- Dataset: DOD_GMV_SB
-- Database: Trino
--------------------------------------------------------------------------------
SELECT "Days" AS "Days", SUM(TOTAL_GMV)/1e7 AS "Total GMV(in Cr)", SUM((CC_GMV)+(DC_GMV)+(EMI_GMV)+(UPI_CC_GMV)+(CS70_UPI_CC_GMV))/1e7 AS "CARD_GMV", SUM(AGG_GMV_EXCLUDING_UPI)/1e7 AS "Chargeable GMV (in Cr)", ((SUM(AGG_GMV_EXCLUDING_UPI)) / (SUM(CC_GMV+DC_GMV+EMI_GMV+UPI_CC_GMV+CS70_UPI_CC_GMV)))*100 AS "Chargeable %" 
FROM (WITH CTE AS (
select DATE(dt) dt,
CASE WHEN UPPER(COALESCE(transaction_bank_settled,'FALSE')) IN ('TRUE') THEN 'POS' ELSE 'AGG' END POSPROVIDER_FLAG,
case
when lower(requesttype) = 'edc' and lower(payment_mode) = 'credit_card' and final_emitype not in ('Brand EMI full swipe','Bank_full_swipe_EMI')  then 'CREDIT_CARD'
when lower(requesttype) = 'edc' and lower(payment_mode) = 'debit_card' and final_emitype not in ('Brand EMI full swipe','Bank_full_swipe_EMI')  then 'DEBIT_CARD'
when final_emitype  in ('Brand EMI','Brand EMI full swipe','Bank_EMI','Bank_full_swipe_EMI') then'EMI'
when final_emitype  not in ('Brand EMI','Brand EMI full swipe','Bank_EMI','Bank_full_swipe_EMI') and payment_mode = 'UPI' AND requesttype = 'DYNAMIC_QR' AND upi_sub_type = 'UPI_CREDIT_CARD' then 'UPI_CC'
when final_emitype  not in ('Brand EMI','Brand EMI full swipe','Bank_EMI','Bank_full_swipe_EMI') and payment_mode = 'UPI' AND requesttype = 'DYNAMIC_QR' AND COALESCE(upi_sub_type,'OTHERS') NOT IN ('UPI_CREDIT_CARD') then 'UPI'
when final_emitype  not in ('Brand EMI','Brand EMI full swipe','Bank_EMI','Bank_full_swipe_EMI') and payment_mode = 'UPI' AND requesttype = 'SEAMLESS_3D_FORM' AND upi_sub_type = 'UPI_CREDIT_CARD' then 'CS70_UPI_CC'
when final_emitype  not in ('Brand EMI','Brand EMI full swipe','Bank_EMI','Bank_full_swipe_EMI') and payment_mode = 'UPI' AND requesttype = 'SEAMLESS_3D_FORM' AND COALESCE(upi_sub_type,'OTHERS') NOT IN ('UPI_CREDIT_CARD') then 'CS70_UPI'
ELSE 'OTHERS' END AS Final_payment_mode,
sum(gtv + coalesce(gtv_ad,0)) as EDC_GMV, sum(pg_comm+coalesce(pg_comm_ad,0)) mdr
from cdo.business_edc_txn_base_snapshot_v3
where gtv/txn>1
and device_serial_no is not null
and date(dt) >=date_trunc('month',current_date - interval '1' day) and dl_last_updated >=date_trunc('month',current_date - interval '1' day)
and lower(mid) in (select distinct lower(mid)
from cdo.edc_final_business_base_snapshot_v3 t1
left join user_paytm_payments.offline_channel_mapping_for_ra ra
on lower(t1.mid) = lower(ra.pg_mid)
where length(trim(t1.device_serial_no))<16
and upper(ra.channel) in ('SEMI ORGANISED','BANKING','ONLINE','RETAIL_EDC','RETAIL_MM')) group by 1,2,3)

SELECT DAY(DT) AS Days,
SUM(COALESCE(EDC_GMV,0)) AS TOTAL_GMV,
SUM(case when final_payment_mode = 'CREDIT_CARD' THEN  COALESCE(EDC_GMV,0) END) AS CC_GMV,
SUM(case when final_payment_mode = 'DEBIT_CARD' THEN  COALESCE(EDC_GMV,0) END) AS DC_GMV,
SUM(case when final_payment_mode = 'EMI' THEN  COALESCE(EDC_GMV,0) END) AS EMI_GMV,
SUM(case when final_payment_mode = 'UPI_CC' THEN  COALESCE(EDC_GMV,0) END) AS UPI_CC_GMV,
SUM(case when final_payment_mode = 'UPI' THEN  COALESCE(EDC_GMV,0) END) AS UPI_GMV,
SUM(case when final_payment_mode = 'CS70_UPI_CC' THEN  COALESCE(EDC_GMV,0) END) AS CS70_UPI_CC_GMV,
SUM(case when final_payment_mode = 'CS70_UPI' THEN  COALESCE(EDC_GMV,0) END) AS CS70_UPI_GMV,
SUM(case when final_payment_mode = 'OTHERS' THEN  COALESCE(EDC_GMV,0) END) AS REST_GMV,
SUM(COALESCE(MDR,0)) AS TOTAL_REVENUE,
SUM(case when final_payment_mode = 'CREDIT_CARD' THEN  COALESCE(MDR,0) END) AS CC_MDR,
SUM(case when final_payment_mode = 'DEBIT_CARD' THEN  COALESCE(MDR,0) END) AS DC_MDR,
SUM(case when final_payment_mode = 'EMI' THEN  COALESCE(MDR,0) END) AS EMI_MDR,
SUM(case when final_payment_mode = 'UPI_CC' THEN  COALESCE(MDR,0) END) AS UPI_CC_MDR,
SUM(case when final_payment_mode = 'UPI' THEN  COALESCE(MDR,0) END) AS UPI_MDR,
SUM(case when final_payment_mode = 'CS70_UPI_CC' THEN  COALESCE(MDR,0) END) AS CS70_UPI_CC_MDR,
SUM(case when final_payment_mode = 'CS70_UPI' THEN  COALESCE(MDR,0) END) AS CS70_UPI_MDR,
SUM(CASE WHEN POSPROVIDER_FLAG = 'AGG' THEN COALESCE(EDC_GMV,0) END) AS AGG_GMV,
SUM(CASE WHEN POSPROVIDER_FLAG = 'AGG' AND FINAL_PAYMENT_MODE NOT IN ('UPI','CS70_UPI') THEN COALESCE(EDC_GMV,0) END) AS AGG_GMV_EXCLUDING_UPI,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'CREDIT_CARD' THEN  COALESCE(EDC_GMV,0) END) AS AGG_CC_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'DEBIT_CARD' THEN  COALESCE(EDC_GMV,0) END) AS AGG_DC_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'EMI' THEN  COALESCE(EDC_GMV,0) END) AS AGG_EMI_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'UPI_CC' THEN  COALESCE(EDC_GMV,0) END) AS AGG_UPI_CC_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'UPI' THEN  COALESCE(EDC_GMV,0) END) AS AGG_UPI_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'CS70_UPI_CC' THEN  COALESCE(EDC_GMV,0) END) AS AGG_CS70_UPI_CC_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'CS70_UPI' THEN  COALESCE(EDC_GMV,0) END) AS AGG_CS70_UPI_GMV,
SUM(case when POSPROVIDER_FLAG = 'AGG' AND final_payment_mode = 'OTHERS' THEN  COALESCE(EDC_GMV,0) END) AS AGG_REST_GMV
FROM CTE
GROUP BY 1
ORDER BY  DAYS
) AS virtual_table GROUP BY "Days" ORDER BY "Total GMV(in Cr)" DESC
LIMIT 1000;



================================================================================

