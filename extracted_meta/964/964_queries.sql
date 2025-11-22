-- SQL Queries for Dashboard: UPI Traffic Dashboard
-- Dashboard ID: 964
-- Total Charts: 10
================================================================================

-- Chart 1: Home Page Traffic Dashboard - UPI Traffic Dashboard (ID: 4616)
-- Chart Type: pivot_table_v2
-- Dataset: Home Page Traffic Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT month_ AS month_, category_name AS category_name, sum(impressions) AS "Impressions__", sum(clicks) AS "Clicks", format('%.2f%%', sum(clicks*1.0000)/SUM(impressions*1.0000)*100)
 AS "CTR" 
FROM (with sub_category_data as
      (
        select a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name, sum(a.impressions) as impressions, sum(a.clicks) as clicks
        from
        (
          select dt,
          case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_,
          
           case
                  when view_type='banner-3_0' then 'Banner-3.0'
                  when view_type='banner-2_0' then 'banner-2_0'
                  when view_type='smart-icon-button' or view_id in (334426 ,339886)  then 'Smart-icon-button'
                  when view_type in ('smart-doodle-widget','smart-doodle-widget-v2') then 'Doodle'
                  when view_type='smart-icon-input-4xn' or view_id in (341290) then 'smart-icon-input-4xn'
                  when view_type in ('smart-reminder-icon','combo-reminder','smart-reminder') then 'Reminder'
                  when  view_id in (339769) then 'Featured'
                  when view_id in (338008) then 'My Paytm Icon'
                  when view_type='interstitial-floating' then 'Interstitial'
                  else view_type
              end as view_type
          
          ,
          sub_category_name,
          campaign_type_name,
          impressions,clicks,
          slot,View_id,
          category_name
          from  hive.team_measurement.banner_campaigns_mv_v1
          where (dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH)
                        and (CURRENT_DATE - INTERVAL '1' DAY))
           and storefront_id = 55486
        ) as a
        --where a.view_type is not NULL
        group by a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name
      )

  select sd.dt,sd.month_, sd.view_type, sd.sub_category_name,campaign_type_name,slot,View_id,category_name, sd.impressions, sd.clicks
      from sub_category_data as sd
      union all
      select dt,  
      case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_
      , 'Push' as view_type,null sub_category_name,null campaign_type_name,null slot, 0 View_id, 'UPI P2M' category_name, sum(total_delivered) as impressions, sum(total_opened) as clicks
      from  hive.team_measurement.push_campaigns_mv_v1
      where dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY - interval '01' month) and (CURRENT_DATE - INTERVAL '1' DAY)
        and category_names in ('UPI P2M')
        group by 1,2,3,4,5,6,7,8
) AS virtual_table 
WHERE month_ IS NOT NULL AND category_name IN ('UPI P2M') GROUP BY month_, category_name ORDER BY sum(impressions) DESC
LIMIT 1000;



================================================================================

-- Chart 2: Home Page Traffic Dashboard - DOD Impressions (ID: 4617)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: Home Page Traffic Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(dt AS TIMESTAMP)) AS dt, sum(clicks*1.0000)/SUM(impressions*1.0000)*100
 AS "CTR" 
