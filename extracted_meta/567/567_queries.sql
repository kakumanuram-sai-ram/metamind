-- SQL Queries for Dashboard: BBD Flipkart Tracking
-- Dashboard ID: 567
-- Total Charts: 9
================================================================================

-- Chart 1: BBD Flipkart Tracking (ID: 2780)
-- Chart Type: pivot_table_v2
-- Dataset: Flipkart BBD Tracking
-- Database: Trino
--------------------------------------------------------------------------------
SELECT mnt_mtd AS mnt_mtd, sum("MAU") AS "MAU__", sum("NR") AS "NR", sum("New") AS "New", sum("React") AS "React", sum(txns) AS "Txns", sum("Gvm") AS "Gmv", sum(card_issued) AS "#Card Issued", sum(card_scrached) AS "#Card Scrached", sum("card_scrached_same_Day") AS "#Card Scrached D0", sum(card_scrached_same_Day*1.0000)/sum(card_scrached*1.0000) AS "D0 Scrach Rate", sum(burn_issued) AS "Burn Issued", sum(burn_processed) AS "Burn Processed" 
FROM (with upi_online_txns AS (
      SELECT day_id, payer_cust_id, txn_id, amount, payee_vpa,final_category,txn_timestamp
FROM (
-- select
-- date(txn_timestamp) day_id, 
-- payer_cust_id AS payer_cust_id,
-- txn_timestamp,
-- txn_id,
-- amount,
-- payee_vpa,
-- final_category,
-- row_number() over (partition by payer_cust_id, date_trunc('month', date(txn_timestamp)) order by txn_timestamp) as rn_ft
-- from hive.user_paytm_payments.upi_flow_wise_base_cm                     --#Change 1 Table: Done
-- where day_id >=DATE'2025-09-01'                                         --#Change 2 dates : Done

-- CASE                        
--         WHEN flow_category IN ('P2P') THEN 'P2P'
--         WHEN flow_category IN ('3P QR', 'Paytm QR') THEN 'SnP'
--         WHEN flow_category IN ('Intent', 'P2M Collect','Mandate_Online') THEN 'Online'
--         WHEN flow_category IN ('Onus_ExcMandates','Mandate_Onus') THEN 'Onus'
--         ELSE 'Others' 
-- END AS final_category,
-- row_number() over (partition by customer_id_payer, date_trunc('month', date(txn_timestamp)) order by txn_timestamp) as rn_ft --

-- row_number() over (partition by customer_id_payer, date_trunc('month', date(txn_timestamp)) order by txn_timestamp) as rn_ft
-- FROM  hive.cdo.fact_upi_transactions_snapshot_v3
-- WHERE dl_last_updated >=date_trunc('MONTH', DATE_ADD('month',-1, date_add('day',-1,current_date)))
--   AND transaction_date_key  >= date_trunc('MONTH', DATE_ADD('month',-1, date_add('day',-1,current_date)))
--   AND status IN ('SUCCESS','DEEMED')
--   AND transaction_type IN ('PAY','COLLECT')
--   AND lower(payer_handle) IN ('paytm','ptyes','ptaxis','pthdfc','ptsbi')
--   and category in ('VPA2ACCOUNT','VPA2VPA','VPA2MERCHANT')
  
        
        
        
          select day_id, payer_cust_id, txn_id, amount, payee_vpa,final_category,txn_timestamp,
          row_number() over (partition by payer_cust_id, date_trunc('month', date(txn_timestamp)) order by txn_timestamp) as rn_ft
          from user_paytm_payments.upi_flow_wise_base_cm -- MTD Source
          where  day_id >= date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          and day(day_id) <= day(current_date  - interval '01' day)
        union all
          select day_id, payer_cust_id, txn_id, amount, payee_vpa,final_category,txn_timestamp,
          row_number() over (partition by payer_cust_id, date_trunc('month', date(txn_timestamp)) order by txn_timestamp) as rn_ft
          from user_paytm_payments.upi_flow_wise_base_partitioned 
        --   where day_id >= date'2025-07-01'
          where  day_id >= date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          and day(day_id) <= day(current_date  - interval '01' day)
          -- date_trunc(current_date  - interval '01' day - interval  '01' month)
          -- date_trunc('MONTH', DATE_ADD('month',-1, date_add('day',-1,current_date)))
      )
      )
,final_online as
(
   select a.*
   from (
     select *, row_number() over(partition by payer_cust_id , date_trunc('month',day_id) order by txn_timestamp) krn 
     from upi_online_txns
    ) a
    join user_paytm_payments.upi_3p_online_merchant_vpa_mapping b1
    ON lower(a.payee_vpa) = lower(b1.payee_vpa)
        where final_category = 'Online'
    and  lower(a.payee_vpa) in (
    'paytm-79192590@ptybl','paytm-79192716@ptybl','flipkart.hypg@kotakpay','paytm-64090553@paytm','paytm-64090553@ptybl',
    'flipkartgrocery.payu@hdfcbank'
,'idfcfirstbank.payu@mairtel'
,'idfcbankloanrepayment.payu@hdfcbank'
,'idfc.payu@icici'
,'flipkart.hyperpg@axb'
,'flipkart.hypg@yespay'
,'setu.flipkart@pineaxis'
,'79003574@ptybl'
,'fkrt@axl'
,'fkrt@ybl'
,'flipkart.payu@axisbank'
,'flipkart.payu@hdfcbank'
,'flipkart.payu@icici'
,'flipkart1.payu@hdfcbank'
,'flipkart1.payu@indus'
,'flipkart1@indus'
,'flipkart2020paytm@hdfcbank'
,'flipkartinterne.payu@mairtel'
,'flipkartinterne814.rzp@icici'
,'flipkartinternetprivatelimited.rzp@hdfcbank'
,'flipkartinternetprivatelimited28.paytm@hdfcbank'
,'flipkartinternetprivatelimited59.paytm@hdfcbank'
,'flipkartwholesale.cca@icici'
,'mswipe.1400062924022657@kotak'
,'mswipe.1400062924023153@kotak'
,'paytm-56505013@paytm'
,'paytm-56505013@ptybl'
,'paytm-78824088@paytm'
,'paytm-78824088@ptybl'
,'sbipmopad.022211900326629-ym571606@sbipay'
,'sbipmopad.02sob0000046783-yc019760@sbipay'
,'flipkartinternetgroce.payu@mairtel'
,'flipkartgrocery-12611431.payu@indus'
,'paytm-78959480@ptybl'
,'flipkartgiftcard.payu@hdfcbank'
,'paytm-82335889@ptybl'
,'flipkart12474444.payu@icici'
,'flipkartpayments-8599699.payu@indus'
,'flipkartinternetpriva.payu@mairtel'
,'flipkart8599699.payu@icici'
,'flipkart-135670.payu@indus'
,'flipkart-149223.payu@indus'
,'flipkart-12474444.payu@indus'
,'flipkartpayments-173405.payu@indus'
,'flipkart149223.payu@axisbank'
,'flipkart8599699.payu@axisbank'
,'flipkart12474444.payu@axisbank'
,'flipkart173405.payu@axisbank'
,'flipkart12611431.payu@axisbank'
,'flipkart149223.payu@mairtel'
,'flipkart12474444.payu@mairtel'
,'flipkart173405.payu@mairtel'
,'flipkart149223.payu@hdfcbank'
,'flipkart173405.payu@hdfcbank'
,'flipkart149223.payu@icici'
,'flipkart12611431.payu@icici'
,'flipkartpayin3.hypg@yespay'
)
)

,paytm_nrr_rolling as
(
SELECT dt, payer_cust_id cust_id , user_type
FROM (
select txn_date as dt,user_type,customer_Id as payer_cust_id
from 
(
select customer_Id,
CASE
WHEN user_type = 'New' THEN 'New'
else 'React_2M+'
END AS user_type,
user_type as user_type_bucket,
txn_date,
row_number()over(partition by customer_Id order by txn_date) as rn
from user_paytm_payments.rolling_nrr_v1 -- this is rolling table for rolling data.
where txn_date >= date_trunc('month',current_date  - interval '01' day - interval  '01' month) 
and day(txn_date) <= day(current_Date - interval '01' day)
and user_type not in ('Repeat') and customer_Id not in (
Select cust_id from user_paytm_payments.ft_base_with_mapping_raw_rolling_nrr_with_online_cm
where dt >= date_trunc('month',current_date  - interval '01' day)
and channel in ('FMCG','MASU Online','MASU Offline') 
union all
Select cust_id from user_paytm_payments.ft_base_with_mapping_raw_rolling_nrr_with_online
where dt >= date_trunc('month',current_date  - interval '01' day - interval  '01' month)
and channel in ('FMCG','MASU Online','MASU Offline'))
)t1
where rn = 1
)

)

,summary_ as (
select 
date_Trunc('month',day_id) mnt_mtd,
-- user_type,
count(distinct payer_cust_id) MAU,
count(distinct payer_cust_id) filter(where krn = 1 and user_type in('New','React_2M+')) NR,
count(distinct payer_cust_id) filter(where krn = 1 and user_type in('New'))  New,
count(distinct payer_cust_id) filter(where krn = 1 and user_type in('React_2M+'))  React,
count(txn_id)txns, 
sum(amount) Gvm 
--payee_vpa,final_category 
from final_online a 
left join  
paytm_nrr_rolling
--paytm_nrr 
b on a.payer_cust_id  = b.cust_id and date_Trunc('month',a.day_id) = date_Trunc('month',b.dt)
where day(day_id) <= day(current_Date - interval '01' day)
group by 1
) 

,burn as (
    select *,
      case
          when a.status = 1 and a.fulfillment_status = 3 then 'Given'
          when a.status = 1 and a.fulfillment_status = 2 then 'Processing'
          when a.status = 2 and a.fulfillment_status = 1 then 'Unscratched' -- need to remove 
          when a.status = 1 and a.fulfillment_status = 1 then 'Pending'
      end as status_1,
      case
        when a.redemption_type = 'coins' then (a.amount/166.67)
        else a.amount
              end as cashburn,
              json_extract_scalar(info, '$.scratchCardId') AS scratchCardId,
              json_extract_scalar(info, '$.scratched') AS scratched
            from
      (
          select *
          from hive.promocard.supercash_task_snapshot_v3
          where dl_last_updated >=date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          and date(created_at) >= date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          and day(date(created_at))<= day(current_date  - interval '01' day)
          and status in (1,2)
          and fulfillment_status in (1,2,3)
          and campaign in ('UPI_3P_FLIPKART_30CB_11SEP25')
      ) a
),

burn_summary as (
select 
date_trunc('month',date(created_at)) mnt,
-- case when date_diff('hour',created_at, b.scratched_at) is null then null
-- when date_diff('hour',created_at, b.scratched_at) <=23 then 'within 24 hr' else 'after 24 hr' end as time_diff,
-- status_1, 
-- scratched,
count(a.id) cards,
count(a.id) filter (where  scratched = 'true') card_scrached ,
count(a.id) filter (where  scratched = 'true' and date_diff('hour',created_at, b.scratched_at) <=23 ) card_scrached_same_Day ,
sum(cashburn) burn_issued,
sum(cashburn) filter (where  status_1 in('Given','Processing','Pending')) burn_processed
from burn a 
left join (
    SELECT id,scratched_at FROM "hive"."scratchcard"."scratch_card_snapshot_v3" where dl_last_updated >= date_trunc('month',current_date  - interval '01' day - interval  '01' month)
)b on a.scratchCardId = cast(b.id as varchar)
group by 1
)
-- select * from burn_summary

select
a.mnt_mtd,
a.MAU,
a.NR,
a.New,
a.React,
a.txns, 
a.Gvm ,
b.cards card_issued,
b.card_scrached card_scrached,
b.card_scrached_same_Day card_scrached_same_Day,
(b.card_scrached_same_Day*1.0000)/(b.card_scrached*1.0000) SameDay_scrach_rate,
b.burn_issued,
b.burn_processed
from summary_ a 
left join burn_summary b on a.mnt_mtd = b.mnt
) AS virtual_table GROUP BY mnt_mtd ORDER BY sum("MAU") DESC
LIMIT 10000;



