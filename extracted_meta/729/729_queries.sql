-- SQL Queries for Dashboard: UPI SuperCash Burn Report
-- Dashboard ID: 729
-- Total Charts: 6
================================================================================

-- Chart 1: UPI  - MTD Cashback (ID: 3455)
-- Chart Type: big_number
-- Dataset: UPI SuperCashback dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('hour', CAST(updated_at AS TIMESTAMP)) AS updated_at, sum(cashburn) AS "Cashback" 
FROM (with burn as (
    select *,
      case
          when a.status = 1 and a.fulfillment_status = 3 then 'Given'
          when a.status = 1 and a.fulfillment_status = 2 then 'Processing'
          when a.status = 2 and a.fulfillment_status = 1 then 'Unscratched' -- need to remove 
          when a.status = 1 and a.fulfillment_status = 1 then 'Pending'
      end as status_1,
      (case
        when a.redemption_type = 'coins' then (a.amount/166.67)
        when a.redemption_type = 'goldcoins' then (a.amount/100)
        when a.redemption_type = 'upi' then (a.amount+0.2478)
        else a.amount
              end) as cashburn,
              json_extract_scalar(info, '$.scratchCardId') AS scratchCardId,
              json_extract_scalar(info, '$.scratched') AS scratched
            from
      (
          select dl_last_updated, created_at, updated_at, id, user_id, status,fulfillment_status, amount,info,redemption_type,campaign
          from  hive.promocard.supercash_task_snapshot_v3
          where 
          
          
          dl_last_updated >= date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and date(created_at) >= current_date  - interval '01' day  --date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and day(date(created_at))<= day(current_date  - interval '01' day)
          and status in (1,2)
          and fulfillment_status in (1,2,3)
          
          -- and campaign in ('UPI_3P_FLIPKART_30CB_11SEP25')
      ) a
)

select a.*,b.wallet from burn a
left join (select distinct wallet,campaign
                  from hive.code.campaign_snapshot_v3 as b
                  where dl_last_updated>= current_date- interval '62' day
                  ) b on a.campaign = b.campaign


-- select 
-- created_at,
-- -- case when date_diff('hour',created_at, b.scratched_at) is null then null
-- -- when date_diff('hour',created_at, b.scratched_at) <=23 then 'within 24 hr' else 'after 24 hr' end as time_diff,
-- -- status_1, 
-- -- scratched,
-- count(a.id) cards,
-- count(a.id) filter (where  scratched = 'true') card_scrached ,
-- count(a.id) filter (where  scratched = 'true' and date_diff('hour',created_at, b.scratched_at) <=23 ) card_scrached_same_Day ,
-- sum(cashburn) burn_issued,
-- sum(cashburn) filter (where  status_1 in('Given','Processing','Pending')) burn_processed
-- from burn a 
-- group by 1


      -- select * from hive.code.campaign_snapshot_v3 where  dl_last_updated >=  current_date  - interval '01' day limit 10
      
      -- as c
      -- on gt.campaign = c.campaign
) AS virtual_table 
WHERE created_at >= TIMESTAMP '2025-11-01 00:00:00.000000' AND created_at < TIMESTAMP '2025-12-01 00:00:00.000000' GROUP BY date_trunc('hour', CAST(updated_at AS TIMESTAMP))
LIMIT 50000;



================================================================================