FROM (with sub_category_data as
      (
        select a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name, sum(a.impressions) as impressions, sum(a.clicks) as clicks
        from
        (
          select dt,
          case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_,
          
           case
                  when view_type='banner-3_0' then 'Banner-3.0'
                  when view_type='banner-2_0' then 'banner-2_0'
                  when view_type='smart-icon-button' or view_id in (334426 ,339886)  then 'Smart-icon-button'
                  when view_type in ('smart-doodle-widget','smart-doodle-widget-v2') then 'Doodle'
                  when view_type='smart-icon-input-4xn' or view_id in (341290) then 'smart-icon-input-4xn'
                  when view_type in ('smart-reminder-icon','combo-reminder','smart-reminder') then 'Reminder'
                  when  view_id in (339769) then 'Featured'
                  when view_id in (338008) then 'My Paytm Icon'
                  when view_type='interstitial-floating' then 'Interstitial'
                  else view_type
              end as view_type
          
          ,
          sub_category_name,
          campaign_type_name,
          impressions,clicks,
          slot,View_id,
          category_name
          from  hive.team_measurement.banner_campaigns_mv_v1
          where (dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH)
                        and (CURRENT_DATE - INTERVAL '1' DAY))
           and storefront_id = 55486
        ) as a
        --where a.view_type is not NULL
        group by a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name
      )

  select sd.dt,sd.month_, sd.view_type, sd.sub_category_name,campaign_type_name,slot,View_id,category_name, sd.impressions, sd.clicks
      from sub_category_data as sd
      union all
      select dt,  
      case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_
      , 'Push' as view_type,null sub_category_name,null campaign_type_name,null slot, 0 View_id, 'UPI P2M' category_name, sum(total_delivered) as impressions, sum(total_opened) as clicks
      from  hive.team_measurement.push_campaigns_mv_v1
      where dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY - interval '01' month) and (CURRENT_DATE - INTERVAL '1' DAY)
        and category_names in ('UPI P2M')
        group by 1,2,3,4,5,6,7,8
) AS virtual_table 
WHERE month_ IN ('MTD') AND category_name IN ('UPI P2M') GROUP BY date_trunc('day', CAST(dt AS TIMESTAMP)) ORDER BY "CTR" DESC
LIMIT 1000;



================================================================================

-- Chart 3: Home Page Traffic Dashboard - DOD Impressions CTR (ID: 4618)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: Home Page Traffic Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(dt AS TIMESTAMP)) AS dt, SUM(impressions)
 AS "Impressions__" 
FROM (with sub_category_data as
      (
        select a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name, sum(a.impressions) as impressions, sum(a.clicks) as clicks
        from
        (
          select dt,
          case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_,
          
           case
                  when view_type='banner-3_0' then 'Banner-3.0'
                  when view_type='banner-2_0' then 'banner-2_0'
                  when view_type='smart-icon-button' or view_id in (334426 ,339886)  then 'Smart-icon-button'
                  when view_type in ('smart-doodle-widget','smart-doodle-widget-v2') then 'Doodle'
                  when view_type='smart-icon-input-4xn' or view_id in (341290) then 'smart-icon-input-4xn'
                  when view_type in ('smart-reminder-icon','combo-reminder','smart-reminder') then 'Reminder'
                  when  view_id in (339769) then 'Featured'
                  when view_id in (338008) then 'My Paytm Icon'
                  when view_type='interstitial-floating' then 'Interstitial'
                  else view_type
              end as view_type
          
          ,
          sub_category_name,
          campaign_type_name,
          impressions,clicks,
          slot,View_id,
          category_name
          from  hive.team_measurement.banner_campaigns_mv_v1
          where (dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH)
                        and (CURRENT_DATE - INTERVAL '1' DAY))
           and storefront_id = 55486
        ) as a
        --where a.view_type is not NULL
        group by a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name
      )

  select sd.dt,sd.month_, sd.view_type, sd.sub_category_name,campaign_type_name,slot,View_id,category_name, sd.impressions, sd.clicks
      from sub_category_data as sd
      union all
      select dt,  
      case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_
      , 'Push' as view_type,null sub_category_name,null campaign_type_name,null slot, 0 View_id, 'UPI P2M' category_name, sum(total_delivered) as impressions, sum(total_opened) as clicks
      from  hive.team_measurement.push_campaigns_mv_v1
      where dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY - interval '01' month) and (CURRENT_DATE - INTERVAL '1' DAY)
        and category_names in ('UPI P2M')
        group by 1,2,3,4,5,6,7,8
) AS virtual_table 
WHERE month_ IN ('MTD') AND category_name IN ('UPI P2M') GROUP BY date_trunc('day', CAST(dt AS TIMESTAMP)) ORDER BY SUM(impressions)
 DESC
