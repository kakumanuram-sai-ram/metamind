-- SQL Queries for Dashboard: Repeat Retention Dashboard
-- Dashboard ID: 249
-- Total Charts: 6
================================================================================

-- Chart 1: TG vs CG - MTD Retention Comparison (ID: 1457)
-- Chart Type: big_number_total
-- Dataset: Repeat Retention Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT sum(users*1.00) 
filter(
where life_time_asofnow = 1 
and UPI_Active_LM = 1
and UPI_Active_MTD =1)
/
sum(users*1.00) 
filter(where life_time_asofnow = 1 
and UPI_Active_LM = 1) AS "TG MTD Retention%" 
FROM (SELECT * from repeat_retention_dashboard_v1
) AS virtual_table
LIMIT 50000;



================================================================================

-- Chart 2: CG MTD Retention Rate (ID: 1458)
-- Chart Type: big_number_total
-- Dataset: Repeat Retention Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT sum(users*1.00) 
filter(
where life_time_asofnow = 0 
and UPI_Active_LM = 1
and UPI_Active_MTD =1)
/
sum(users*1.00) 
filter(where life_time_asofnow = 0 
and UPI_Active_LM = 1) AS "CG MTD Retention%" 
FROM (SELECT * from repeat_retention_dashboard_v1
) AS virtual_table
LIMIT 50000;



================================================================================

-- Chart 3: Monthly Active Users - TG vs CG by Feature (ID: 1460)
-- Chart Type: dist_bar
-- Dataset: Repeat Retention Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT feature AS feature, sum(users) filter(
where life_time_asofnow = 1 
and upi_active_mtd = 1) AS "TG_MTD_MAU", sum(users) 
filter(
where life_time_asofnow =0 
and upi_active_mtd = 1) AS "CG_MTD_MAU" 
FROM (SELECT * from repeat_retention_dashboard_v1
) AS virtual_table GROUP BY feature
LIMIT 10;



================================================================================

-- Chart 4: Transaction Per User (TPU) - TG vs CG (ID: 1461)
-- Chart Type: dist_bar
-- Dataset: Repeat Retention Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT feature AS feature, sum(upi_txns_mtd * 1.00)
filter(where life_time_asofnow = 1 
and upi_active_mtd = 1)
/
sum(users * 1.00) 
filter(where life_time_asofnow = 1
and upi_active_mtd = 1) AS "TG_MTD_TPU", sum(upi_txns_mtd * 1.00)
filter(
where life_time_asofnow = 0 
and upi_active_mtd = 1)
/
sum(users * 1.00) 
filter(
where life_time_asofnow =0 
and upi_active_mtd = 1) AS "CG_MTD_TPU" 
FROM (SELECT * from repeat_retention_dashboard_v1
) AS virtual_table GROUP BY feature
LIMIT 10;



================================================================================

-- Chart 5: User Distribution by Feature (ID: 1462)
-- Chart Type: pie
-- Dataset: Repeat Retention Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT * from repeat_retention_dashboard_v1 

================================================================================

-- Chart 6: L3M Active Users - Pre/Post Analysis (ID: 1463)
-- Chart Type: dist_bar
-- Dataset: Repeat Retention Dashboard
-- Database: Trino
--------------------------------------------------------------------------------
SELECT feature AS feature, sum(users) 
filter(
where
--life_time_asofnow =0 and 
lm = 1
and upi_active_llm = 1
and upi_active_lm = 1
and upi_active_mtd =1
) AS "Pre/Post-TG_L3M_Active", sum(users*1.00) 
filter(
where
life_time_asofnow =0
-- and 
-- lm = 1
and upi_active_llm = 1
and upi_active_lm = 1
and upi_active_mtd =1
) AS "Pre/Post-CG_L3M_Active" 
FROM (SELECT * from repeat_retention_dashboard_v1
) AS virtual_table GROUP BY feature
LIMIT 10;



================================================================================

