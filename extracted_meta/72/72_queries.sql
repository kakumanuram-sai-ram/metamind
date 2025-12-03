-- SQL Queries for Dashboard: MHD Eval Dashboard
-- Dashboard ID: 72
-- Total Charts: 92
================================================================================

-- Chart 1: LLM L1 Metrics (ID: 480)
-- Chart Type: table
-- Dataset: sb_eval_llm_l1
-- Database: Trino
--------------------------------------------------------------------------------
SELECT out_key_problem_desc AS out_key_problem_desc, sum(active_sessions) AS "Active Sessions", AVG(avg_eval_score) * 100 AS "AVG Eval Score", AVG(avg_response_relevance_score) * 100 AS "AVG Response Relevance", CASE 
    WHEN (SUM(happy) + SUM(sad)) = 0 THEN NULL
    ELSE (SUM(happy) * 100.0) / (SUM(happy) + SUM(sad))
END AS "MSAT %", AVG(avg_empathy_score) * 100 AS "AVG Empathy Score", CASE 
    WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
    ELSE SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "+ve Sentiment Change %", AVG(avg_resolution_achieved) * 100 AS "AVG Resolution Achieved", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(intent_incoherence_count) * 100 / SUM(active_sessions)
END AS "Intent Detection Failed %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(agent_response_repetition) * 100 / SUM(active_sessions)
END AS "Bot Repetition %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(function_call_failed) * 100 / SUM(active_sessions)
END AS "Bot Failed %", AVG(avg_topic_drift) * 100 AS "AVG Topic Drift" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_llm_l1" 
WHERE date_ <= CURRENT_DATE - INTERVAL '1' DAY
ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY out_key_problem_desc ORDER BY "Active Sessions" DESC
LIMIT 1000;



================================================================================

-- Chart 2: LLM L1 Metrics (ID: 480)
-- Chart Type: table
-- Dataset: sb_eval_llm_l1
-- Database: Trino
--------------------------------------------------------------------------------
SELECT out_key_problem_desc AS out_key_problem_desc, sum(active_sessions) AS "Active Sessions", AVG(avg_eval_score) * 100 AS "AVG Eval Score", AVG(avg_response_relevance_score) * 100 AS "AVG Response Relevance", CASE 
    WHEN (SUM(happy) + SUM(sad)) = 0 THEN NULL
    ELSE (SUM(happy) * 100.0) / (SUM(happy) + SUM(sad))
END AS "MSAT %", AVG(avg_empathy_score) * 100 AS "AVG Empathy Score", CASE 
    WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
    ELSE SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "+ve Sentiment Change %", AVG(avg_resolution_achieved) * 100 AS "AVG Resolution Achieved", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(intent_incoherence_count) * 100 / SUM(active_sessions)
END AS "Intent Detection Failed %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(agent_response_repetition) * 100 / SUM(active_sessions)
END AS "Bot Repetition %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(function_call_failed) * 100 / SUM(active_sessions)
END AS "Bot Failed %", AVG(avg_topic_drift) * 100 AS "AVG Topic Drift" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_llm_l1" 
WHERE date_ <= CURRENT_DATE - INTERVAL '1' DAY
ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY out_key_problem_desc ORDER BY "Active Sessions" DESC
LIMIT 1000;



================================================================================

-- Chart 3: Analyzed + Eval Completed % - Complete Day (ID: 534)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bsoundbox', 'p4bAIBot') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Analyzed %" DESC
LIMIT 1000;



================================================================================

-- Chart 4: Analyzed + Eval Completed % - Complete Day (ID: 534)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bsoundbox', 'p4bAIBot') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Analyzed %" DESC
LIMIT 1000;



================================================================================

-- Chart 5: Daily Quality Metrics Trend (%) (ID: 537)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, (AVG(avg_eval_score)) * 100 AS "AVG Eval Score %", CASE WHEN SUM(active_sessions) = 0 THEN NULL ELSE
(SUM(active_sessions) - SUM(fd_tickets)) * 100 / SUM(active_sessions)
END AS "Bot Containment %", CASE WHEN (SUM(sad)+SUM(happy)) = 0 THEN NULL 
ELSE SUM(happy) * 100 /(SUM(sad)+SUM(happy)) END AS "MSAT %", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bsoundbox', 'p4bAIBot') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "AVG Eval Score %" DESC
LIMIT 10000;



================================================================================

-- Chart 6: Daily Quality Metrics Trend (%) (ID: 537)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, (AVG(avg_eval_score)) * 100 AS "AVG Eval Score %", CASE WHEN SUM(active_sessions) = 0 THEN NULL ELSE
(SUM(active_sessions) - SUM(fd_tickets)) * 100 / SUM(active_sessions)
END AS "Bot Containment %", CASE WHEN (SUM(sad)+SUM(happy)) = 0 THEN NULL 
ELSE SUM(happy) * 100 /(SUM(sad)+SUM(happy)) END AS "MSAT %", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bsoundbox', 'p4bAIBot') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "AVG Eval Score %" DESC
LIMIT 10000;



================================================================================