LIMIT 1000;



================================================================================

-- Chart 4: Home Page Traffic Dashboard - DOD Clicks (ID: 4619)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: Home Page Traffic Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(dt AS TIMESTAMP)) AS dt, SUM(clicks)
 AS "Clicks__" 
FROM (with sub_category_data as
      (
        select a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name, sum(a.impressions) as impressions, sum(a.clicks) as clicks
        from
        (
          select dt,
          case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_,
          
           case
                  when view_type='banner-3_0' then 'Banner-3.0'
                  when view_type='banner-2_0' then 'banner-2_0'
                  when view_type='smart-icon-button' or view_id in (334426 ,339886)  then 'Smart-icon-button'
                  when view_type in ('smart-doodle-widget','smart-doodle-widget-v2') then 'Doodle'
                  when view_type='smart-icon-input-4xn' or view_id in (341290) then 'smart-icon-input-4xn'
                  when view_type in ('smart-reminder-icon','combo-reminder','smart-reminder') then 'Reminder'
                  when  view_id in (339769) then 'Featured'
                  when view_id in (338008) then 'My Paytm Icon'
                  when view_type='interstitial-floating' then 'Interstitial'
                  else view_type
              end as view_type
          
          ,
          sub_category_name,
          campaign_type_name,
          impressions,clicks,
          slot,View_id,
          category_name
          from  hive.team_measurement.banner_campaigns_mv_v1
          where (dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH)
                        and (CURRENT_DATE - INTERVAL '1' DAY))
           and storefront_id = 55486
        ) as a
        --where a.view_type is not NULL
        group by a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name
      )

  select sd.dt,sd.month_, sd.view_type, sd.sub_category_name,campaign_type_name,slot,View_id,category_name, sd.impressions, sd.clicks
      from sub_category_data as sd
      union all
      select dt,  
      case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_
      , 'Push' as view_type,null sub_category_name,null campaign_type_name,null slot, 0 View_id, 'UPI P2M' category_name, sum(total_delivered) as impressions, sum(total_opened) as clicks
      from  hive.team_measurement.push_campaigns_mv_v1
      where dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY - interval '01' month) and (CURRENT_DATE - INTERVAL '1' DAY)
        and category_names in ('UPI P2M')
        group by 1,2,3,4,5,6,7,8
) AS virtual_table 
WHERE month_ IN ('MTD') AND category_name IN ('UPI P2M') GROUP BY date_trunc('day', CAST(dt AS TIMESTAMP)) ORDER BY SUM(clicks)
 DESC
LIMIT 1000;



================================================================================

-- Chart 5: Home Page Traffic Dashboard - Banner 3.0 (ID: 4620)
-- Chart Type: table
-- Dataset: Home Page Traffic Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT category_name AS category_name, SUM(impressions)filter(where month_ = 'LMTD') AS "Impressions LMTD", SUM(clicks) filter(where month_ = 'LMTD') AS "Clicks LMTD", sum(clicks*1.0000) filter(where month_ = 'LMTD')
/SUM(impressions*1.0000) filter(where month_ = 'LMTD')
 AS "CTR LMTD", sum(impressions)filter(where month_ = 'MTD') AS "Impression MTD", sum(clicks) filter(where month_ = 'MTD') AS "Clicks MTD", sum(clicks*1.0000) filter(where month_ = 'MTD')
/SUM(impressions*1.0000) filter(where month_ = 'MTD')
 AS "CTR MTD", sum(clicks*1.0000) filter(where month_ = 'LMTD') AS "Impression LMTD" 