-- Chart 2: UPI  - MTD Gratified Users (ID: 3456)
-- Chart Type: big_number
-- Dataset: UPI SuperCashback dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('hour', CAST(updated_at AS TIMESTAMP)) AS updated_at, count(DISTINCT user_id) AS "Cashback" 
FROM (with burn as (
    select *,
      case
          when a.status = 1 and a.fulfillment_status = 3 then 'Given'
          when a.status = 1 and a.fulfillment_status = 2 then 'Processing'
          when a.status = 2 and a.fulfillment_status = 1 then 'Unscratched' -- need to remove 
          when a.status = 1 and a.fulfillment_status = 1 then 'Pending'
      end as status_1,
      (case
        when a.redemption_type = 'coins' then (a.amount/166.67)
        when a.redemption_type = 'goldcoins' then (a.amount/100)
        when a.redemption_type = 'upi' then (a.amount+0.2478)
        else a.amount
              end) as cashburn,
              json_extract_scalar(info, '$.scratchCardId') AS scratchCardId,
              json_extract_scalar(info, '$.scratched') AS scratched
            from
      (
          select dl_last_updated, created_at, updated_at, id, user_id, status,fulfillment_status, amount,info,redemption_type,campaign
          from  hive.promocard.supercash_task_snapshot_v3
          where 
          
          
          dl_last_updated >= date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and date(created_at) >= current_date  - interval '01' day  --date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and day(date(created_at))<= day(current_date  - interval '01' day)
          and status in (1,2)
          and fulfillment_status in (1,2,3)
          
          -- and campaign in ('UPI_3P_FLIPKART_30CB_11SEP25')
      ) a
)

select a.*,b.wallet from burn a
left join (select distinct wallet,campaign
                  from hive.code.campaign_snapshot_v3 as b
                  where dl_last_updated>= current_date- interval '62' day
                  ) b on a.campaign = b.campaign


-- select 
-- created_at,
-- -- case when date_diff('hour',created_at, b.scratched_at) is null then null
-- -- when date_diff('hour',created_at, b.scratched_at) <=23 then 'within 24 hr' else 'after 24 hr' end as time_diff,
-- -- status_1, 
-- -- scratched,
-- count(a.id) cards,
-- count(a.id) filter (where  scratched = 'true') card_scrached ,
-- count(a.id) filter (where  scratched = 'true' and date_diff('hour',created_at, b.scratched_at) <=23 ) card_scrached_same_Day ,
-- sum(cashburn) burn_issued,
-- sum(cashburn) filter (where  status_1 in('Given','Processing','Pending')) burn_processed
-- from burn a 
-- group by 1


      -- select * from hive.code.campaign_snapshot_v3 where  dl_last_updated >=  current_date  - interval '01' day limit 10
      
      -- as c
      -- on gt.campaign = c.campaign
) AS virtual_table 
WHERE created_at >= TIMESTAMP '2025-11-01 00:00:00.000000' AND created_at < TIMESTAMP '2025-12-01 00:00:00.000000' GROUP BY date_trunc('hour', CAST(updated_at AS TIMESTAMP))
LIMIT 50000;



================================================================================

-- Chart 3: UPI  - MTD Daily Cashback (ID: 3457)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: UPI SuperCashback dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(updated_at AS TIMESTAMP)) AS updated_at, count(DISTINCT user_id) AS "Cashback" 
FROM (with burn as (
    select *,
      case
          when a.status = 1 and a.fulfillment_status = 3 then 'Given'
          when a.status = 1 and a.fulfillment_status = 2 then 'Processing'
          when a.status = 2 and a.fulfillment_status = 1 then 'Unscratched' -- need to remove 
          when a.status = 1 and a.fulfillment_status = 1 then 'Pending'
      end as status_1,
      (case
        when a.redemption_type = 'coins' then (a.amount/166.67)
        when a.redemption_type = 'goldcoins' then (a.amount/100)
        when a.redemption_type = 'upi' then (a.amount+0.2478)
        else a.amount
              end) as cashburn,
              json_extract_scalar(info, '$.scratchCardId') AS scratchCardId,
              json_extract_scalar(info, '$.scratched') AS scratched
            from
      (
          select dl_last_updated, created_at, updated_at, id, user_id, status,fulfillment_status, amount,info,redemption_type,campaign
          from  hive.promocard.supercash_task_snapshot_v3
          where 
          
          
          dl_last_updated >= date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and date(created_at) >= current_date  - interval '01' day  --date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and day(date(created_at))<= day(current_date  - interval '01' day)
          and status in (1,2)
          and fulfillment_status in (1,2,3)
          
          -- and campaign in ('UPI_3P_FLIPKART_30CB_11SEP25')
      ) a
)

select a.*,b.wallet from burn a
left join (select distinct wallet,campaign
                  from hive.code.campaign_snapshot_v3 as b
                  where dl_last_updated>= current_date- interval '62' day
                  ) b on a.campaign = b.campaign


-- select 
-- created_at,
-- -- case when date_diff('hour',created_at, b.scratched_at) is null then null
-- -- when date_diff('hour',created_at, b.scratched_at) <=23 then 'within 24 hr' else 'after 24 hr' end as time_diff,
-- -- status_1, 
-- -- scratched,
-- count(a.id) cards,
-- count(a.id) filter (where  scratched = 'true') card_scrached ,
-- count(a.id) filter (where  scratched = 'true' and date_diff('hour',created_at, b.scratched_at) <=23 ) card_scrached_same_Day ,
-- sum(cashburn) burn_issued,
-- sum(cashburn) filter (where  status_1 in('Given','Processing','Pending')) burn_processed
-- from burn a 
-- group by 1


      -- select * from hive.code.campaign_snapshot_v3 where  dl_last_updated >=  current_date  - interval '01' day limit 10
      
      -- as c
      -- on gt.campaign = c.campaign
) AS virtual_table 
WHERE updated_at >= TIMESTAMP '2025-11-01 00:00:00.000000' AND updated_at < TIMESTAMP '2025-12-01 00:00:00.000000' GROUP BY date_trunc('day', CAST(updated_at AS TIMESTAMP)) ORDER BY "Cashback" DESC
LIMIT 10000;



================================================================================