================================================================================

-- Chart 2: Flipkart BBD (ID: 2788)
-- Chart Type: pivot_table_v2
-- Dataset: Flipkart BBD
-- Database: Trino
--------------------------------------------------------------------------------
SELECT day_id AS day_id, sum(dau) AS "Dau__", sum(mau) AS "Mau", sum("NR") AS "NR", sum(new) AS "New", sum("React") AS "React", sum(n_txns) AS n_txns, sum(gmv) AS gmv 
FROM (with upi_reference_table as (
select a.*, date_trunc('month',day_id) mnt
from (
select
date(txn_timestamp) day_id, 
customer_id_payer AS customer_id,
txn_timestamp created_on,
txn_id,
amount,
payee_vpa,
-- from hive.user_paytm_payments.upi_flow_wise_base_cm                     --#Change 1 Table: Done
-- where day_id >=DATE'2025-09-01'                                         --#Change 2 dates : Done

CASE                        
        WHEN flow_category IN ('P2P') THEN 'P2P'
        WHEN flow_category IN ('3P QR', 'Paytm QR') THEN 'SnP'
        WHEN flow_category IN ('Intent', 'P2M Collect','Mandate_Online') THEN 'Online'
        WHEN flow_category IN ('Onus_ExcMandates','Mandate_Onus') THEN 'Onus'
        ELSE 'Others' 
END AS final_category,
row_number() over (partition by customer_id_payer, date_trunc('month', date(txn_timestamp)) order by txn_timestamp) as rn_ft

-- row_number() over (partition by customer_id_payer, date_trunc('month', date(txn_timestamp)) order by txn_timestamp) as rn_ft
FROM  hive.cdo.fact_upi_transactions_snapshot_v3
WHERE dl_last_updated >=DATE'2025-09-01'
  AND transaction_date_key  >= DATE'2025-09-01'
  AND status IN ('SUCCESS','DEEMED')
  AND transaction_type IN ('PAY','COLLECT')
  AND lower(payer_handle) IN ('paytm','ptyes','ptaxis','pthdfc','ptsbi')
  and category in ('VPA2ACCOUNT','VPA2VPA','VPA2MERCHANT')
  


-- dl_last_updated>= date_trunc('month',current_Date - interval  '01' day - interval '01' month)
                                                                    --#Change 3Add VPA 2: Done
      -- AND PAYEE_VPA IN ('flipkartgrocery.payu@hdfcbank','idfcfirstbank.payu@mairtel','idfcbankloanrepayment.payu@hdfcbank','idfc.payu@icici',
      -- 'flipkart.hyperpg@axb','flipkart.hypg@yespay','setu.flipkart@pineaxis','79003574@ptybl','fkrt@axl','fkrt@ybl','flipkart.payu@axisbank','flipkart.payu@hdfcbank','flipkart.payu@icici','flipkart1.payu@hdfcbank','flipkart1.payu@indus','flipkart1@indus','flipkart2020paytm@hdfcbank','flipkartinterne.payu@mairtel','flipkartinterne814.rzp@icici','flipkartinternetprivatelimited.rzp@hdfcbank','flipkartinternetprivatelimited28.paytm@hdfcbank','flipkartinternetprivatelimited59.paytm@hdfcbank','flipkartwholesale.cca@icici','mswipe.1400062924022657@kotak','mswipe.1400062924023153@kotak','paytm-56505013@paytm','paytm-56505013@ptybl','paytm-78824088@paytm','paytm-78824088@ptybl','sbipmopad.022211900326629-ym571606@sbipay','sbipmopad.02sob0000046783-yc019760@sbipay','flipkartinternetgroce.payu@mairtel','flipkartgrocery-12611431.payu@indus','paytm-78959480@ptybl','flipkartgiftcard.payu@hdfcbank','paytm-82335889@ptybl','flipkart12474444.payu@icici','flipkartpayments-8599699.payu@indus','flipkartinternetpriva.payu@mairtel','flipkart8599699.payu@icici','flipkart-135670.payu@indus','flipkart-149223.payu@indus','flipkart-12474444.payu@indus','flipkartpayments-173405.payu@indus','flipkart149223.payu@axisbank','flipkart8599699.payu@axisbank','flipkart12474444.payu@axisbank','flipkart173405.payu@axisbank','flipkart12611431.payu@axisbank','flipkart149223.payu@mairtel','flipkart12474444.payu@mairtel','flipkart173405.payu@mairtel','flipkart149223.payu@hdfcbank','flipkart173405.payu@hdfcbank','flipkart149223.payu@icici','flipkart12611431.payu@icici','flipkartpayin3.hypg@yespay','flipkart12474444.payu@axisbank','flipkart12611431.payu@axisbank')
    and category in ('VPA2ACCOUNT','VPA2VPA','VPA2MERCHANT')
    and status = 'SUCCESS'
    and lower(payer_handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi')
    )a

    WHERE PAYEE_VPA IN ('paytm-79192590@ptybl','paytm-79192716@ptybl','flipkart.hypg@kotakpay','paytm-64090553@paytm','paytm-64090553@ptybl',
    'paytm-79192590@ptybl','paytm-79192716@ptybl','flipkart.hypg@kotakpay', 'flipkartgrocery.payu@hdfcbank','idfcfirstbank.payu@mairtel','idfcbankloanrepayment.payu@hdfcbank','idfc.payu@icici',
       'flipkart.hyperpg@axb','flipkart.hypg@yespay','setu.flipkart@pineaxis','79003574@ptybl','fkrt@axl','fkrt@ybl','flipkart.payu@axisbank','flipkart.payu@hdfcbank','flipkart.payu@icici','flipkart1.payu@hdfcbank','flipkart1.payu@indus','flipkart1@indus','flipkart2020paytm@hdfcbank','flipkartinterne.payu@mairtel','flipkartinterne814.rzp@icici','flipkartinternetprivatelimited.rzp@hdfcbank','flipkartinternetprivatelimited28.paytm@hdfcbank','flipkartinternetprivatelimited59.paytm@hdfcbank','flipkartwholesale.cca@icici','mswipe.1400062924022657@kotak','mswipe.1400062924023153@kotak','paytm-56505013@paytm','paytm-56505013@ptybl','paytm-78824088@paytm','paytm-78824088@ptybl','sbipmopad.022211900326629-ym571606@sbipay','sbipmopad.02sob0000046783-yc019760@sbipay','flipkartinternetgroce.payu@mairtel','flipkartgrocery-12611431.payu@indus','paytm-78959480@ptybl','flipkartgiftcard.payu@hdfcbank','paytm-82335889@ptybl','flipkart12474444.payu@icici','flipkartpayments-8599699.payu@indus','flipkartinternetpriva.payu@mairtel','flipkart8599699.payu@icici','flipkart-135670.payu@indus','flipkart-149223.payu@indus','flipkart-12474444.payu@indus','flipkartpayments-173405.payu@indus','flipkart149223.payu@axisbank','flipkart8599699.payu@axisbank','flipkart12474444.payu@axisbank','flipkart173405.payu@axisbank','flipkart12611431.payu@axisbank','flipkart149223.payu@mairtel','flipkart12474444.payu@mairtel','flipkart173405.payu@mairtel','flipkart149223.payu@hdfcbank','flipkart173405.payu@hdfcbank','flipkart149223.payu@icici','flipkart12611431.payu@icici','flipkartpayin3.hypg@yespay','flipkart12474444.payu@axisbank','flipkart12611431.payu@axisbank')




--       JOIN  hive.user_paytm_payments.upi_3p_online_merchant_vpa_mapping b on LOWER(a.payee_vpa) = LOWER(b.payee_vpa)
-- WHERE b.online_merchant_name = 'flipkart' --## change later
    ),
paytm_nrr AS (
      SELECT customer_id customer_id, date_trunc('month',date(txn_date) ) mnt,
      CASE
      WHEN user_type = 'New' THEN 'New'
      WHEN user_type = 'Repeat' THEN 'Repeat'
      ELSE 'React_2M+'
      END AS user_type
      FROM  hive.user_paytm_payments.rolling_nrr_v1
      WHERE txn_date >= date'2025-09-01'
      and user_type not IN ('Repeat')
       and
        customer_Id not in (
        Select cust_id from hive.user_paytm_payments.ft_base_with_mapping_raw_rolling_nrr_with_online --set of user is already tagged
        where dt >=  date'2025-09-01'--date_trunc('month',current_Date - interval  '01' day - interval '01' month)
        and channel in ('FMCG','MASU Online','MASU Offline')
        union all
        Select cust_id from hive.user_paytm_payments.ft_base_with_mapping_raw_rolling_nrr_with_online_cm
        where dt >=  date'2025-09-01'--date_trunc('month',current_Date - interval  '01' day - interval '01' month)
        and channel in ('FMCG','MASU Online','MASU Offline')
        )
      )
----------------------------------------------------------------------------------------------------------------------------------------------------------------
select
day_id,
    count(distinct a.customer_id) as dau,
    count(distinct case when a.rn_mau = 1 then a.customer_id end) as mau,
    count(distinct case when a.rn_ft = 1 and b.customer_id is not null then a.customer_id  end) as NR, --- paytm new/react
    count(distinct case when a.rn_ft = 1 and b.user_type = 'New' then a.customer_id  end) as new, --- paytm new/react
    count(distinct case when a.rn_ft = 1 and  b.user_type = 'React_2M+' then a.customer_id  end) as React, --- paytm new/react
    count(distinct a.txn_id) as n_txns,
    sum(cast (amount as double)) as gmv
from
(
select day_id,txn_id,customer_id,amount,rn_ft,mnt,
row_number() over (partition by customer_id, date_trunc('month', day_id) , day_id>= date'2025-09-18' order by day_id) as rn_mau
from  upi_reference_table a
        where   final_category = 'Online'
            and day_id >= date'2025-09-01'--date_trunc('month',current_Date - interval  '01' day - interval '01' month)
)a
left join paytm_nrr b on a.customer_id = b.customer_id  and a.mnt = b.mnt
group by 1
ORDER BY 1
) AS virtual_table GROUP BY day_id ORDER BY sum(dau) DESC
LIMIT 1000;



================================================================================

-- Chart 3: Flipkart BBD DAU (ID: 2868)
-- Chart Type: big_number_total
-- Dataset: Flipkart BBD Todays Metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT count(DISTINCT payer_cust_id) AS "DAU" 
FROM (with ti as (
select 
created_on,
txn_id,
amount
FROM hive.switch.txn_info_snapshot_v3
            WHERE dl_last_updated >= current_date - interval '01' day
            and date(created_on) >= current_date - interval '01' day
            and type in ('PAY','COLLECT')
            AND category in('VPA2MERCHANT')
            AND status in('SUCCESS','DEEMED')
            and lower(psp_handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi')
and(
    (type = 'COLLECT' and (business_type is null or business_type <> 'MANDATE'))
    or(type = 'PAY' and upper(channel_code) = 'PAYTM'
    and JSON_EXTRACT_SCALAR(extended_info, '$.initiationMode') in ('04','03'))
    or(type = 'PAY' and upper(channel_code) in ('ONLINE_3P_NATIVE')
    )
)

),
tp1 as (
select txn_id, vpa payer_vpa,handle payer_handle, scope_cust_id payer_cust_id, account_type,bank_code payer_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day 
and lower(handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi') 
and participant_type = 'PAYER'
),
tp2 as (
select txn_id, vpa payee_vpa,handle payee_handle,bank_code payee_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day
and participant_type = 'PAYEE'
AND lower(vpa) IN (
'paytm-79192590@ptybl','paytm-79192716@ptybl','flipkart.hypg@kotakpay','paytm-64090553@paytm','paytm-64090553@ptybl',
'flipkartgrocery.payu@hdfcbank','idfcfirstbank.payu@mairtel','idfcbankloanrepayment.payu@hdfcbank','idfc.payu@icici',
       'flipkart.hyperpg@axb','flipkart.hypg@yespay','setu.flipkart@pineaxis','79003574@ptybl','fkrt@axl','fkrt@ybl','flipkart.payu@axisbank','flipkart.payu@hdfcbank','flipkart.payu@icici','flipkart1.payu@hdfcbank','flipkart1.payu@indus','flipkart1@indus','flipkart2020paytm@hdfcbank','flipkartinterne.payu@mairtel','flipkartinterne814.rzp@icici','flipkartinternetprivatelimited.rzp@hdfcbank','flipkartinternetprivatelimited28.paytm@hdfcbank','flipkartinternetprivatelimited59.paytm@hdfcbank','flipkartwholesale.cca@icici','mswipe.1400062924022657@kotak','mswipe.1400062924023153@kotak','paytm-56505013@paytm','paytm-56505013@ptybl','paytm-78824088@paytm','paytm-78824088@ptybl','sbipmopad.022211900326629-ym571606@sbipay','sbipmopad.02sob0000046783-yc019760@sbipay','flipkartinternetgroce.payu@mairtel','flipkartgrocery-12611431.payu@indus','paytm-78959480@ptybl','flipkartgiftcard.payu@hdfcbank','paytm-82335889@ptybl','flipkart12474444.payu@icici','flipkartpayments-8599699.payu@indus','flipkartinternetpriva.payu@mairtel','flipkart8599699.payu@icici','flipkart-135670.payu@indus','flipkart-149223.payu@indus','flipkart-12474444.payu@indus','flipkartpayments-173405.payu@indus','flipkart149223.payu@axisbank','flipkart8599699.payu@axisbank','flipkart12474444.payu@axisbank','flipkart173405.payu@axisbank','flipkart12611431.payu@axisbank','flipkart149223.payu@mairtel','flipkart12474444.payu@mairtel','flipkart173405.payu@mairtel','flipkart149223.payu@hdfcbank','flipkart173405.payu@hdfcbank','flipkart149223.payu@icici','flipkart12611431.payu@icici','flipkartpayin3.hypg@yespay','flipkart12474444.payu@axisbank','flipkart12611431.payu@axisbank')
)


select 
ti.created_on
,date(ti.created_on) dt
,ti.txn_id
,ti.amount
,tp1.payer_cust_id
 from  ti  
 join tp1 on ti.txn_id = tp1.txn_id
 join tp2 on ti.txn_id = tp2.txn_id
) AS virtual_table 
WHERE created_on >= TIMESTAMP '2025-11-22 00:00:00.000000' AND created_on < TIMESTAMP '2025-11-23 00:00:00.000000'
LIMIT 50000;



================================================================================

-- Chart 4: Flipkart BBD Txns (ID: 2870)
-- Chart Type: big_number_total
-- Dataset: Flipkart BBD Todays Metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT count(txn_id) AS "Transactions" 
FROM (with ti as (
select 
created_on,
txn_id,
amount
FROM hive.switch.txn_info_snapshot_v3
            WHERE dl_last_updated >= current_date - interval '01' day
            and date(created_on) >= current_date - interval '01' day
            and type in ('PAY','COLLECT')
            AND category in('VPA2MERCHANT')
            AND status in('SUCCESS','DEEMED')
            and lower(psp_handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi')
and(
    (type = 'COLLECT' and (business_type is null or business_type <> 'MANDATE'))
    or(type = 'PAY' and upper(channel_code) = 'PAYTM'
    and JSON_EXTRACT_SCALAR(extended_info, '$.initiationMode') in ('04','03'))
    or(type = 'PAY' and upper(channel_code) in ('ONLINE_3P_NATIVE')
    )
)

),
tp1 as (
select txn_id, vpa payer_vpa,handle payer_handle, scope_cust_id payer_cust_id, account_type,bank_code payer_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day 
and lower(handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi') 
and participant_type = 'PAYER'
),
tp2 as (
select txn_id, vpa payee_vpa,handle payee_handle,bank_code payee_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day
and participant_type = 'PAYEE'
AND lower(vpa) IN (
'paytm-79192590@ptybl','paytm-79192716@ptybl','flipkart.hypg@kotakpay','paytm-64090553@paytm','paytm-64090553@ptybl',
'flipkartgrocery.payu@hdfcbank','idfcfirstbank.payu@mairtel','idfcbankloanrepayment.payu@hdfcbank','idfc.payu@icici',
       'flipkart.hyperpg@axb','flipkart.hypg@yespay','setu.flipkart@pineaxis','79003574@ptybl','fkrt@axl','fkrt@ybl','flipkart.payu@axisbank','flipkart.payu@hdfcbank','flipkart.payu@icici','flipkart1.payu@hdfcbank','flipkart1.payu@indus','flipkart1@indus','flipkart2020paytm@hdfcbank','flipkartinterne.payu@mairtel','flipkartinterne814.rzp@icici','flipkartinternetprivatelimited.rzp@hdfcbank','flipkartinternetprivatelimited28.paytm@hdfcbank','flipkartinternetprivatelimited59.paytm@hdfcbank','flipkartwholesale.cca@icici','mswipe.1400062924022657@kotak','mswipe.1400062924023153@kotak','paytm-56505013@paytm','paytm-56505013@ptybl','paytm-78824088@paytm','paytm-78824088@ptybl','sbipmopad.022211900326629-ym571606@sbipay','sbipmopad.02sob0000046783-yc019760@sbipay','flipkartinternetgroce.payu@mairtel','flipkartgrocery-12611431.payu@indus','paytm-78959480@ptybl','flipkartgiftcard.payu@hdfcbank','paytm-82335889@ptybl','flipkart12474444.payu@icici','flipkartpayments-8599699.payu@indus','flipkartinternetpriva.payu@mairtel','flipkart8599699.payu@icici','flipkart-135670.payu@indus','flipkart-149223.payu@indus','flipkart-12474444.payu@indus','flipkartpayments-173405.payu@indus','flipkart149223.payu@axisbank','flipkart8599699.payu@axisbank','flipkart12474444.payu@axisbank','flipkart173405.payu@axisbank','flipkart12611431.payu@axisbank','flipkart149223.payu@mairtel','flipkart12474444.payu@mairtel','flipkart173405.payu@mairtel','flipkart149223.payu@hdfcbank','flipkart173405.payu@hdfcbank','flipkart149223.payu@icici','flipkart12611431.payu@icici','flipkartpayin3.hypg@yespay','flipkart12474444.payu@axisbank','flipkart12611431.payu@axisbank')
)


select 
ti.created_on
,date(ti.created_on) dt
,ti.txn_id
,ti.amount
,tp1.payer_cust_id
 from  ti  
 join tp1 on ti.txn_id = tp1.txn_id
 join tp2 on ti.txn_id = tp2.txn_id
) AS virtual_table 
WHERE created_on >= TIMESTAMP '2025-11-22 00:00:00.000000' AND created_on < TIMESTAMP '2025-11-23 00:00:00.000000'
LIMIT 50000;



================================================================================

-- Chart 5: Flipkart BBD Gmv (ID: 2872)
-- Chart Type: big_number_total
-- Dataset: Flipkart BBD Todays Metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT sum(amount) AS "Gmv" 
FROM (with ti as (
select 
created_on,
txn_id,
amount
FROM hive.switch.txn_info_snapshot_v3
            WHERE dl_last_updated >= current_date - interval '01' day
            and date(created_on) >= current_date - interval '01' day
            and type in ('PAY','COLLECT')
            AND category in('VPA2MERCHANT')
            AND status in('SUCCESS','DEEMED')
            and lower(psp_handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi')
and(
    (type = 'COLLECT' and (business_type is null or business_type <> 'MANDATE'))
    or(type = 'PAY' and upper(channel_code) = 'PAYTM'
    and JSON_EXTRACT_SCALAR(extended_info, '$.initiationMode') in ('04','03'))
    or(type = 'PAY' and upper(channel_code) in ('ONLINE_3P_NATIVE')
    )
)

),
tp1 as (
select txn_id, vpa payer_vpa,handle payer_handle, scope_cust_id payer_cust_id, account_type,bank_code payer_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day 
and lower(handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi') 
and participant_type = 'PAYER'
),
tp2 as (
select txn_id, vpa payee_vpa,handle payee_handle,bank_code payee_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day
and participant_type = 'PAYEE'
AND lower(vpa) IN (
'paytm-79192590@ptybl','paytm-79192716@ptybl','flipkart.hypg@kotakpay','paytm-64090553@paytm','paytm-64090553@ptybl',
'flipkartgrocery.payu@hdfcbank','idfcfirstbank.payu@mairtel','idfcbankloanrepayment.payu@hdfcbank','idfc.payu@icici',
       'flipkart.hyperpg@axb','flipkart.hypg@yespay','setu.flipkart@pineaxis','79003574@ptybl','fkrt@axl','fkrt@ybl','flipkart.payu@axisbank','flipkart.payu@hdfcbank','flipkart.payu@icici','flipkart1.payu@hdfcbank','flipkart1.payu@indus','flipkart1@indus','flipkart2020paytm@hdfcbank','flipkartinterne.payu@mairtel','flipkartinterne814.rzp@icici','flipkartinternetprivatelimited.rzp@hdfcbank','flipkartinternetprivatelimited28.paytm@hdfcbank','flipkartinternetprivatelimited59.paytm@hdfcbank','flipkartwholesale.cca@icici','mswipe.1400062924022657@kotak','mswipe.1400062924023153@kotak','paytm-56505013@paytm','paytm-56505013@ptybl','paytm-78824088@paytm','paytm-78824088@ptybl','sbipmopad.022211900326629-ym571606@sbipay','sbipmopad.02sob0000046783-yc019760@sbipay','flipkartinternetgroce.payu@mairtel','flipkartgrocery-12611431.payu@indus','paytm-78959480@ptybl','flipkartgiftcard.payu@hdfcbank','paytm-82335889@ptybl','flipkart12474444.payu@icici','flipkartpayments-8599699.payu@indus','flipkartinternetpriva.payu@mairtel','flipkart8599699.payu@icici','flipkart-135670.payu@indus','flipkart-149223.payu@indus','flipkart-12474444.payu@indus','flipkartpayments-173405.payu@indus','flipkart149223.payu@axisbank','flipkart8599699.payu@axisbank','flipkart12474444.payu@axisbank','flipkart173405.payu@axisbank','flipkart12611431.payu@axisbank','flipkart149223.payu@mairtel','flipkart12474444.payu@mairtel','flipkart173405.payu@mairtel','flipkart149223.payu@hdfcbank','flipkart173405.payu@hdfcbank','flipkart149223.payu@icici','flipkart12611431.payu@icici','flipkartpayin3.hypg@yespay','flipkart12474444.payu@axisbank','flipkart12611431.payu@axisbank')
)


select 
ti.created_on
,date(ti.created_on) dt
,ti.txn_id
,ti.amount
,tp1.payer_cust_id
 from  ti  
 join tp1 on ti.txn_id = tp1.txn_id
 join tp2 on ti.txn_id = tp2.txn_id
) AS virtual_table 
WHERE created_on >= TIMESTAMP '2025-11-22 00:00:00.000000' AND created_on < TIMESTAMP '2025-11-23 00:00:00.000000'
LIMIT 50000;



================================================================================

-- Chart 6: Flipkart BBD hourly users (ID: 2873)
-- Chart Type: echarts_timeseries_line
-- Dataset: Flipkart BBD Todays Metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT hour(created_on) AS hour, dt AS dt, count(DISTINCT payer_cust_id) AS "Users" 
FROM (with ti as (
select 
created_on,
txn_id,
amount
FROM hive.switch.txn_info_snapshot_v3
            WHERE dl_last_updated >= current_date - interval '01' day
            and date(created_on) >= current_date - interval '01' day
            and type in ('PAY','COLLECT')
            AND category in('VPA2MERCHANT')
            AND status in('SUCCESS','DEEMED')
            and lower(psp_handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi')
and(
    (type = 'COLLECT' and (business_type is null or business_type <> 'MANDATE'))
    or(type = 'PAY' and upper(channel_code) = 'PAYTM'
    and JSON_EXTRACT_SCALAR(extended_info, '$.initiationMode') in ('04','03'))
    or(type = 'PAY' and upper(channel_code) in ('ONLINE_3P_NATIVE')
    )
)

),
tp1 as (
select txn_id, vpa payer_vpa,handle payer_handle, scope_cust_id payer_cust_id, account_type,bank_code payer_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day 
and lower(handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi') 
and participant_type = 'PAYER'
),
tp2 as (
select txn_id, vpa payee_vpa,handle payee_handle,bank_code payee_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day
and participant_type = 'PAYEE'
AND lower(vpa) IN (
'paytm-79192590@ptybl','paytm-79192716@ptybl','flipkart.hypg@kotakpay','paytm-64090553@paytm','paytm-64090553@ptybl',
'flipkartgrocery.payu@hdfcbank','idfcfirstbank.payu@mairtel','idfcbankloanrepayment.payu@hdfcbank','idfc.payu@icici',
       'flipkart.hyperpg@axb','flipkart.hypg@yespay','setu.flipkart@pineaxis','79003574@ptybl','fkrt@axl','fkrt@ybl','flipkart.payu@axisbank','flipkart.payu@hdfcbank','flipkart.payu@icici','flipkart1.payu@hdfcbank','flipkart1.payu@indus','flipkart1@indus','flipkart2020paytm@hdfcbank','flipkartinterne.payu@mairtel','flipkartinterne814.rzp@icici','flipkartinternetprivatelimited.rzp@hdfcbank','flipkartinternetprivatelimited28.paytm@hdfcbank','flipkartinternetprivatelimited59.paytm@hdfcbank','flipkartwholesale.cca@icici','mswipe.1400062924022657@kotak','mswipe.1400062924023153@kotak','paytm-56505013@paytm','paytm-56505013@ptybl','paytm-78824088@paytm','paytm-78824088@ptybl','sbipmopad.022211900326629-ym571606@sbipay','sbipmopad.02sob0000046783-yc019760@sbipay','flipkartinternetgroce.payu@mairtel','flipkartgrocery-12611431.payu@indus','paytm-78959480@ptybl','flipkartgiftcard.payu@hdfcbank','paytm-82335889@ptybl','flipkart12474444.payu@icici','flipkartpayments-8599699.payu@indus','flipkartinternetpriva.payu@mairtel','flipkart8599699.payu@icici','flipkart-135670.payu@indus','flipkart-149223.payu@indus','flipkart-12474444.payu@indus','flipkartpayments-173405.payu@indus','flipkart149223.payu@axisbank','flipkart8599699.payu@axisbank','flipkart12474444.payu@axisbank','flipkart173405.payu@axisbank','flipkart12611431.payu@axisbank','flipkart149223.payu@mairtel','flipkart12474444.payu@mairtel','flipkart173405.payu@mairtel','flipkart149223.payu@hdfcbank','flipkart173405.payu@hdfcbank','flipkart149223.payu@icici','flipkart12611431.payu@icici','flipkartpayin3.hypg@yespay','flipkart12474444.payu@axisbank','flipkart12611431.payu@axisbank')
)


select 
ti.created_on
,date(ti.created_on) dt
,ti.txn_id
,ti.amount
,tp1.payer_cust_id
 from  ti  
 join tp1 on ti.txn_id = tp1.txn_id
 join tp2 on ti.txn_id = tp2.txn_id
) AS virtual_table GROUP BY hour(created_on), dt ORDER BY "Users" DESC
LIMIT 10000;



================================================================================

-- Chart 7: Flipkart BBD hourly txns (ID: 2874)
-- Chart Type: echarts_timeseries_line
-- Dataset: Flipkart BBD Todays Metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT hour(created_on) AS hour, dt AS dt, count(txn_id) AS "Txns" 
FROM (with ti as (
select 
created_on,
txn_id,
amount
FROM hive.switch.txn_info_snapshot_v3
            WHERE dl_last_updated >= current_date - interval '01' day
            and date(created_on) >= current_date - interval '01' day
            and type in ('PAY','COLLECT')
            AND category in('VPA2MERCHANT')
            AND status in('SUCCESS','DEEMED')
            and lower(psp_handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi')
and(
    (type = 'COLLECT' and (business_type is null or business_type <> 'MANDATE'))
    or(type = 'PAY' and upper(channel_code) = 'PAYTM'
    and JSON_EXTRACT_SCALAR(extended_info, '$.initiationMode') in ('04','03'))
    or(type = 'PAY' and upper(channel_code) in ('ONLINE_3P_NATIVE')
    )
)

),
tp1 as (
select txn_id, vpa payer_vpa,handle payer_handle, scope_cust_id payer_cust_id, account_type,bank_code payer_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day 
and lower(handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi') 
and participant_type = 'PAYER'
),
tp2 as (
select txn_id, vpa payee_vpa,handle payee_handle,bank_code payee_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day
and participant_type = 'PAYEE'
AND lower(vpa) IN (
'paytm-79192590@ptybl','paytm-79192716@ptybl','flipkart.hypg@kotakpay','paytm-64090553@paytm','paytm-64090553@ptybl',
'flipkartgrocery.payu@hdfcbank','idfcfirstbank.payu@mairtel','idfcbankloanrepayment.payu@hdfcbank','idfc.payu@icici',
       'flipkart.hyperpg@axb','flipkart.hypg@yespay','setu.flipkart@pineaxis','79003574@ptybl','fkrt@axl','fkrt@ybl','flipkart.payu@axisbank','flipkart.payu@hdfcbank','flipkart.payu@icici','flipkart1.payu@hdfcbank','flipkart1.payu@indus','flipkart1@indus','flipkart2020paytm@hdfcbank','flipkartinterne.payu@mairtel','flipkartinterne814.rzp@icici','flipkartinternetprivatelimited.rzp@hdfcbank','flipkartinternetprivatelimited28.paytm@hdfcbank','flipkartinternetprivatelimited59.paytm@hdfcbank','flipkartwholesale.cca@icici','mswipe.1400062924022657@kotak','mswipe.1400062924023153@kotak','paytm-56505013@paytm','paytm-56505013@ptybl','paytm-78824088@paytm','paytm-78824088@ptybl','sbipmopad.022211900326629-ym571606@sbipay','sbipmopad.02sob0000046783-yc019760@sbipay','flipkartinternetgroce.payu@mairtel','flipkartgrocery-12611431.payu@indus','paytm-78959480@ptybl','flipkartgiftcard.payu@hdfcbank','paytm-82335889@ptybl','flipkart12474444.payu@icici','flipkartpayments-8599699.payu@indus','flipkartinternetpriva.payu@mairtel','flipkart8599699.payu@icici','flipkart-135670.payu@indus','flipkart-149223.payu@indus','flipkart-12474444.payu@indus','flipkartpayments-173405.payu@indus','flipkart149223.payu@axisbank','flipkart8599699.payu@axisbank','flipkart12474444.payu@axisbank','flipkart173405.payu@axisbank','flipkart12611431.payu@axisbank','flipkart149223.payu@mairtel','flipkart12474444.payu@mairtel','flipkart173405.payu@mairtel','flipkart149223.payu@hdfcbank','flipkart173405.payu@hdfcbank','flipkart149223.payu@icici','flipkart12611431.payu@icici','flipkartpayin3.hypg@yespay','flipkart12474444.payu@axisbank','flipkart12611431.payu@axisbank')
)


select 
ti.created_on
,date(ti.created_on) dt
,ti.txn_id
,ti.amount
,tp1.payer_cust_id
 from  ti  
 join tp1 on ti.txn_id = tp1.txn_id
 join tp2 on ti.txn_id = tp2.txn_id
) AS virtual_table GROUP BY hour(created_on), dt ORDER BY "Txns" DESC
LIMIT 10000;



================================================================================

-- Chart 8: Flipkart BBD hourly Gmv (ID: 2875)
-- Chart Type: echarts_timeseries_line
-- Dataset: Flipkart BBD Todays Metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT hour(created_on) AS hour, dt AS dt, sum(amount) AS "Gmv" 
FROM (with ti as (
select 
created_on,
txn_id,
amount
FROM hive.switch.txn_info_snapshot_v3
            WHERE dl_last_updated >= current_date - interval '01' day
            and date(created_on) >= current_date - interval '01' day
            and type in ('PAY','COLLECT')
            AND category in('VPA2MERCHANT')
            AND status in('SUCCESS','DEEMED')
            and lower(psp_handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi')
and(
    (type = 'COLLECT' and (business_type is null or business_type <> 'MANDATE'))
    or(type = 'PAY' and upper(channel_code) = 'PAYTM'
    and JSON_EXTRACT_SCALAR(extended_info, '$.initiationMode') in ('04','03'))
    or(type = 'PAY' and upper(channel_code) in ('ONLINE_3P_NATIVE')
    )
)

),
tp1 as (
select txn_id, vpa payer_vpa,handle payer_handle, scope_cust_id payer_cust_id, account_type,bank_code payer_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day 
and lower(handle) in ('paytm','ptyes','ptaxis','pthdfc','ptsbi') 
and participant_type = 'PAYER'
),
tp2 as (
select txn_id, vpa payee_vpa,handle payee_handle,bank_code payee_bank from 
hive.switch.txn_participants_snapshot_v3 p
where dl_last_updated >=  current_date - interval '01' day
and participant_type = 'PAYEE'
AND lower(vpa) IN (
'paytm-79192590@ptybl','paytm-79192716@ptybl','flipkart.hypg@kotakpay','paytm-64090553@paytm','paytm-64090553@ptybl',
'flipkartgrocery.payu@hdfcbank','idfcfirstbank.payu@mairtel','idfcbankloanrepayment.payu@hdfcbank','idfc.payu@icici',
       'flipkart.hyperpg@axb','flipkart.hypg@yespay','setu.flipkart@pineaxis','79003574@ptybl','fkrt@axl','fkrt@ybl','flipkart.payu@axisbank','flipkart.payu@hdfcbank','flipkart.payu@icici','flipkart1.payu@hdfcbank','flipkart1.payu@indus','flipkart1@indus','flipkart2020paytm@hdfcbank','flipkartinterne.payu@mairtel','flipkartinterne814.rzp@icici','flipkartinternetprivatelimited.rzp@hdfcbank','flipkartinternetprivatelimited28.paytm@hdfcbank','flipkartinternetprivatelimited59.paytm@hdfcbank','flipkartwholesale.cca@icici','mswipe.1400062924022657@kotak','mswipe.1400062924023153@kotak','paytm-56505013@paytm','paytm-56505013@ptybl','paytm-78824088@paytm','paytm-78824088@ptybl','sbipmopad.022211900326629-ym571606@sbipay','sbipmopad.02sob0000046783-yc019760@sbipay','flipkartinternetgroce.payu@mairtel','flipkartgrocery-12611431.payu@indus','paytm-78959480@ptybl','flipkartgiftcard.payu@hdfcbank','paytm-82335889@ptybl','flipkart12474444.payu@icici','flipkartpayments-8599699.payu@indus','flipkartinternetpriva.payu@mairtel','flipkart8599699.payu@icici','flipkart-135670.payu@indus','flipkart-149223.payu@indus','flipkart-12474444.payu@indus','flipkartpayments-173405.payu@indus','flipkart149223.payu@axisbank','flipkart8599699.payu@axisbank','flipkart12474444.payu@axisbank','flipkart173405.payu@axisbank','flipkart12611431.payu@axisbank','flipkart149223.payu@mairtel','flipkart12474444.payu@mairtel','flipkart173405.payu@mairtel','flipkart149223.payu@hdfcbank','flipkart173405.payu@hdfcbank','flipkart149223.payu@icici','flipkart12611431.payu@icici','flipkartpayin3.hypg@yespay','flipkart12474444.payu@axisbank','flipkart12611431.payu@axisbank')
)


select 
ti.created_on
,date(ti.created_on) dt
,ti.txn_id
,ti.amount
,tp1.payer_cust_id
 from  ti  
 join tp1 on ti.txn_id = tp1.txn_id
 join tp2 on ti.txn_id = tp2.txn_id
) AS virtual_table GROUP BY hour(created_on), dt ORDER BY "Gmv" DESC
LIMIT 10000;



================================================================================

-- Chart 9: NR Table updated As Of (ID: 3164)
-- Chart Type: big_number_total
-- Dataset: rolling_nrr_v1
-- Database: Trino
--------------------------------------------------------------------------------
SELECT max(nr_updated_as_of) AS "MAX(nr_updated_as_of)" 
FROM (SELECT max(txn_date) nr_updated_as_of from hive.user_paytm_payments.rolling_nrr_v1
) AS virtual_table
LIMIT 50000;



================================================================================