FROM (with sub_category_data as
      (
        select a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name, sum(a.impressions) as impressions, sum(a.clicks) as clicks
        from
        (
          select dt,
          case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_,
          
           case
                  when view_type='banner-3_0' then 'Banner-3.0'
                  when view_type='banner-2_0' then 'banner-2_0'
                  when view_type='smart-icon-button' or view_id in (334426 ,339886)  then 'Smart-icon-button'
                  when view_type in ('smart-doodle-widget','smart-doodle-widget-v2') then 'Doodle'
                  when view_type='smart-icon-input-4xn' or view_id in (341290) then 'smart-icon-input-4xn'
                  when view_type in ('smart-reminder-icon','combo-reminder','smart-reminder') then 'Reminder'
                  when  view_id in (339769) then 'Featured'
                  when view_id in (338008) then 'My Paytm Icon'
                  when view_type='interstitial-floating' then 'Interstitial'
                  else view_type
              end as view_type
          
          ,
          sub_category_name,
          campaign_type_name,
          impressions,clicks,
          slot,View_id,
          category_name
          from  hive.team_measurement.banner_campaigns_mv_v1
          where (dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH)
                        and (CURRENT_DATE - INTERVAL '1' DAY))
           and storefront_id = 55486
        ) as a
        --where a.view_type is not NULL
        group by a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name
      )

  select sd.dt,sd.month_, sd.view_type, sd.sub_category_name,campaign_type_name,slot,View_id,category_name, sd.impressions, sd.clicks
      from sub_category_data as sd
      union all
      select dt,  
      case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_
      , 'Push' as view_type,null sub_category_name,null campaign_type_name,null slot, 0 View_id, 'UPI P2M' category_name, sum(total_delivered) as impressions, sum(total_opened) as clicks
      from  hive.team_measurement.push_campaigns_mv_v1
      where dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY - interval '01' month) and (CURRENT_DATE - INTERVAL '1' DAY)
        and category_names in ('UPI P2M')
        group by 1,2,3,4,5,6,7,8
) AS virtual_table 
WHERE month_ IS NOT NULL AND view_type IN ('Banner-3.0', 'banner-3.0') GROUP BY category_name ORDER BY "Impressions LMTD" DESC
LIMIT 1000;



================================================================================

-- Chart 6: Home Page Traffic Dashboard - My Paytm Icon (ID: 4621)
-- Chart Type: table
-- Dataset: Home Page Traffic Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT case when category_name in ('PAYTM-UPI P2P','UPI P2M') then 'UPI' else category_name end  AS category_name, SUM(impressions)filter(where month_ = 'LMTD') AS "Impressions LMTD", SUM(clicks) filter(where month_ = 'LMTD') AS "Clicks LMTD", sum(clicks*1.0000) filter(where month_ = 'LMTD')
/SUM(impressions*1.0000) filter(where month_ = 'LMTD')
 AS "CTR LMTD", sum(impressions)filter(where month_ = 'MTD') AS "Impression MTD", sum(clicks) filter(where month_ = 'MTD') AS "Clicks MTD", sum(clicks*1.0000) filter(where month_ = 'MTD')
/SUM(impressions*1.0000) filter(where month_ = 'MTD')
 AS "CTR MTD", sum(clicks*1.0000) filter(where month_ = 'LMTD') AS "Impression LMTD" 