-- Chart 4: UPI  - MTD Daily Users (ID: 3458)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: UPI SuperCashback dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(updated_at AS TIMESTAMP)) AS updated_at, count(DISTINCT user_id) AS "COUNT_DISTINCT(user_id)" 
FROM (with burn as (
    select *,
      case
          when a.status = 1 and a.fulfillment_status = 3 then 'Given'
          when a.status = 1 and a.fulfillment_status = 2 then 'Processing'
          when a.status = 2 and a.fulfillment_status = 1 then 'Unscratched' -- need to remove 
          when a.status = 1 and a.fulfillment_status = 1 then 'Pending'
      end as status_1,
      (case
        when a.redemption_type = 'coins' then (a.amount/166.67)
        when a.redemption_type = 'goldcoins' then (a.amount/100)
        when a.redemption_type = 'upi' then (a.amount+0.2478)
        else a.amount
              end) as cashburn,
              json_extract_scalar(info, '$.scratchCardId') AS scratchCardId,
              json_extract_scalar(info, '$.scratched') AS scratched
            from
      (
          select dl_last_updated, created_at, updated_at, id, user_id, status,fulfillment_status, amount,info,redemption_type,campaign
          from  hive.promocard.supercash_task_snapshot_v3
          where 
          
          
          dl_last_updated >= date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and date(created_at) >= current_date  - interval '01' day  --date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and day(date(created_at))<= day(current_date  - interval '01' day)
          and status in (1,2)
          and fulfillment_status in (1,2,3)
          
          -- and campaign in ('UPI_3P_FLIPKART_30CB_11SEP25')
      ) a
)

select a.*,b.wallet from burn a
left join (select distinct wallet,campaign
                  from hive.code.campaign_snapshot_v3 as b
                  where dl_last_updated>= current_date- interval '62' day
                  ) b on a.campaign = b.campaign


-- select 
-- created_at,
-- -- case when date_diff('hour',created_at, b.scratched_at) is null then null
-- -- when date_diff('hour',created_at, b.scratched_at) <=23 then 'within 24 hr' else 'after 24 hr' end as time_diff,
-- -- status_1, 
-- -- scratched,
-- count(a.id) cards,
-- count(a.id) filter (where  scratched = 'true') card_scrached ,
-- count(a.id) filter (where  scratched = 'true' and date_diff('hour',created_at, b.scratched_at) <=23 ) card_scrached_same_Day ,
-- sum(cashburn) burn_issued,
-- sum(cashburn) filter (where  status_1 in('Given','Processing','Pending')) burn_processed
-- from burn a 
-- group by 1


      -- select * from hive.code.campaign_snapshot_v3 where  dl_last_updated >=  current_date  - interval '01' day limit 10
      
      -- as c
      -- on gt.campaign = c.campaign
) AS virtual_table 
WHERE updated_at >= TIMESTAMP '2025-11-01 00:00:00.000000' AND updated_at < TIMESTAMP '2025-12-01 00:00:00.000000' GROUP BY date_trunc('day', CAST(updated_at AS TIMESTAMP)) ORDER BY "COUNT_DISTINCT(user_id)" DESC
LIMIT 10000;



================================================================================

-- Chart 5: UPI  - Daily Updated Campaign Wise Burn summary (ID: 3459)
-- Chart Type: table
-- Dataset: UPI SuperCashback dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date(dl_last_updated) AS "Date", campaign AS campaign, status_1 AS "Status", wallet AS wallet, redemption_type AS redemption_type, count(DISTINCT user_id) AS "#Users", sum(cashburn) AS "SUM(cashburn)" 
FROM (with burn as (
    select *,
      case
          when a.status = 1 and a.fulfillment_status = 3 then 'Given'
          when a.status = 1 and a.fulfillment_status = 2 then 'Processing'
          when a.status = 2 and a.fulfillment_status = 1 then 'Unscratched' -- need to remove 
          when a.status = 1 and a.fulfillment_status = 1 then 'Pending'
      end as status_1,
      (case
        when a.redemption_type = 'coins' then (a.amount/166.67)
        when a.redemption_type = 'goldcoins' then (a.amount/100)
        when a.redemption_type = 'upi' then (a.amount+0.2478)
        else a.amount
              end) as cashburn,
              json_extract_scalar(info, '$.scratchCardId') AS scratchCardId,
              json_extract_scalar(info, '$.scratched') AS scratched
            from
      (
          select dl_last_updated, created_at, updated_at, id, user_id, status,fulfillment_status, amount,info,redemption_type,campaign
          from  hive.promocard.supercash_task_snapshot_v3
          where 
          
          
          dl_last_updated >= date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and date(created_at) >= current_date  - interval '01' day  --date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and day(date(created_at))<= day(current_date  - interval '01' day)
          and status in (1,2)
          and fulfillment_status in (1,2,3)
          
          -- and campaign in ('UPI_3P_FLIPKART_30CB_11SEP25')
      ) a
)

select a.*,b.wallet from burn a
left join (select distinct wallet,campaign
                  from hive.code.campaign_snapshot_v3 as b
                  where dl_last_updated>= current_date- interval '62' day
                  ) b on a.campaign = b.campaign


-- select 
-- created_at,
-- -- case when date_diff('hour',created_at, b.scratched_at) is null then null
-- -- when date_diff('hour',created_at, b.scratched_at) <=23 then 'within 24 hr' else 'after 24 hr' end as time_diff,
-- -- status_1, 
-- -- scratched,
-- count(a.id) cards,
-- count(a.id) filter (where  scratched = 'true') card_scrached ,
-- count(a.id) filter (where  scratched = 'true' and date_diff('hour',created_at, b.scratched_at) <=23 ) card_scrached_same_Day ,
-- sum(cashburn) burn_issued,
-- sum(cashburn) filter (where  status_1 in('Given','Processing','Pending')) burn_processed
-- from burn a 
-- group by 1


      -- select * from hive.code.campaign_snapshot_v3 where  dl_last_updated >=  current_date  - interval '01' day limit 10
      
      -- as c
      -- on gt.campaign = c.campaign
) AS virtual_table GROUP BY date(dl_last_updated), campaign, status_1, wallet, redemption_type ORDER BY "#Users" DESC
LIMIT 10000;