-- Chart 7: Final User Sentiment Analysis (ID: 538)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(neutral_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Neutral Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Positive Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(negative_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Negative Change %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change %" DESC
LIMIT 10000;



================================================================================

-- Chart 8: Final User Sentiment Analysis (ID: 538)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(neutral_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Neutral Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Positive Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(negative_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Negative Change %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change %" DESC
LIMIT 10000;



================================================================================

-- Chart 9: Final User Sentiment # (ID: 539)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, sum(neutral_user_sentiment) AS "Neutral Change #", sum(positive_user_sentiment) AS "Positive Change #", sum(negative_user_sentiment) AS "Negative Change #" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change #" DESC
LIMIT 10000;



================================================================================

-- Chart 10: Final User Sentiment # (ID: 539)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, sum(neutral_user_sentiment) AS "Neutral Change #", sum(positive_user_sentiment) AS "Positive Change #", sum(negative_user_sentiment) AS "Negative Change #" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change #" DESC
LIMIT 10000;



================================================================================

-- Chart 11: Bot Performance Metrics (ID: 540)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(agent_response_repetition) * 100.0 / SUM(eval_completed)
END AS "Bot Repetition %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(function_call_failed) * 100.0 / SUM(eval_completed)
END AS "Bot Failed %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(intent_incoherence_count) * 100.0 / SUM(eval_completed)
END AS "Intent Detection Failed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Bot Repetition %" DESC
LIMIT 10000;



================================================================================

-- Chart 12: Bot Performance Metrics (ID: 540)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(agent_response_repetition) * 100.0 / SUM(eval_completed)
END AS "Bot Repetition %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(function_call_failed) * 100.0 / SUM(eval_completed)
END AS "Bot Failed %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(intent_incoherence_count) * 100.0 / SUM(eval_completed)
END AS "Intent Detection Failed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Bot Repetition %" DESC
LIMIT 10000;



================================================================================

-- Chart 13: AVG Empathy Score + Resolution Achieved + Response Relevance (ID: 541)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, AVG(avg_empathy_score) * 100 AS "Avg Empathy Score", AVG(avg_resolution_achieved) * 100 AS "Avg Resolution Achieved", AVG(avg_response_relevance_score) * 100 AS "Avg Response Relevance" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Avg Empathy Score" DESC
LIMIT 10000;



================================================================================

-- Chart 14: AVG Empathy Score + Resolution Achieved + Response Relevance (ID: 541)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, AVG(avg_empathy_score) * 100 AS "Avg Empathy Score", AVG(avg_resolution_achieved) * 100 AS "Avg Resolution Achieved", AVG(avg_response_relevance_score) * 100 AS "Avg Response Relevance" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Avg Empathy Score" DESC
LIMIT 10000;



================================================================================

-- Chart 15: Overall Summary (ID: 542)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", sum(happy) AS "Happy Feedback", sum(sad) AS "Sad Feedback", SUM(ah_tickets) AS "Agent Tickets", SUM(service_tickets) AS "Service Tickets", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE (SUM(happy) + SUM(sad)) * 100 / SUM(active_sessions)
END AS "Feedback Rate %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(ah_tickets) * 100 / SUM(active_sessions)
END AS "Agent Handover %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(service_tickets) * 100 / SUM(active_sessions)
END AS "Service Ticket %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 16: Overall Summary (ID: 542)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", sum(happy) AS "Happy Feedback", sum(sad) AS "Sad Feedback", SUM(ah_tickets) AS "Agent Tickets", SUM(service_tickets) AS "Service Tickets", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE (SUM(happy) + SUM(sad)) * 100 / SUM(active_sessions)
END AS "Feedback Rate %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(ah_tickets) * 100 / SUM(active_sessions)
END AS "Agent Handover %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(service_tickets) * 100 / SUM(active_sessions)
END AS "Service Ticket %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bsoundbox', 'p4bAIBot'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 17: Analyzed + Eval Completed % - Complete Day (ID: 595)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Analyzed %" DESC
LIMIT 1000;



================================================================================

-- Chart 18: Analyzed + Eval Completed % - Complete Day (ID: 595)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Analyzed %" DESC
LIMIT 1000;



================================================================================

-- Chart 19: Daily Quality Metrics Trend (%) (ID: 596)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, (AVG(avg_eval_score)) * 100 AS "AVG Eval Score %", CASE WHEN SUM(active_sessions) = 0 THEN NULL ELSE
(SUM(active_sessions) - SUM(fd_tickets)) * 100 / SUM(active_sessions)
END AS "Bot Containment %", CASE WHEN (SUM(sad)+SUM(happy)) = 0 THEN NULL 
ELSE SUM(happy) * 100 /(SUM(sad)+SUM(happy)) END AS "MSAT %", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "AVG Eval Score %" DESC
LIMIT 10000;



================================================================================

-- Chart 20: Daily Quality Metrics Trend (%) (ID: 596)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, (AVG(avg_eval_score)) * 100 AS "AVG Eval Score %", CASE WHEN SUM(active_sessions) = 0 THEN NULL ELSE
(SUM(active_sessions) - SUM(fd_tickets)) * 100 / SUM(active_sessions)
END AS "Bot Containment %", CASE WHEN (SUM(sad)+SUM(happy)) = 0 THEN NULL 
ELSE SUM(happy) * 100 /(SUM(sad)+SUM(happy)) END AS "MSAT %", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "AVG Eval Score %" DESC
LIMIT 10000;



================================================================================

-- Chart 21: Final User Sentiment Analysis (ID: 598)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(neutral_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Neutral Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Positive Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(negative_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Negative Change %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change %" DESC
LIMIT 10000;



================================================================================

-- Chart 22: Final User Sentiment Analysis (ID: 598)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(neutral_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Neutral Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Positive Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(negative_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Negative Change %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change %" DESC
LIMIT 10000;



================================================================================

-- Chart 23: Final User Sentiment # (ID: 599)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, sum(neutral_user_sentiment) AS "Neutral Change #", sum(positive_user_sentiment) AS "Positive Change #", sum(negative_user_sentiment) AS "Negative Change #" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change #" DESC
LIMIT 10000;



================================================================================

-- Chart 24: Final User Sentiment # (ID: 599)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, sum(neutral_user_sentiment) AS "Neutral Change #", sum(positive_user_sentiment) AS "Positive Change #", sum(negative_user_sentiment) AS "Negative Change #" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change #" DESC
LIMIT 10000;



================================================================================

-- Chart 25: Bot Performance Metrics (ID: 600)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC;

================================================================================

-- Chart 26: Bot Performance Metrics (ID: 600)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC;

================================================================================

-- Chart 27: AVG Empathy Score + Resolution Achieved + Response Relevance (ID: 601)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, AVG(avg_empathy_score) * 100 AS "Avg Empathy Score", AVG(avg_resolution_achieved) * 100 AS "Avg Resolution Achieved", AVG(avg_response_relevance_score) * 100 AS "Avg Response Relevance" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Avg Empathy Score" DESC
LIMIT 10000;



================================================================================

-- Chart 28: AVG Empathy Score + Resolution Achieved + Response Relevance (ID: 601)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, AVG(avg_empathy_score) * 100 AS "Avg Empathy Score", AVG(avg_resolution_achieved) * 100 AS "Avg Resolution Achieved", AVG(avg_response_relevance_score) * 100 AS "Avg Response Relevance" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Avg Empathy Score" DESC
LIMIT 10000;



================================================================================

-- Chart 29: LLM L1 Metrics (ID: 602)
-- Chart Type: table
-- Dataset: sb_eval_llm_l1
-- Database: Trino
--------------------------------------------------------------------------------
SELECT out_key_problem_desc AS out_key_problem_desc, sum(active_sessions) AS "Active Sessions", SUM(eval_completed) * 100/ SUM(active_sessions) AS "Eval Completed %", AVG(avg_eval_score) * 100 AS "AVG Eval Score", AVG(avg_response_relevance_score) * 100 AS "AVG Response Relevance", CASE 
    WHEN (SUM(happy) + SUM(sad)) = 0 THEN NULL
    ELSE (SUM(happy) * 100.0) / (SUM(happy) + SUM(sad))
END AS "MSAT %", AVG(avg_empathy_score) * 100 AS "AVG Empathy Score", CASE 
    WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
    ELSE SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "+ve Sentiment Change %", AVG(avg_resolution_achieved) * 100 AS "AVG Resolution Achieved", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(intent_incoherence_count) * 100 / SUM(active_sessions)
END AS "Intent Detection Failed %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(agent_response_repetition) * 100 / SUM(active_sessions)
END AS "Bot Repetition %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(function_call_failed) * 100 / SUM(active_sessions)
END AS "Bot Failed %", AVG(avg_topic_drift) * 100 AS "AVG Topic Drift" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_llm_l1" 
WHERE date_ <= CURRENT_DATE - INTERVAL '1' DAY
ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY out_key_problem_desc ORDER BY "Active Sessions" DESC
LIMIT 1000;



================================================================================

-- Chart 30: LLM L1 Metrics (ID: 602)
-- Chart Type: table
-- Dataset: sb_eval_llm_l1
-- Database: Trino
--------------------------------------------------------------------------------
SELECT out_key_problem_desc AS out_key_problem_desc, sum(active_sessions) AS "Active Sessions", SUM(eval_completed) * 100/ SUM(active_sessions) AS "Eval Completed %", AVG(avg_eval_score) * 100 AS "AVG Eval Score", AVG(avg_response_relevance_score) * 100 AS "AVG Response Relevance", CASE 
    WHEN (SUM(happy) + SUM(sad)) = 0 THEN NULL
    ELSE (SUM(happy) * 100.0) / (SUM(happy) + SUM(sad))
END AS "MSAT %", AVG(avg_empathy_score) * 100 AS "AVG Empathy Score", CASE 
    WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
    ELSE SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "+ve Sentiment Change %", AVG(avg_resolution_achieved) * 100 AS "AVG Resolution Achieved", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(intent_incoherence_count) * 100 / SUM(active_sessions)
END AS "Intent Detection Failed %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(agent_response_repetition) * 100 / SUM(active_sessions)
END AS "Bot Repetition %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(function_call_failed) * 100 / SUM(active_sessions)
END AS "Bot Failed %", AVG(avg_topic_drift) * 100 AS "AVG Topic Drift" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_llm_l1" 
WHERE date_ <= CURRENT_DATE - INTERVAL '1' DAY
ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY out_key_problem_desc ORDER BY "Active Sessions" DESC
LIMIT 1000;



================================================================================

-- Chart 31: Overall Summary (ID: 603)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", sum(happy) AS "Happy Feedback", sum(sad) AS "Sad Feedback", SUM(ah_tickets) AS "Agent Tickets", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE (SUM(happy) + SUM(sad)) * 100 / SUM(active_sessions)
END AS "Feedback Rate %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(ah_tickets) * 100 / SUM(active_sessions)
END AS "Agent Handover %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 32: Overall Summary (ID: 603)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", sum(happy) AS "Happy Feedback", sum(sad) AS "Sad Feedback", SUM(ah_tickets) AS "Agent Tickets", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE (SUM(happy) + SUM(sad)) * 100 / SUM(active_sessions)
END AS "Feedback Rate %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(ah_tickets) * 100 / SUM(active_sessions)
END AS "Agent Handover %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bpayoutandsettlement'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 33: Analyzed + Eval Completed % - Complete Day (ID: 605)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC;

================================================================================

-- Chart 34: Analyzed + Eval Completed % - Complete Day (ID: 605)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC;

================================================================================

-- Chart 35: Daily Quality Metrics Trend (%) (ID: 607)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, (AVG(avg_eval_score)) * 100 AS "AVG Eval Score %", CASE WHEN SUM(active_sessions) = 0 THEN NULL ELSE
(SUM(active_sessions) - SUM(fd_tickets)) * 100 / SUM(active_sessions)
END AS "Bot Containment %", CASE WHEN (SUM(sad)+SUM(happy)) = 0 THEN NULL 
ELSE SUM(happy) * 100 /(SUM(sad)+SUM(happy)) END AS "MSAT %", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "AVG Eval Score %" DESC
LIMIT 10000;



================================================================================

-- Chart 36: Daily Quality Metrics Trend (%) (ID: 607)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, (AVG(avg_eval_score)) * 100 AS "AVG Eval Score %", CASE WHEN SUM(active_sessions) = 0 THEN NULL ELSE
(SUM(active_sessions) - SUM(fd_tickets)) * 100 / SUM(active_sessions)
END AS "Bot Containment %", CASE WHEN (SUM(sad)+SUM(happy)) = 0 THEN NULL 
ELSE SUM(happy) * 100 /(SUM(sad)+SUM(happy)) END AS "MSAT %", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "AVG Eval Score %" DESC
LIMIT 10000;



================================================================================

-- Chart 37: Final User Sentiment Analysis (ID: 608)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(neutral_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Neutral Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Positive Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(negative_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Negative Change %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change %" DESC
LIMIT 10000;



================================================================================

-- Chart 38: Final User Sentiment Analysis (ID: 608)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(neutral_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Neutral Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Positive Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(negative_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Negative Change %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change %" DESC
LIMIT 10000;



================================================================================

-- Chart 39: Final User Sentiment # (ID: 609)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, sum(neutral_user_sentiment) AS "Neutral Change #", sum(positive_user_sentiment) AS "Positive Change #", sum(negative_user_sentiment) AS "Negative Change #" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change #" DESC
LIMIT 10000;



================================================================================

-- Chart 40: Final User Sentiment # (ID: 609)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, sum(neutral_user_sentiment) AS "Neutral Change #", sum(positive_user_sentiment) AS "Positive Change #", sum(negative_user_sentiment) AS "Negative Change #" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change #" DESC
LIMIT 10000;



================================================================================

-- Chart 41: Bot Performance Metrics (ID: 610)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(agent_response_repetition) * 100.0 / SUM(eval_completed)
END AS "Bot Repetition %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(function_call_failed) * 100.0 / SUM(eval_completed)
END AS "Bot Failed %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(intent_incoherence_count) * 100.0 / SUM(eval_completed)
END AS "Intent Detection Failed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Bot Repetition %" DESC
LIMIT 10000;



================================================================================

-- Chart 42: Bot Performance Metrics (ID: 610)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(agent_response_repetition) * 100.0 / SUM(eval_completed)
END AS "Bot Repetition %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(function_call_failed) * 100.0 / SUM(eval_completed)
END AS "Bot Failed %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(intent_incoherence_count) * 100.0 / SUM(eval_completed)
END AS "Intent Detection Failed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Bot Repetition %" DESC
LIMIT 10000;



================================================================================

-- Chart 43: AVG Empathy Score + Resolution Achieved + Response Relevance (ID: 611)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, AVG(avg_empathy_score) * 100 AS "Avg Empathy Score", AVG(avg_resolution_achieved) * 100 AS "Avg Resolution Achieved", AVG(avg_response_relevance_score) * 100 AS "Avg Response Relevance" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Avg Empathy Score" DESC
LIMIT 10000;



================================================================================

-- Chart 44: AVG Empathy Score + Resolution Achieved + Response Relevance (ID: 611)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, AVG(avg_empathy_score) * 100 AS "Avg Empathy Score", AVG(avg_resolution_achieved) * 100 AS "Avg Resolution Achieved", AVG(avg_response_relevance_score) * 100 AS "Avg Response Relevance" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Avg Empathy Score" DESC
LIMIT 10000;



================================================================================

-- Chart 45: LLM L1 Metrics (ID: 612)
-- Chart Type: table
-- Dataset: sb_eval_llm_l1
-- Database: Trino
--------------------------------------------------------------------------------
SELECT out_key_problem_desc AS out_key_problem_desc, sum(active_sessions) AS "Active Sessions", SUM(eval_completed) * 100/ SUM(active_sessions) AS "Eval Completed %", AVG(avg_eval_score) * 100 AS "AVG Eval Score", AVG(avg_response_relevance_score) * 100 AS "AVG Response Relevance", CASE 
    WHEN (SUM(happy) + SUM(sad)) = 0 THEN NULL
    ELSE (SUM(happy) * 100.0) / (SUM(happy) + SUM(sad))
END AS "MSAT %", AVG(avg_empathy_score) * 100 AS "AVG Empathy Score", CASE 
    WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
    ELSE SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "+ve Sentiment Change %", AVG(avg_resolution_achieved) * 100 AS "AVG Resolution Achieved", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(intent_incoherence_count) * 100 / SUM(active_sessions)
END AS "Intent Detection Failed %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(agent_response_repetition) * 100 / SUM(active_sessions)
END AS "Bot Repetition %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(function_call_failed) * 100 / SUM(active_sessions)
END AS "Bot Failed %", AVG(avg_topic_drift) * 100 AS "AVG Topic Drift" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_llm_l1" 
WHERE date_ <= CURRENT_DATE - INTERVAL '1' DAY
ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY out_key_problem_desc ORDER BY "Active Sessions" DESC
LIMIT 1000;



================================================================================

-- Chart 46: LLM L1 Metrics (ID: 612)
-- Chart Type: table
-- Dataset: sb_eval_llm_l1
-- Database: Trino
--------------------------------------------------------------------------------
SELECT out_key_problem_desc AS out_key_problem_desc, sum(active_sessions) AS "Active Sessions", SUM(eval_completed) * 100/ SUM(active_sessions) AS "Eval Completed %", AVG(avg_eval_score) * 100 AS "AVG Eval Score", AVG(avg_response_relevance_score) * 100 AS "AVG Response Relevance", CASE 
    WHEN (SUM(happy) + SUM(sad)) = 0 THEN NULL
    ELSE (SUM(happy) * 100.0) / (SUM(happy) + SUM(sad))
END AS "MSAT %", AVG(avg_empathy_score) * 100 AS "AVG Empathy Score", CASE 
    WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
    ELSE SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "+ve Sentiment Change %", AVG(avg_resolution_achieved) * 100 AS "AVG Resolution Achieved", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(intent_incoherence_count) * 100 / SUM(active_sessions)
END AS "Intent Detection Failed %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(agent_response_repetition) * 100 / SUM(active_sessions)
END AS "Bot Repetition %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(function_call_failed) * 100 / SUM(active_sessions)
END AS "Bot Failed %", AVG(avg_topic_drift) * 100 AS "AVG Topic Drift" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_llm_l1" 
WHERE date_ <= CURRENT_DATE - INTERVAL '1' DAY
ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY out_key_problem_desc ORDER BY "Active Sessions" DESC
LIMIT 1000;



================================================================================

-- Chart 47: Overall Summary (ID: 613)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", sum(happy) AS "Happy Feedback", sum(sad) AS "Sad Feedback", SUM(ah_tickets) AS "Agent Tickets", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE (SUM(happy) + SUM(sad)) * 100 / SUM(active_sessions)
END AS "Feedback Rate %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(ah_tickets) * 100 / SUM(active_sessions)
END AS "Agent Handover %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 48: Overall Summary (ID: 613)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", sum(happy) AS "Happy Feedback", sum(sad) AS "Sad Feedback", SUM(ah_tickets) AS "Agent Tickets", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE (SUM(happy) + SUM(sad)) * 100 / SUM(active_sessions)
END AS "Feedback Rate %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(ah_tickets) * 100 / SUM(active_sessions)
END AS "Agent Handover %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bbusinessloan'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 49: Analyzed + Eval Completed % - Complete Day (ID: 615)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC;

================================================================================

-- Chart 50: Analyzed + Eval Completed % - Complete Day (ID: 615)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC;

================================================================================

-- Chart 51: Daily Quality Metrics Trend (%) (ID: 616)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, (AVG(avg_eval_score)) * 100 AS "AVG Eval Score %", CASE WHEN SUM(active_sessions) = 0 THEN NULL ELSE
(SUM(active_sessions) - SUM(fd_tickets)) * 100 / SUM(active_sessions)
END AS "Bot Containment %", CASE WHEN (SUM(sad)+SUM(happy)) = 0 THEN NULL 
ELSE SUM(happy) * 100 /(SUM(sad)+SUM(happy)) END AS "MSAT %", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "AVG Eval Score %" DESC
LIMIT 10000;



================================================================================

-- Chart 52: Daily Quality Metrics Trend (%) (ID: 616)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, (AVG(avg_eval_score)) * 100 AS "AVG Eval Score %", CASE WHEN SUM(active_sessions) = 0 THEN NULL ELSE
(SUM(active_sessions) - SUM(fd_tickets)) * 100 / SUM(active_sessions)
END AS "Bot Containment %", CASE WHEN (SUM(sad)+SUM(happy)) = 0 THEN NULL 
ELSE SUM(happy) * 100 /(SUM(sad)+SUM(happy)) END AS "MSAT %", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "AVG Eval Score %" DESC
LIMIT 10000;



================================================================================

-- Chart 53: Final User Sentiment Analysis (ID: 618)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(neutral_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Neutral Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Positive Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(negative_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Negative Change %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change %" DESC
LIMIT 10000;



================================================================================

-- Chart 54: Final User Sentiment Analysis (ID: 618)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(neutral_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Neutral Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Positive Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(negative_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Negative Change %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change %" DESC
LIMIT 10000;



================================================================================

-- Chart 55: Final User Sentiment # (ID: 622)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, sum(neutral_user_sentiment) AS "Neutral Change #", sum(positive_user_sentiment) AS "Positive Change #", sum(negative_user_sentiment) AS "Negative Change #" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change #" DESC
LIMIT 10000;



================================================================================

-- Chart 56: Final User Sentiment # (ID: 622)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, sum(neutral_user_sentiment) AS "Neutral Change #", sum(positive_user_sentiment) AS "Positive Change #", sum(negative_user_sentiment) AS "Negative Change #" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change #" DESC
LIMIT 10000;



================================================================================

-- Chart 57: Bot Performance Metrics (ID: 623)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(agent_response_repetition) * 100.0 / SUM(eval_completed)
END AS "Bot Repetition %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(function_call_failed) * 100.0 / SUM(eval_completed)
END AS "Bot Failed %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(intent_incoherence_count) * 100.0 / SUM(eval_completed)
END AS "Intent Detection Failed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Bot Repetition %" DESC
LIMIT 10000;



================================================================================

-- Chart 58: Bot Performance Metrics (ID: 623)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(agent_response_repetition) * 100.0 / SUM(eval_completed)
END AS "Bot Repetition %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(function_call_failed) * 100.0 / SUM(eval_completed)
END AS "Bot Failed %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(intent_incoherence_count) * 100.0 / SUM(eval_completed)
END AS "Intent Detection Failed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Bot Repetition %" DESC
LIMIT 10000;



================================================================================

-- Chart 59: AVG Empathy Score + Resolution Achieved + Response Relevance (ID: 624)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, AVG(avg_empathy_score) * 100 AS "Avg Empathy Score", AVG(avg_resolution_achieved) * 100 AS "Avg Resolution Achieved", AVG(avg_response_relevance_score) * 100 AS "Avg Response Relevance" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Avg Empathy Score" DESC
LIMIT 10000;



================================================================================

-- Chart 60: AVG Empathy Score + Resolution Achieved + Response Relevance (ID: 624)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, AVG(avg_empathy_score) * 100 AS "Avg Empathy Score", AVG(avg_resolution_achieved) * 100 AS "Avg Resolution Achieved", AVG(avg_response_relevance_score) * 100 AS "Avg Response Relevance" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Avg Empathy Score" DESC
LIMIT 10000;



================================================================================

-- Chart 61: LLM L1 Metrics (ID: 625)
-- Chart Type: table
-- Dataset: sb_eval_llm_l1
-- Database: Trino
--------------------------------------------------------------------------------
SELECT out_key_problem_desc AS out_key_problem_desc, sum(active_sessions) AS "Active Sessions", SUM(eval_completed) * 100/ SUM(active_sessions) AS "Eval Completed %", AVG(avg_eval_score) * 100 AS "AVG Eval Score", AVG(avg_response_relevance_score) * 100 AS "AVG Response Relevance", CASE 
    WHEN (SUM(happy) + SUM(sad)) = 0 THEN NULL
    ELSE (SUM(happy) * 100.0) / (SUM(happy) + SUM(sad))
END AS "MSAT %", AVG(avg_empathy_score) * 100 AS "AVG Empathy Score", CASE 
    WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
    ELSE SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "+ve Sentiment Change %", AVG(avg_resolution_achieved) * 100 AS "AVG Resolution Achieved", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(intent_incoherence_count) * 100 / SUM(active_sessions)
END AS "Intent Detection Failed %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(agent_response_repetition) * 100 / SUM(active_sessions)
END AS "Bot Repetition %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(function_call_failed) * 100 / SUM(active_sessions)
END AS "Bot Failed %", AVG(avg_topic_drift) * 100 AS "AVG Topic Drift" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_llm_l1" 
WHERE date_ <= CURRENT_DATE - INTERVAL '1' DAY
ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY out_key_problem_desc ORDER BY "Active Sessions" DESC
LIMIT 1000;



================================================================================

-- Chart 62: LLM L1 Metrics (ID: 625)
-- Chart Type: table
-- Dataset: sb_eval_llm_l1
-- Database: Trino
--------------------------------------------------------------------------------
SELECT out_key_problem_desc AS out_key_problem_desc, sum(active_sessions) AS "Active Sessions", SUM(eval_completed) * 100/ SUM(active_sessions) AS "Eval Completed %", AVG(avg_eval_score) * 100 AS "AVG Eval Score", AVG(avg_response_relevance_score) * 100 AS "AVG Response Relevance", CASE 
    WHEN (SUM(happy) + SUM(sad)) = 0 THEN NULL
    ELSE (SUM(happy) * 100.0) / (SUM(happy) + SUM(sad))
END AS "MSAT %", AVG(avg_empathy_score) * 100 AS "AVG Empathy Score", CASE 
    WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
    ELSE SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "+ve Sentiment Change %", AVG(avg_resolution_achieved) * 100 AS "AVG Resolution Achieved", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(intent_incoherence_count) * 100 / SUM(active_sessions)
END AS "Intent Detection Failed %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(agent_response_repetition) * 100 / SUM(active_sessions)
END AS "Bot Repetition %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(function_call_failed) * 100 / SUM(active_sessions)
END AS "Bot Failed %", AVG(avg_topic_drift) * 100 AS "AVG Topic Drift" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_llm_l1" 
WHERE date_ <= CURRENT_DATE - INTERVAL '1' DAY
ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY out_key_problem_desc ORDER BY "Active Sessions" DESC
LIMIT 1000;



================================================================================

-- Chart 63: Overall Summary (ID: 626)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", sum(happy) AS "Happy Feedback", sum(sad) AS "Sad Feedback", SUM(ah_tickets) AS "Agent Tickets", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE (SUM(happy) + SUM(sad)) * 100 / SUM(active_sessions)
END AS "Feedback Rate %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(ah_tickets) * 100 / SUM(active_sessions)
END AS "Agent Handover %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 64: Overall Summary (ID: 626)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", sum(happy) AS "Happy Feedback", sum(sad) AS "Sad Feedback", SUM(ah_tickets) AS "Agent Tickets", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE (SUM(happy) + SUM(sad)) * 100 / SUM(active_sessions)
END AS "Feedback Rate %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(ah_tickets) * 100 / SUM(active_sessions)
END AS "Agent Handover %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bprofile'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 65: Analyzed + Eval Completed % - Complete Day (ID: 628)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC;

================================================================================

-- Chart 66: Analyzed + Eval Completed % - Complete Day (ID: 628)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC;

================================================================================

-- Chart 67: Daily Quality Metrics Trend (%) (ID: 630)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, (AVG(avg_eval_score)) * 100 AS "AVG Eval Score %", CASE WHEN SUM(active_sessions) = 0 THEN NULL ELSE
(SUM(active_sessions) - SUM(fd_tickets)) * 100 / SUM(active_sessions)
END AS "Bot Containment %", CASE WHEN (SUM(sad)+SUM(happy)) = 0 THEN NULL 
ELSE SUM(happy) * 100 /(SUM(sad)+SUM(happy)) END AS "MSAT %", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "AVG Eval Score %" DESC
LIMIT 10000;



================================================================================

-- Chart 68: Daily Quality Metrics Trend (%) (ID: 630)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, (AVG(avg_eval_score)) * 100 AS "AVG Eval Score %", CASE WHEN SUM(active_sessions) = 0 THEN NULL ELSE
(SUM(active_sessions) - SUM(fd_tickets)) * 100 / SUM(active_sessions)
END AS "Bot Containment %", CASE WHEN (SUM(sad)+SUM(happy)) = 0 THEN NULL 
ELSE SUM(happy) * 100 /(SUM(sad)+SUM(happy)) END AS "MSAT %", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "AVG Eval Score %" DESC
LIMIT 10000;



================================================================================

-- Chart 69: Final User Sentiment Analysis (ID: 631)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(neutral_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Neutral Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Positive Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(negative_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Negative Change %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change %" DESC
LIMIT 10000;



================================================================================

-- Chart 70: Final User Sentiment Analysis (ID: 631)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(neutral_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Neutral Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Positive Change %", CASE WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
ELSE
SUM(negative_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "Negative Change %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change %" DESC
LIMIT 10000;



================================================================================

-- Chart 71: Final User Sentiment # (ID: 632)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, sum(neutral_user_sentiment) AS "Neutral Change #", sum(positive_user_sentiment) AS "Positive Change #", sum(negative_user_sentiment) AS "Negative Change #" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change #" DESC
LIMIT 10000;



================================================================================

-- Chart 72: Final User Sentiment # (ID: 632)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, sum(neutral_user_sentiment) AS "Neutral Change #", sum(positive_user_sentiment) AS "Positive Change #", sum(negative_user_sentiment) AS "Negative Change #" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Neutral Change #" DESC
LIMIT 10000;



================================================================================

-- Chart 73: Bot Performance Metrics (ID: 633)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(agent_response_repetition) * 100.0 / SUM(eval_completed)
END AS "Bot Repetition %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(function_call_failed) * 100.0 / SUM(eval_completed)
END AS "Bot Failed %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(intent_incoherence_count) * 100.0 / SUM(eval_completed)
END AS "Intent Detection Failed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Bot Repetition %" DESC
LIMIT 10000;



================================================================================

-- Chart 74: Bot Performance Metrics (ID: 633)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) AS hour_timestamp, CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(agent_response_repetition) * 100.0 / SUM(eval_completed)
END AS "Bot Repetition %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(function_call_failed) * 100.0 / SUM(eval_completed)
END AS "Bot Failed %", CASE
  WHEN SUM(eval_completed) = 0 THEN NULL
  ELSE SUM(intent_incoherence_count) * 100.0 / SUM(eval_completed)
END AS "Intent Detection Failed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(hour_timestamp AS TIMESTAMP)) ORDER BY "Bot Repetition %" DESC
LIMIT 10000;



================================================================================

-- Chart 75: AVG Empathy Score + Resolution Achieved + Response Relevance (ID: 634)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, AVG(avg_empathy_score) * 100 AS "Avg Empathy Score", AVG(avg_resolution_achieved) * 100 AS "Avg Resolution Achieved", AVG(avg_response_relevance_score) * 100 AS "Avg Response Relevance" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Avg Empathy Score" DESC
LIMIT 10000;



================================================================================

-- Chart 76: AVG Empathy Score + Resolution Achieved + Response Relevance (ID: 634)
-- Chart Type: echarts_timeseries_smooth
-- Dataset: soundbox_eval_metrics
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date_, AVG(avg_empathy_score) * 100 AS "Avg Empathy Score", AVG(avg_resolution_achieved) * 100 AS "Avg Resolution Achieved", AVG(avg_response_relevance_score) * 100 AS "Avg Response Relevance" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_l1_summary1" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY "Avg Empathy Score" DESC
LIMIT 10000;



================================================================================

-- Chart 77: LLM L1 Metrics (ID: 635)
-- Chart Type: table
-- Dataset: sb_eval_llm_l1
-- Database: Trino
--------------------------------------------------------------------------------
SELECT out_key_problem_desc AS out_key_problem_desc, sum(active_sessions) AS "Active Sessions", SUM(eval_completed) * 100/ SUM(active_sessions) AS "Eval Completed %", AVG(avg_eval_score) * 100 AS "AVG Eval Score", AVG(avg_response_relevance_score) * 100 AS "AVG Response Relevance", CASE 
    WHEN (SUM(happy) + SUM(sad)) = 0 THEN NULL
    ELSE (SUM(happy) * 100.0) / (SUM(happy) + SUM(sad))
END AS "MSAT %", AVG(avg_empathy_score) * 100 AS "AVG Empathy Score", CASE 
    WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
    ELSE SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "+ve Sentiment Change %", AVG(avg_resolution_achieved) * 100 AS "AVG Resolution Achieved", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(intent_incoherence_count) * 100 / SUM(active_sessions)
END AS "Intent Detection Failed %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(agent_response_repetition) * 100 / SUM(active_sessions)
END AS "Bot Repetition %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(function_call_failed) * 100 / SUM(active_sessions)
END AS "Bot Failed %", AVG(avg_topic_drift) * 100 AS "AVG Topic Drift" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_llm_l1" 
WHERE date_ <= CURRENT_DATE - INTERVAL '1' DAY
ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY out_key_problem_desc ORDER BY "Active Sessions" DESC
LIMIT 1000;



================================================================================

-- Chart 78: LLM L1 Metrics (ID: 635)
-- Chart Type: table
-- Dataset: sb_eval_llm_l1
-- Database: Trino
--------------------------------------------------------------------------------
SELECT out_key_problem_desc AS out_key_problem_desc, sum(active_sessions) AS "Active Sessions", SUM(eval_completed) * 100/ SUM(active_sessions) AS "Eval Completed %", AVG(avg_eval_score) * 100 AS "AVG Eval Score", AVG(avg_response_relevance_score) * 100 AS "AVG Response Relevance", CASE 
    WHEN (SUM(happy) + SUM(sad)) = 0 THEN NULL
    ELSE (SUM(happy) * 100.0) / (SUM(happy) + SUM(sad))
END AS "MSAT %", AVG(avg_empathy_score) * 100 AS "AVG Empathy Score", CASE 
    WHEN (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment)) = 0 THEN NULL
    ELSE SUM(positive_user_sentiment) * 100 / (SUM(positive_user_sentiment)+SUM(negative_user_sentiment)+SUM(neutral_user_sentiment))
END AS "+ve Sentiment Change %", AVG(avg_resolution_achieved) * 100 AS "AVG Resolution Achieved", CASE WHEN (SUM(eval_score_good) + SUM(eval_score_bad)) = 0 THEN NULL
ELSE SUM(eval_score_bad) * 100 / (SUM(eval_score_good) + SUM(eval_score_bad))
END AS "Bad Eval Share %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(intent_incoherence_count) * 100 / SUM(active_sessions)
END AS "Intent Detection Failed %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(agent_response_repetition) * 100 / SUM(active_sessions)
END AS "Bot Repetition %", CASE 
    WHEN SUM(active_sessions) = 0 THEN NULL
    ELSE SUM(function_call_failed) * 100 / SUM(active_sessions)
END AS "Bot Failed %", AVG(avg_topic_drift) * 100 AS "AVG Topic Drift" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_llm_l1" 
WHERE date_ <= CURRENT_DATE - INTERVAL '1' DAY
ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY out_key_problem_desc ORDER BY "Active Sessions" DESC
LIMIT 1000;



================================================================================

-- Chart 79: Overall Summary (ID: 636)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", sum(happy) AS "Happy Feedback", sum(sad) AS "Sad Feedback", SUM(ah_tickets) AS "Agent Tickets", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE (SUM(happy) + SUM(sad)) * 100 / SUM(active_sessions)
END AS "Feedback Rate %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(ah_tickets) * 100 / SUM(active_sessions)
END AS "Agent Handover %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 80: Overall Summary (ID: 636)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", sum(happy) AS "Happy Feedback", sum(sad) AS "Sad Feedback", SUM(ah_tickets) AS "Agent Tickets", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE (SUM(happy) + SUM(sad)) * 100 / SUM(active_sessions)
END AS "Feedback Rate %", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(ah_tickets) * 100 / SUM(active_sessions)
END AS "Agent Handover %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE ((cst_entity IN ('p4bwealth'))) GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 81: Device Eval Summary (ID: 638)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bsoundbox', 'p4bAIBot') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 82: Device Eval Summary (ID: 638)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bsoundbox', 'p4bAIBot') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 83: Payout & Settlement Eval Summary (ID: 640)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bpayoutandsettlement') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY MAX(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 84: Payout & Settlement Eval Summary (ID: 640)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bpayoutandsettlement') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY MAX(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 85: Profile Eval Summary (ID: 642)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bprofile') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY MAX(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 86: Profile Eval Summary (ID: 642)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bprofile') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY MAX(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 87: MHD Overall Eval Summary (ID: 644)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 88: MHD Overall Eval Summary (ID: 644)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY max(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 89: Business Loan Eval Summary (ID: 749)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bbusinessloan') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY MAX(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 90: Business Loan Eval Summary (ID: 749)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bbusinessloan') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY MAX(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 91: Wealth Eval Summary (ID: 750)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bwealth') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY MAX(date_) DESC
LIMIT 1000;



================================================================================

-- Chart 92: Wealth Eval Summary (ID: 750)
-- Chart Type: table
-- Dataset: sb_eval_completed
-- Database: Trino
--------------------------------------------------------------------------------
SELECT date_trunc('day', CAST(date_ AS TIMESTAMP)) AS date___, sum(active_sessions) AS "Active Sessions", sum(analyzed_sessions) AS "Analyzed Sessions", sum(eval_completed) AS "Eval Completed", CASE WHEN SUM(active_sessions) = 0 THEN NULL
ELSE SUM(analyzed_sessions) * 100 / SUM(active_sessions)
END AS "Analyzed %", CASE WHEN SUM(analyzed_sessions) = 0 THEN NULL
ELSE SUM(eval_completed) * 100 / SUM(analyzed_sessions)
END AS "Eval Completed %" 
FROM (SELECT * FROM "hive"."team_cst_mhd_product"."soundbox_eval_completed" ORDER BY 1, 2 DESC
) AS virtual_table 
WHERE cst_entity IN ('p4bwealth') GROUP BY date_trunc('day', CAST(date_ AS TIMESTAMP)) ORDER BY MAX(date_) DESC
LIMIT 1000;



================================================================================