FROM (with sub_category_data as
      (
        select a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name, sum(a.impressions) as impressions, sum(a.clicks) as clicks
        from
        (
          select dt,
          case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_,
          
           case
                  when view_type='banner-3_0' then 'Banner-3.0'
                  when view_type='banner-2_0' then 'banner-2_0'
                  when view_type='smart-icon-button' or view_id in (334426 ,339886)  then 'Smart-icon-button'
                  when view_type in ('smart-doodle-widget','smart-doodle-widget-v2') then 'Doodle'
                  when view_type='smart-icon-input-4xn' or view_id in (341290) then 'smart-icon-input-4xn'
                  when view_type in ('smart-reminder-icon','combo-reminder','smart-reminder') then 'Reminder'
                  when  view_id in (339769) then 'Featured'
                  when view_id in (338008) then 'My Paytm Icon'
                  when view_type='interstitial-floating' then 'Interstitial'
                  else view_type
              end as view_type
          
          ,
          sub_category_name,
          campaign_type_name,
          impressions,clicks,
          slot,View_id,
          category_name
          from  hive.team_measurement.banner_campaigns_mv_v1
          where (dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH)
                        and (CURRENT_DATE - INTERVAL '1' DAY))
           and storefront_id = 55486
        ) as a
        --where a.view_type is not NULL
        group by a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name
      )

  select sd.dt,sd.month_, sd.view_type, sd.sub_category_name,campaign_type_name,slot,View_id,category_name, sd.impressions, sd.clicks
      from sub_category_data as sd
      union all
      select dt,  
      case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_
      , 'Push' as view_type,null sub_category_name,null campaign_type_name,null slot, 0 View_id, 'UPI P2M' category_name, sum(total_delivered) as impressions, sum(total_opened) as clicks
      from  hive.team_measurement.push_campaigns_mv_v1
      where dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY - interval '01' month) and (CURRENT_DATE - INTERVAL '1' DAY)
        and category_names in ('UPI P2M')
        group by 1,2,3,4,5,6,7,8
) AS virtual_table 
WHERE month_ IS NOT NULL AND "View_id" IN (338008, 339885, 341290, 341793, 336232, 347883, 343271, 345809, 341478, 346252, 346319) AND category_name IS NOT NULL GROUP BY case when category_name in ('PAYTM-UPI P2P','UPI P2M') then 'UPI' else category_name end  ORDER BY "Impressions LMTD" DESC
LIMIT 1000;



================================================================================

-- Chart 7: Home Page Traffic Dashboard - UPI P2M LAST MONTH (ID: 4630)
-- Chart Type: pivot_table_v2
-- Dataset: Home Page Traffic Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT case when day(dt) between 1 and 7 then 'Week 1'
 when day(dt) between 8 and 14 then 'Week 2'
 when day(dt) between 15 and 21 then 'Week 3'
 when day(dt) between 22 and 28 then 'Week 4'
 when day(dt)> 28 then 'Week 5'
End
 AS "Weeks", view_type AS view_type, SUM(impressions) AS "Impression", SUM(clicks) AS "Clicks", sum(clicks*1.0000) 
/SUM(impressions*1.0000) AS "CTR", format('%.2f%%',(
sum(impressions*1.0000)/
(sum(sum(impressions)) over(
partition by 
case when day(dt) between 1 and 7 then 'Week 1'
 when day(dt) between 8 and 14 then 'Week 2'
 when day(dt) between 15 and 21 then 'Week 3'
 when day(dt) between 22 and 28 then 'Week 4'
 when day(dt)> 28 then 'Week 5'
End
))
*100)) AS "Category Share" 
FROM (with sub_category_data as
      (
        select a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name, sum(a.impressions) as impressions, sum(a.clicks) as clicks
        from
        (
          select dt,
          case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_,
          
           case
                  when view_type='banner-3_0' then 'Banner-3.0'
                  when view_type='banner-2_0' then 'banner-2_0'
                  when view_type='smart-icon-button' or view_id in (334426 ,339886)  then 'Smart-icon-button'
                  when view_type in ('smart-doodle-widget','smart-doodle-widget-v2') then 'Doodle'
                  when view_type='smart-icon-input-4xn' or view_id in (341290) then 'smart-icon-input-4xn'
                  when view_type in ('smart-reminder-icon','combo-reminder','smart-reminder') then 'Reminder'
                  when  view_id in (339769) then 'Featured'
                  when view_id in (338008) then 'My Paytm Icon'
                  when view_type='interstitial-floating' then 'Interstitial'
                  else view_type
              end as view_type
          
          ,
          sub_category_name,
          campaign_type_name,
          impressions,clicks,
          slot,View_id,
          category_name
          from  hive.team_measurement.banner_campaigns_mv_v1
          where (dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH)
                        and (CURRENT_DATE - INTERVAL '1' DAY))
           and storefront_id = 55486
        ) as a
        --where a.view_type is not NULL
        group by a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name
      )

  select sd.dt,sd.month_, sd.view_type, sd.sub_category_name,campaign_type_name,slot,View_id,category_name, sd.impressions, sd.clicks
      from sub_category_data as sd
      union all
      select dt,  
      case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_
      , 'Push' as view_type,null sub_category_name,null campaign_type_name,null slot, 0 View_id, 'UPI P2M' category_name, sum(total_delivered) as impressions, sum(total_opened) as clicks
      from  hive.team_measurement.push_campaigns_mv_v1
      where dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY - interval '01' month) and (CURRENT_DATE - INTERVAL '1' DAY)
        and category_names in ('UPI P2M')
        group by 1,2,3,4,5,6,7,8
) AS virtual_table 
WHERE category_name = 'UPI P2M' AND ((date_Trunc('month',date(dt)) = date_trunc('month',
(current_Date - interval '01' day - interval '01' month)
))) GROUP BY case when day(dt) between 1 and 7 then 'Week 1'
 when day(dt) between 8 and 14 then 'Week 2'
 when day(dt) between 15 and 21 then 'Week 3'
 when day(dt) between 22 and 28 then 'Week 4'
 when day(dt)> 28 then 'Week 5'