================================================================================

-- Chart 6: UPI  - Daily by Created Date Campaign Wise Burn Summary (ID: 3460)
-- Chart Type: table
-- Dataset: UPI SuperCashback dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date(created_at) AS "Date", campaign AS campaign, status_1 AS "Status", wallet AS wallet, redemption_type AS redemption_type, count(DISTINCT user_id) AS "#Users", sum(cashburn) AS "SUM(cashburn)" 
FROM (with burn as (
    select *,
      case
          when a.status = 1 and a.fulfillment_status = 3 then 'Given'
          when a.status = 1 and a.fulfillment_status = 2 then 'Processing'
          when a.status = 2 and a.fulfillment_status = 1 then 'Unscratched' -- need to remove 
          when a.status = 1 and a.fulfillment_status = 1 then 'Pending'
      end as status_1,
      (case
        when a.redemption_type = 'coins' then (a.amount/166.67)
        when a.redemption_type = 'goldcoins' then (a.amount/100)
        when a.redemption_type = 'upi' then (a.amount+0.2478)
        else a.amount
              end) as cashburn,
              json_extract_scalar(info, '$.scratchCardId') AS scratchCardId,
              json_extract_scalar(info, '$.scratched') AS scratched
            from
      (
          select dl_last_updated, created_at, updated_at, id, user_id, status,fulfillment_status, amount,info,redemption_type,campaign
          from  hive.promocard.supercash_task_snapshot_v3
          where 
          
          
          dl_last_updated >= date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and date(created_at) >= current_date  - interval '01' day  --date_trunc('month',current_date  - interval '01' day - interval  '01' month)
          --and day(date(created_at))<= day(current_date  - interval '01' day)
          and status in (1,2)
          and fulfillment_status in (1,2,3)
          
          -- and campaign in ('UPI_3P_FLIPKART_30CB_11SEP25')
      ) a
)

select a.*,b.wallet from burn a
left join (select distinct wallet,campaign
                  from hive.code.campaign_snapshot_v3 as b
                  where dl_last_updated>= current_date- interval '62' day
                  ) b on a.campaign = b.campaign


-- select 
-- created_at,
-- -- case when date_diff('hour',created_at, b.scratched_at) is null then null
-- -- when date_diff('hour',created_at, b.scratched_at) <=23 then 'within 24 hr' else 'after 24 hr' end as time_diff,
-- -- status_1, 
-- -- scratched,
-- count(a.id) cards,
-- count(a.id) filter (where  scratched = 'true') card_scrached ,
-- count(a.id) filter (where  scratched = 'true' and date_diff('hour',created_at, b.scratched_at) <=23 ) card_scrached_same_Day ,
-- sum(cashburn) burn_issued,
-- sum(cashburn) filter (where  status_1 in('Given','Processing','Pending')) burn_processed
-- from burn a 
-- group by 1


      -- select * from hive.code.campaign_snapshot_v3 where  dl_last_updated >=  current_date  - interval '01' day limit 10
      
      -- as c
      -- on gt.campaign = c.campaign
) AS virtual_table 
WHERE ((date(created_at) >= date_trunc('month', current_date - interval '01' day))) GROUP BY date(created_at), campaign, status_1, wallet, redemption_type ORDER BY "#Users" DESC
LIMIT 10000;



================================================================================

