-- SQL Queries for Dashboard: P2P Inward(VPA2VPA) Transaction
-- Dashboard ID: 842
-- Total Charts: 6
================================================================================

-- Chart 1: P2P Inward Transactions (ID: 4003)
-- Chart Type: table
-- Dataset: p2p_inward_hourly_reporting_dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT hour_ AS hour___, COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day)) AS "Yesterdays Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month)) AS "Last month same day Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date)) AS "Todays Txns", case when (COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000) = 0 then null else

(COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day))*1.0000) - 1
end  AS "today Vs Yesterday", case when (COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)  = 0 
then null else
(COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month))*1.0000) - 1
end AS "Today vs Last month Same Day" 
FROM (select * from user_paytm_payments.p2p_inward_hourly_reporting_dataset
) AS virtual_table GROUP BY hour_ ORDER BY AVG(hour_) ASC
LIMIT 1000;



================================================================================

-- Chart 2: P2P Inward Transaction (Payee Psp = yes) (ID: 4005)
-- Chart Type: table
-- Dataset: p2p_inward_hourly_reporting_dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT hour_ AS hour___, COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day)) AS "Yesterdays Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month)) AS "Last month same day Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date)) AS "Todays Txns", 
(COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day))*1.0000) - 1 AS "today Vs Yesterday", 
(COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month))*1.0000) - 1 AS "Today vs Last month Same Day" 
FROM (select * from user_paytm_payments.p2p_inward_hourly_reporting_dataset
) AS virtual_table 
WHERE payee_handle IN ('ptyes') AND ((hour_<=lastest_hour)) GROUP BY hour_ ORDER BY AVG(hour_) ASC
LIMIT 1000;



================================================================================

-- Chart 3: P2P Inward Transaction (Payee Psp = HDFC) (ID: 4036)
-- Chart Type: table
-- Dataset: p2p_inward_hourly_reporting_dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT hour_ AS hour___, COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day)) AS "Yesterdays Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month)) AS "Last month same day Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date)) AS "Todays Txns", 
(COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day))*1.0000) - 1 AS "today Vs Yesterday", 
(COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month))*1.0000) - 1 AS "Today vs Last month Same Day" 
FROM (select * from user_paytm_payments.p2p_inward_hourly_reporting_dataset
) AS virtual_table 
WHERE payee_handle IN ('pthdfc') AND ((hour_<=lastest_hour)) GROUP BY hour_ ORDER BY AVG(hour_) ASC
LIMIT 1000;



================================================================================

-- Chart 4: P2P Inward Transaction (Payee Psp = AXIS) (ID: 4040)
-- Chart Type: table
-- Dataset: p2p_inward_hourly_reporting_dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT hour_ AS hour___, COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day)) AS "Yesterdays Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month)) AS "Last month same day Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date)) AS "Todays Txns", 
(COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day))*1.0000) - 1 AS "today Vs Yesterday", 
(COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month))*1.0000) - 1 AS "Today vs Last month Same Day" 
FROM (select * from user_paytm_payments.p2p_inward_hourly_reporting_dataset
) AS virtual_table 
WHERE payee_handle IN ('ptaxis') AND ((hour_<=lastest_hour)) GROUP BY hour_ ORDER BY AVG(hour_) ASC
LIMIT 1000;



================================================================================

-- Chart 5: P2P Inward Transaction (Payee Psp = SBI) (ID: 4050)
-- Chart Type: table
-- Dataset: p2p_inward_hourly_reporting_dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT hour_ AS hour___, COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day)) AS "Yesterdays Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month)) AS "Last month same day Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date)) AS "Todays Txns", 
(COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day))*1.0000) - 1 AS "today Vs Yesterday", 
(COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month))*1.0000) - 1 AS "Today vs Last month Same Day" 
FROM (select * from user_paytm_payments.p2p_inward_hourly_reporting_dataset
) AS virtual_table 
WHERE payee_handle IN ('ptsbi') AND ((hour_<=lastest_hour)) GROUP BY hour_ ORDER BY AVG(hour_) ASC
LIMIT 1000;



================================================================================

-- Chart 6: P2P Inward Transactions comp (ID: 4267)
-- Chart Type: pivot_table_v2
-- Dataset: p2p_inward_hourly_reporting_dataset
-- Database: Trino
--------------------------------------------------------------------------------
SELECT case when 
lower(payer_handle) 
in('paytm',
'ptyes',
'ptaxis',
'pthdfc',
'ptsbi'
) then 'Payer = Paytm'
else 'Payer = Other'
End AS "Payer PsP", hour_ AS hour_, COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day)) AS "Yesterdays Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month)) AS "Last month same day Txns", COUNT(txn_id)filter(where date(created_on) = (current_Date)) AS "Todays Txns", 
case when 
COUNT(txn_id)filter(where date(created_on) = (current_Date)) >
COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day))
then
format('%s %.2f%%','🔼', abs((COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day))*1.0000) - 1) * 100)
ELSE
format('%s %.2f%%','🔽' ,abs((COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' day))*1.0000) - 1) * 100)
end AS "today Vs Yesterday", 
case when 
COUNT(txn_id)filter(where date(created_on) = (current_Date)) >
COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month))
then
format('%s %.2f%%','🔼', abs((COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month))*1.0000) - 1) * 100)
ELSE
format('%s %.2f%%','🔽' ,abs((COUNT(txn_id)filter(where date(created_on) = (current_Date))*1.0000)
/
(COUNT(txn_id)filter(where date(created_on) = (current_Date - interval '01' month))*1.0000) - 1) * 100)
end AS "Today vs Last month Same Day" 
FROM (select * from user_paytm_payments.p2p_inward_hourly_reporting_dataset
) AS virtual_table 
WHERE ((hour_<=lastest_hour)) GROUP BY case when 
lower(payer_handle) 
in('paytm',
'ptyes',
'ptaxis',
'pthdfc',
'ptsbi'
) then 'Payer = Paytm'
else 'Payer = Other'
End, hour_ ORDER BY "Yesterdays Txns" ASC
LIMIT 1000;



================================================================================