End
, view_type ORDER BY "Impression" DESC
LIMIT 1000;



================================================================================

-- Chart 8: Home Page Traffic Dashboard - UPI P2M Current Month (ID: 4631)
-- Chart Type: pivot_table_v2
-- Dataset: Home Page Traffic Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT case when day(dt) between 1 and 7 then 'Week 1'
 when day(dt) between 8 and 14 then 'Week 2'
 when day(dt) between 15 and 21 then 'Week 3'
 when day(dt) between 22 and 28 then 'Week 4'
 when day(dt)> 28 then 'Week 5'
End
 AS "Weeks", view_type AS view_type, SUM(impressions) AS "Impression", SUM(clicks) AS "Clicks", format('%.2f%%',
sum(clicks*1.0000) 
/SUM(impressions*1.0000)
) AS "CTR", format('%.2f%%',(
sum(impressions*1.0000)/
(sum(sum(impressions)) over(
partition by 
case when day(dt) between 1 and 7 then 'Week 1'
 when day(dt) between 8 and 14 then 'Week 2'
 when day(dt) between 15 and 21 then 'Week 3'
 when day(dt) between 22 and 28 then 'Week 4'
 when day(dt)> 28 then 'Week 5'
End
))
*100)) AS "Category Share" 
FROM (with sub_category_data as
      (
        select a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name, sum(a.impressions) as impressions, sum(a.clicks) as clicks
        from
        (
          select dt,
          case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_,
          
           case
                  when view_type='banner-3_0' then 'Banner-3.0'
                  when view_type='banner-2_0' then 'banner-2_0'
                  when view_type='smart-icon-button' or view_id in (334426 ,339886)  then 'Smart-icon-button'
                  when view_type in ('smart-doodle-widget','smart-doodle-widget-v2') then 'Doodle'
                  when view_type='smart-icon-input-4xn' or view_id in (341290) then 'smart-icon-input-4xn'
                  when view_type in ('smart-reminder-icon','combo-reminder','smart-reminder') then 'Reminder'
                  when  view_id in (339769) then 'Featured'
                  when view_id in (338008) then 'My Paytm Icon'
                  when view_type='interstitial-floating' then 'Interstitial'
                  else view_type
              end as view_type
          
          ,
          sub_category_name,
          campaign_type_name,
          impressions,clicks,
          slot,View_id,
          category_name
          from  hive.team_measurement.banner_campaigns_mv_v1
          where (dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH)
                        and (CURRENT_DATE - INTERVAL '1' DAY))
           and storefront_id = 55486
        ) as a
        --where a.view_type is not NULL
        group by a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name
      )

  select sd.dt,sd.month_, sd.view_type, sd.sub_category_name,campaign_type_name,slot,View_id,category_name, sd.impressions, sd.clicks
      from sub_category_data as sd
      union all
      select dt,  
      case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_
      , 'Push' as view_type,null sub_category_name,null campaign_type_name,null slot, 0 View_id, 'UPI P2M' category_name, sum(total_delivered) as impressions, sum(total_opened) as clicks
      from  hive.team_measurement.push_campaigns_mv_v1
      where dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY - interval '01' month) and (CURRENT_DATE - INTERVAL '1' DAY)
        and category_names in ('UPI P2M')
        group by 1,2,3,4,5,6,7,8
) AS virtual_table 
WHERE category_name = 'UPI P2M' AND ((date_Trunc('month',date(dt)) = date_trunc('month',
(current_Date - interval '01' day)
))) GROUP BY case when day(dt) between 1 and 7 then 'Week 1'
 when day(dt) between 8 and 14 then 'Week 2'
 when day(dt) between 15 and 21 then 'Week 3'
 when day(dt) between 22 and 28 then 'Week 4'
 when day(dt)> 28 then 'Week 5'
End
, view_type ORDER BY "Impression" DESC
LIMIT 1000;



================================================================================

-- Chart 9: Home Page Traffic Dashboard - Banner 2.0 (ID: 4833)
-- Chart Type: table
-- Dataset: Home Page Traffic Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT category_name AS category_name, SUM(impressions)filter(where month_ = 'LMTD') AS "Impressions LMTD", SUM(clicks) filter(where month_ = 'LMTD') AS "Clicks LMTD", sum(clicks*1.0000) filter(where month_ = 'LMTD')
/SUM(impressions*1.0000) filter(where month_ = 'LMTD')
 AS "CTR LMTD", sum(impressions)filter(where month_ = 'MTD') AS "Impression MTD", sum(clicks) filter(where month_ = 'MTD') AS "Clicks MTD", sum(clicks*1.0000) filter(where month_ = 'MTD')
/SUM(impressions*1.0000) filter(where month_ = 'MTD')
 AS "CTR MTD", sum(clicks*1.0000) filter(where month_ = 'LMTD') AS "Impression LMTD" 
FROM (with sub_category_data as
      (
        select a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name, sum(a.impressions) as impressions, sum(a.clicks) as clicks
        from
        (
          select dt,
          case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_,
          
           case
                  when view_type='banner-3_0' then 'Banner-3.0'
                  when view_type='banner-2_0' then 'banner-2_0'
                  when view_type='smart-icon-button' or view_id in (334426 ,339886)  then 'Smart-icon-button'
                  when view_type in ('smart-doodle-widget','smart-doodle-widget-v2') then 'Doodle'
                  when view_type='smart-icon-input-4xn' or view_id in (341290) then 'smart-icon-input-4xn'
                  when view_type in ('smart-reminder-icon','combo-reminder','smart-reminder') then 'Reminder'
                  when  view_id in (339769) then 'Featured'
                  when view_id in (338008) then 'My Paytm Icon'
                  when view_type='interstitial-floating' then 'Interstitial'
                  else view_type
              end as view_type
          
          ,
          sub_category_name,
          campaign_type_name,
          impressions,clicks,
          slot,View_id,
          category_name
          from  hive.team_measurement.banner_campaigns_mv_v1
          where (dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH)
                        and (CURRENT_DATE - INTERVAL '1' DAY))
           and storefront_id = 55486
        ) as a
        --where a.view_type is not NULL
        group by a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name
      )

  select sd.dt,sd.month_, sd.view_type, sd.sub_category_name,campaign_type_name,slot,View_id,category_name, sd.impressions, sd.clicks
      from sub_category_data as sd
      union all
      select dt,  
      case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_
      , 'Push' as view_type,null sub_category_name,null campaign_type_name,null slot, 0 View_id, 'UPI P2M' category_name, sum(total_delivered) as impressions, sum(total_opened) as clicks
      from  hive.team_measurement.push_campaigns_mv_v1
      where dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY - interval '01' month) and (CURRENT_DATE - INTERVAL '1' DAY)
        and category_names in ('UPI P2M')
        group by 1,2,3,4,5,6,7,8
) AS virtual_table 
WHERE month_ IS NOT NULL AND view_type IN ('banner-2_0') GROUP BY category_name ORDER BY "Impressions LMTD" DESC
LIMIT 1000;



================================================================================

-- Chart 10: Home Page Traffic Dashboard - Category wise trend (ID: 4834)
-- Chart Type: pivot_table_v2
-- Dataset: Home Page Traffic Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT month_ AS month_, case WHEN category_name in ('PAYTM-UPI P2P','UPI P2M') then 'UPI'
else category_name end AS category_name, SUM(impressions) AS "Impression", SUM(clicks) AS "Clicks", format('%.2f%%',
try(sum(clicks*1.0000) 
/SUM(impressions*1.0000)
)
) AS "CTR", format('%.2f%%',(
sum(impressions*1.0000)/
(sum(sum(impressions)) over(
partition by 
month_
))
*100)) AS "Category Share" 
FROM (with sub_category_data as
      (
        select a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name, sum(a.impressions) as impressions, sum(a.clicks) as clicks
        from
        (
          select dt,
          case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_,
          
           case
                  when view_type='banner-3_0' then 'Banner-3.0'
                  when view_type='banner-2_0' then 'banner-2_0'
                  when view_type='smart-icon-button' or view_id in (334426 ,339886)  then 'Smart-icon-button'
                  when view_type in ('smart-doodle-widget','smart-doodle-widget-v2') then 'Doodle'
                  when view_type='smart-icon-input-4xn' or view_id in (341290) then 'smart-icon-input-4xn'
                  when view_type in ('smart-reminder-icon','combo-reminder','smart-reminder') then 'Reminder'
                  when  view_id in (339769) then 'Featured'
                  when view_id in (338008) then 'My Paytm Icon'
                  when view_type='interstitial-floating' then 'Interstitial'
                  else view_type
              end as view_type
          
          ,
          sub_category_name,
          campaign_type_name,
          impressions,clicks,
          slot,View_id,
          category_name
          from  hive.team_measurement.banner_campaigns_mv_v1
          where (dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH)
                        and (CURRENT_DATE - INTERVAL '1' DAY))
           and storefront_id = 55486
        ) as a
        --where a.view_type is not NULL
        group by a.dt,a.month_, a.view_type, a.sub_category_name,campaign_type_name,slot,View_id,category_name
      )

  select sd.dt,sd.month_, sd.view_type, sd.sub_category_name,campaign_type_name,slot,View_id,category_name, sd.impressions, sd.clicks
      from sub_category_data as sd
      union all
      select dt,  
      case
            when dt between DATE_TRUNC('MONTH', (CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) and
              ((CURRENT_DATE - INTERVAL '1' DAY) - interval '1' MONTH) then 'LMTD'
            when dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY) and (CURRENT_DATE - INTERVAL '1' DAY) then 'MTD'
          end as month_
      , 'Push' as view_type,null sub_category_name,null campaign_type_name,null slot, 0 View_id, 'UPI P2M' category_name, sum(total_delivered) as impressions, sum(total_opened) as clicks
      from  hive.team_measurement.push_campaigns_mv_v1
      where dt between DATE_TRUNC('MONTH', CURRENT_DATE - INTERVAL '1' DAY - interval '01' month) and (CURRENT_DATE - INTERVAL '1' DAY)
        and category_names in ('UPI P2M')
        group by 1,2,3,4,5,6,7,8
) AS virtual_table 
WHERE category_name IS NOT NULL AND month_ IS NOT NULL GROUP BY month_, case WHEN category_name in ('PAYTM-UPI P2P','UPI P2M') then 'UPI'
else category_name end ORDER BY "Impression" DESC
LIMIT 1000;



================================================================================

