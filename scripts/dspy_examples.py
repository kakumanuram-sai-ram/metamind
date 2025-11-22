"""
DSPy Examples for SourceTableColumnExtractor

Add your examples here. Each example should be a dspy.Example object
with all input and output fields populated.

To use these examples, import them in llm_extractor.py:
    from dspy_examples import EXAMPLES
"""
import dspy
import json

# ============================================================================
# EXAMPLE 1: Simple aggregation query
# ============================================================================
example1 = dspy.Example(
    sql_query="""SELECT "Day_" AS "Day_", month_ AS month_, sum(dau) AS "SUM(dau)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment = 'Overall' AND ((day_id>= date'2025-07-01'
and day(day_id)<= day(current_Date - interval '01' day))) GROUP BY "Day_", month_ ORDER BY "SUM(dau)" DESC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({
        "metrics": [],
        "columns": ["Day_", "month_", "SUM(dau)"],
        "chart_id": "1234",
        "chart_name": "Daily Active Users"
    }),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, segment, mau, dau",
    
    derived_columns_mapping=json.dumps({
        "mau_rolling": {
            "source_column": "mau",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        },
        "Day_": {
            "source_column": "day_id",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "date_Format(day_id, 'Day %d')"
        },
        "month_": {
            "source_column": "day_id",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "date_Format(day_id, '%b''%y')"
        },
        "SUM(dau)": {
            "source_column": "dau",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(dau)"
        }
    })
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 2: Complex query with CASE statements and window functions
# ============================================================================
example2 = dspy.Example(
    sql_query="""SELECT case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end AS "Segments_", date_trunc('month', day_id) AS "date_trunc('month', day_id)", (sum(mau*1.0000)/lag(sum(mau)) over(
partition by 
case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end
order by date_trunc('month',day_id)
))-1 AS prev_month_mau, sum(mau) AS "MAU__", sum(n_txns) AS "Txns", (sum(n_txns*1.0000)/lag(sum(n_txns)) over(
partition by 
case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end
order by date_trunc('month',day_id)
))-1 AS "prev_month_Txns", sum(gmv) AS "Gmv", (sum(gmv*1.0000)/lag(sum(gmv)) over(
partition by 
case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end
order by date_trunc('month',day_id)
))-1 AS "Prev_month_gmv" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE ((day(day_id)<= day(current_date - interval '01' day))) GROUP BY case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end, date_trunc('month', day_id) ORDER BY prev_month_mau ASC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({
        "metrics": [
            {"label": "MAU", "column": {"column_name": "mau"}},
            {"label": "Transactions", "column": {"column_name": "n_txns"}},
            {"label": "GMV", "column": {"column_name": "gmv"}}
        ],
        "columns": ["Segments_", "date_trunc('month', day_id)", "prev_month_mau", "MAU__", "Txns", "prev_month_Txns", "Gmv", "Prev_month_gmv"],
        "chart_id": "5678",
        "chart_name": "Monthly Metrics by Segment"
    }),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="segment, day_id, mau, n_txns, gmv, dau",
    
    derived_columns_mapping=json.dumps({
        "mau_rolling": {
            "source_column": "mau",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        },
        "Day_": {
            "source_column": "day_id",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "date_Format(day_id, 'Day %d')"
        },
        "month_": {
            "source_column": "day_id",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "date_Format(day_id, '%b''%y')"
        },
        "Segments_": {
            "source_column": "segment",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end"
        },
        "date_trunc('month', day_id)": {
            "source_column": "day_id",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "date_trunc('month', day_id)"
        },
        "prev_month_mau": {
            "source_column": "mau",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "(sum(mau*1.0000)/lag(sum(mau)) over(partition by case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end order by date_trunc('month',day_id)))-1"
        },
        "MAU__": {
            "source_column": "mau",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(mau)"
        },
        "Txns": {
            "source_column": "n_txns",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(n_txns)"
        },
        "prev_month_Txns": {
            "source_column": "n_txns",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "(sum(n_txns*1.0000)/lag(sum(n_txns)) over(partition by case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end order by date_trunc('month',day_id)))-1"
        },
        "Gmv": {
            "source_column": "gmv",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "sum(gmv)"
        },
        "Prev_month_gmv": {
            "source_column": "gmv",
            "source_table": "user_paytm_payments.upi_tracker_insight",
            "logic": "(sum(gmv*1.0000)/lag(sum(gmv)) over(partition by case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end order by date_trunc('month',day_id)))-1"
        }
    })
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# Add more examples below following the same format
# ============================================================================

"""
DSPy Examples for SourceTableColumnExtractor

Add your examples here. Each example should be a dspy.Example object
with all input and output fields populated.

To use these examples, import them in llm_extractor.py:
    from dspy_examples import EXAMPLES
"""
import dspy
import json

# ============================================================================
# EXAMPLE 3: UPI Tracker - UPI UPI Daily Trend (Chart ID: 1561)
# ============================================================================
example3 = dspy.Example(
    sql_query="""SELECT "Day_" AS "Day_", month_ AS month_, sum(dau) AS "SUM(dau)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment = 'Overall' AND ((day_id>= date'2025-07-01'
and day(day_id)<= day(current_Date - interval '01' day))) GROUP BY "Day_", month_ ORDER BY "SUM(dau)" DESC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }}
        ],
        "columns": [
                "Day_",
                "SUM(dau)",
                "month_"
        ],
        "chart_id": "1561",
        "chart_name": "UPI Tracker - UPI UPI Daily Trend"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="dau, day_id, mau, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(dau)": {{
                "source_column": "dau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(dau)"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 4: UPI Tracker - UPI MAU - MTD (Chart ID: 1563)
# ============================================================================
example4 = dspy.Example(
    sql_query="""SELECT date_trunc('month', CAST(day_id AS TIMESTAMP)) AS day_id, sum(mau) AS "SUM(mau)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment = 'Overall' AND ((day_id>= date'2025-07-01'
and day(day_id)<= day(current_Date - interval '01' day))) GROUP BY date_trunc('month', CAST(day_id AS TIMESTAMP))
LIMIT 50000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }}
        ],
        "columns": [
                "SUM(mau)",
                "TIMESTAMP"
        ],
        "chart_id": "1563",
        "chart_name": "UPI Tracker - UPI MAU - MTD"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, mau, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "date_trunc('month', day_id)": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_trunc('month', CAST(day_id AS TIMESTAMP))"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 5: UPI Tracker - UPI P2P MAU - MTD (Chart ID: 1564)
# ============================================================================
example5 = dspy.Example(
    sql_query="""SELECT date_trunc('month', CAST(day_id AS TIMESTAMP)) AS day_id, sum(mau) AS "SUM(mau)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment = 'P2P' AND ((day_id>= date'2025-07-01'
and day(day_id)<= day(current_Date - interval '01' day))) GROUP BY date_trunc('month', CAST(day_id AS TIMESTAMP))
LIMIT 50000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }}
        ],
        "columns": [
                "SUM(mau)",
                "TIMESTAMP"
        ],
        "chart_id": "1564",
        "chart_name": "UPI Tracker - UPI P2P MAU - MTD"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, mau, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "date_trunc('month', day_id)": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_trunc('month', CAST(day_id AS TIMESTAMP))"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 6: UPI Tracker - UPI P2M MAU - MTD (Chart ID: 1565)
# ============================================================================
example6 = dspy.Example(
    sql_query="""SELECT date_trunc('month', CAST(day_id AS TIMESTAMP)) AS day_id, sum(mau) AS "SUM(mau)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment = 'P2M' AND ((day_id>= date'2025-07-01'
and day(day_id)<= day(current_Date - interval '01' day))) GROUP BY date_trunc('month', CAST(day_id AS TIMESTAMP))
LIMIT 50000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }}
        ],
        "columns": [
                "SUM(mau)",
                "TIMESTAMP"
        ],
        "chart_id": "1565",
        "chart_name": "UPI Tracker - UPI P2M MAU - MTD"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, mau, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "date_trunc('month', day_id)": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_trunc('month', CAST(day_id AS TIMESTAMP))"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 7: UPI Tracker - UPI P2M Txns - MTD (Chart ID: 1566)
# ============================================================================
example7 = dspy.Example(
    sql_query="""SELECT date_trunc('month', CAST(day_id AS TIMESTAMP)) AS day_id, sum(n_txns) AS "Txns" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment = 'P2M' AND ((day_id>= date'2025-07-01'
and day(day_id)<= day(current_Date - interval '01' day))) GROUP BY date_trunc('month', CAST(day_id AS TIMESTAMP))
LIMIT 50000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }},
                {{
                        "label": "Transactions",
                        "column": {{
                                "column_name": "n_txns"
                        }}
                }}
        ],
        "columns": [
                "Txns",
                "TIMESTAMP"
        ],
        "chart_id": "1566",
        "chart_name": "UPI Tracker - UPI P2M Txns - MTD"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, mau, n_txns, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "Txns": {{
                "source_column": "n_txns",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(n_txns)"
        }},
        "date_trunc('month', day_id)": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_trunc('month', CAST(day_id AS TIMESTAMP))"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 8: UPI Tracker - UPI P2P Txns - MTD (Chart ID: 1567)
# ============================================================================
example8 = dspy.Example(
    sql_query="""SELECT date_trunc('month', CAST(day_id AS TIMESTAMP)) AS day_id, sum(n_txns) AS "Txns" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment = 'P2P' AND ((day_id>= date'2025-07-01'
and day(day_id)<= day(current_Date - interval '01' day))) GROUP BY date_trunc('month', CAST(day_id AS TIMESTAMP))
LIMIT 50000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }},
                {{
                        "label": "Transactions",
                        "column": {{
                                "column_name": "n_txns"
                        }}
                }}
        ],
        "columns": [
                "Txns",
                "TIMESTAMP"
        ],
        "chart_id": "1567",
        "chart_name": "UPI Tracker - UPI P2P Txns - MTD"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, mau, n_txns, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "Txns": {{
                "source_column": "n_txns",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(n_txns)"
        }},
        "date_trunc('month', day_id)": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_trunc('month', CAST(day_id AS TIMESTAMP))"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 9: UPI Tracker - UPI Txns - MTD (Chart ID: 1568)
# ============================================================================
example9 = dspy.Example(
    sql_query="""SELECT date_trunc('month', CAST(day_id AS TIMESTAMP)) AS day_id, sum(n_txns) AS "Txns" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment = 'Overall' AND ((day_id>= date'2025-07-01'
and day(day_id)<= day(current_Date - interval '01' day))) GROUP BY date_trunc('month', CAST(day_id AS TIMESTAMP))
LIMIT 50000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }},
                {{
                        "label": "Transactions",
                        "column": {{
                                "column_name": "n_txns"
                        }}
                }}
        ],
        "columns": [
                "Txns",
                "TIMESTAMP"
        ],
        "chart_id": "1568",
        "chart_name": "UPI Tracker - UPI Txns - MTD"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, mau, n_txns, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "Txns": {{
                "source_column": "n_txns",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(n_txns)"
        }},
        "date_trunc('month', day_id)": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_trunc('month', CAST(day_id AS TIMESTAMP))"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 10: UPI Tracker - UPI P2M Daily Trend (Chart ID: 1570)
# ============================================================================
example10 = dspy.Example(
    sql_query="""SELECT "Day_" AS "Day_", month_ AS month_, sum(dau) AS "SUM(dau)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment = 'P2M' AND ((day_id>= date'2025-07-01'
and day(day_id)<= day(current_Date - interval '01' day))) GROUP BY "Day_", month_ ORDER BY "SUM(dau)" DESC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }}
        ],
        "columns": [
                "Day_",
                "SUM(dau)",
                "month_"
        ],
        "chart_id": "1570",
        "chart_name": "UPI Tracker - UPI P2M Daily Trend"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="dau, day_id, mau, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(dau)": {{
                "source_column": "dau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(dau)"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 11: UPI Tracker - UPI P2P Daily Trend (Chart ID: 1571)
# ============================================================================
example11 = dspy.Example(
    sql_query="""SELECT "Day_" AS "Day_", month_ AS month_, sum(dau) AS "SUM(dau)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment = 'P2P' AND ((day_id>= date'2025-07-01'
and day(day_id)<= day(current_Date - interval '01' day))) GROUP BY "Day_", month_ ORDER BY "SUM(dau)" DESC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }}
        ],
        "columns": [
                "Day_",
                "SUM(dau)",
                "month_"
        ],
        "chart_id": "1571",
        "chart_name": "UPI Tracker - UPI P2P Daily Trend"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="dau, day_id, mau, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(dau)": {{
                "source_column": "dau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(dau)"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 12: UPI Tracker - Category Wise Summary (Chart ID: 1696)
# ============================================================================
example12 = dspy.Example(
    sql_query="""SELECT case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end AS "Segments_", date_trunc('day', CAST(day_id AS TIMESTAMP)) AS day_id, sum(dau) AS "DAU__", sum(mau_rolling) AS "MAU(Rolling)", sum(n_txns) AS "Txns", sum(gmv) AS "Gmv" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE day_id >= DATE '2025-11-01' AND day_id < DATE '2025-12-01' GROUP BY case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end, date_trunc('day', CAST(day_id AS TIMESTAMP)) ORDER BY sum(dau) DESC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }},
                {{
                        "label": "Transactions",
                        "column": {{
                                "column_name": "n_txns"
                        }}
                }},
                {{
                        "label": "GMV",
                        "column": {{
                                "column_name": "gmv"
                        }}
                }}
        ],
        "columns": [
                "Segments_",
                "DAU__",
                "MAU(Rolling)",
                "Txns",
                "Gmv",
                "TIMESTAMP"
        ],
        "chart_id": "1696",
        "chart_name": "UPI Tracker - Category Wise Summary"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="dau, day_id, gmv, mau, n_txns, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(dau)": {{
                "source_column": "dau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(dau)"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "Txns": {{
                "source_column": "n_txns",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(n_txns)"
        }},
        "Gmv": {{
                "source_column": "gmv",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(gmv)"
        }},
        "date_trunc('month', day_id)": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_trunc('month', CAST(day_id AS TIMESTAMP))"
        }},
        "Segments_": {{
                "source_column": "segment",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 13: UPI Tracker - Category Wise Summary MTD (Chart ID: 1697)
# ============================================================================
example13 = dspy.Example(
    sql_query="""SELECT case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end AS "Segments_", date_trunc('month', day_id) AS "date_trunc('month', day_id)", (sum(mau*1.0000)/lag(sum(mau)) over(
partition by 
case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end
order by date_trunc('month',day_id)
))-1 AS prev_month_mau, sum(mau) AS "MAU__", sum(n_txns) AS "Txns", (sum(n_txns*1.0000)/lag(sum(n_txns)) over(
partition by 
case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end
order by date_trunc('month',day_id)
))-1 AS "prev_month_Txns", sum(gmv) AS "Gmv", (sum(gmv*1.0000)/lag(sum(gmv)) over(
partition by 
case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end
order by date_trunc('month',day_id)
))-1 AS "Prev_month_gmv" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE ((day(day_id)<= day(current_date - interval '01' day))) GROUP BY case when segment='Overall' then 'A:Overall'
 when segment='P2P' then 'B:P2P'
 when segment='P2M' then 'C:P2M'
 when segment='SnP' then 'D:SnP'
 when segment='Online' then 'E:Online'
 when segment='Onus' then 'F:Onus'
 when segment='Paytm QR' then 'G:Paytm QR'
 when segment='3P QR' then 'H:3P QR'
 when segment='Intent' then 'I:Intent'
 when segment='P2M Collect' then 'J:P2M Collect'
 when segment='Mandate_Online' then 'K:Mandate_Online'
 when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates'
 when segment='Mandate_Onus' then 'M:Mandate_Onus'
 end, date_trunc('month', day_id) ORDER BY prev_month_mau ASC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }},
                {{
                        "label": "Transactions",
                        "column": {{
                                "column_name": "n_txns"
                        }}
                }},
                {{
                        "label": "GMV",
                        "column": {{
                                "column_name": "gmv"
                        }}
                }}
        ],
        "columns": [
                "Segments_",
                "date_trunc('month', day_id)",
                "MAU__",
                "Txns",
                "prev_month_Txns",
                "Gmv",
                "Prev_month_gmv",
                "prev_month_mau"
        ],
        "chart_id": "1697",
        "chart_name": "UPI Tracker - Category Wise Summary MTD"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, gmv, mau, n_txns, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "MAU__": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "Txns": {{
                "source_column": "n_txns",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(n_txns)"
        }},
        "Gmv": {{
                "source_column": "gmv",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(gmv)"
        }},
        "Segments_": {{
                "source_column": "segment",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end"
        }},
        "prev_month_mau": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "(sum(mau*1.0000)/lag(sum(mau)) over(partition by case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end order by date_trunc('month',day_id)))-1"
        }},
        "prev_month_Txns": {{
                "source_column": "n_txns",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "(sum(n_txns*1.0000)/lag(sum(n_txns)) over(partition by case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end order by date_trunc('month',day_id)))-1"
        }},
        "Prev_month_gmv": {{
                "source_column": "gmv",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "(sum(gmv*1.0000)/lag(sum(gmv)) over(partition by case when segment='Overall' then 'A:Overall' when segment='P2P' then 'B:P2P' when segment='P2M' then 'C:P2M' when segment='SnP' then 'D:SnP' when segment='Online' then 'E:Online' when segment='Onus' then 'F:Onus' when segment='Paytm QR' then 'G:Paytm QR' when segment='3P QR' then 'H:3P QR' when segment='Intent' then 'I:Intent' when segment='P2M Collect' then 'J:P2M Collect' when segment='Mandate_Online' then 'K:Mandate_Online' when segment='Onus_ExcMandates' then 'L:Onus_ExcMandates' when segment='Mandate_Onus' then 'M:Mandate_Onus' end order by date_trunc('month',day_id)))-1"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 14: MTD P2P P2M - UPI Tracker (Chart ID: 1718)
# ============================================================================
example14 = dspy.Example(
    sql_query="""SELECT month_ AS month_, segment AS segment, sum(n_txns) AS "SUM(n_txns)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment IN ('P2M', 'P2P') AND ((day_id>= date_Trunc('month',current_Date - interval '01' day - interval '03' month)) AND (day(day_id)<=day(current_Date - interval '01' day))) GROUP BY month_, segment ORDER BY "SUM(n_txns)" DESC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }},
                {{
                        "label": "Transactions",
                        "column": {{
                                "column_name": "n_txns"
                        }}
                }}
        ],
        "columns": [
                "SUM(n_txns)",
                "month_",
                "segment"
        ],
        "chart_id": "1718",
        "chart_name": "MTD P2P P2M - UPI Tracker"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, mau, n_txns, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "SUM(n_txns)": {{
                "source_column": "n_txns",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(n_txns)"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 15: MTD P2M L1 - UPI Tracker (Chart ID: 1719)
# ============================================================================
example15 = dspy.Example(
    sql_query="""SELECT month_ AS month_, segment AS segment, sum(n_txns) AS "SUM(n_txns)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment IN ('SnP', 'Online', 'Onus') AND ((day_id>= date_Trunc('month',current_Date - interval '01' day - interval '03' month)) AND (day(day_id)<=day(current_Date - interval '01' day))) GROUP BY month_, segment ORDER BY "SUM(n_txns)" DESC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }},
                {{
                        "label": "Transactions",
                        "column": {{
                                "column_name": "n_txns"
                        }}
                }}
        ],
        "columns": [
                "SUM(n_txns)",
                "month_",
                "segment"
        ],
        "chart_id": "1719",
        "chart_name": "MTD P2M L1 - UPI Tracker"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, mau, n_txns, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "SUM(n_txns)": {{
                "source_column": "n_txns",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(n_txns)"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 16: MTD P2M SNP L2 - UPI Tracker (Chart ID: 1720)
# ============================================================================
example16 = dspy.Example(
    sql_query="""SELECT month_ AS month_, segment AS segment, sum(n_txns) AS "SUM(n_txns)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment IN ('Paytm QR', '3P QR') AND ((day_id>= date_Trunc('month',current_Date - interval '01' day - interval '03' month)) AND (day(day_id)<=day(current_Date - interval '01' day))) GROUP BY month_, segment ORDER BY "SUM(n_txns)" DESC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }},
                {{
                        "label": "Transactions",
                        "column": {{
                                "column_name": "n_txns"
                        }}
                }}
        ],
        "columns": [
                "SUM(n_txns)",
                "month_",
                "segment"
        ],
        "chart_id": "1720",
        "chart_name": "MTD P2M SNP L2 - UPI Tracker"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, mau, n_txns, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "SUM(n_txns)": {{
                "source_column": "n_txns",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(n_txns)"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 17: MTD P2M Online L2 - UPI Tracker (Chart ID: 1721)
# ============================================================================
example17 = dspy.Example(
    sql_query="""SELECT month_ AS month_, segment AS segment, sum(n_txns) AS "SUM(n_txns)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment IN ('Intent', 'P2M Collect', 'Mandate_Online') AND ((day_id>= date_Trunc('month',current_Date - interval '01' day - interval '03' month)) AND (day(day_id)<=day(current_Date - interval '01' day))) GROUP BY month_, segment ORDER BY "SUM(n_txns)" DESC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }},
                {{
                        "label": "Transactions",
                        "column": {{
                                "column_name": "n_txns"
                        }}
                }}
        ],
        "columns": [
                "SUM(n_txns)",
                "month_",
                "segment"
        ],
        "chart_id": "1721",
        "chart_name": "MTD P2M Online L2 - UPI Tracker"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, mau, n_txns, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "SUM(n_txns)": {{
                "source_column": "n_txns",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(n_txns)"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# EXAMPLE 18: MTD P2M Onus L2 - UPI Tracker (Chart ID: 1722)
# ============================================================================
example18 = dspy.Example(
    sql_query="""SELECT month_ AS month_, segment AS segment, sum(n_txns) AS "SUM(n_txns)" 
FROM (select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight
UNION all
select *
,sum(mau) over(partition by segment,date_Trunc('month',day_id) order by segment,day_id) mau_rolling
,date_Format(day_id,'Day %d') Day_
,date_Format(day_id,'%b''%y') month_
from user_paytm_payments.upi_tracker_insight_cm
) AS virtual_table 
WHERE segment IN ('Onus_ExcMandates', 'Mandate_Onus') AND ((day_id>= date_Trunc('month',current_Date - interval '01' day - interval '03' month)) AND (day(day_id)<=day(current_Date - interval '01' day))) GROUP BY month_, segment ORDER BY "SUM(n_txns)" DESC
LIMIT 10000;""",
    
    chart_metadata=json.dumps({{
        "metrics": [
                {{
                        "label": "MAU",
                        "column": {{
                                "column_name": "mau"
                        }}
                }},
                {{
                        "label": "Transactions",
                        "column": {{
                                "column_name": "n_txns"
                        }}
                }}
        ],
        "columns": [
                "SUM(n_txns)",
                "month_",
                "segment"
        ],
        "chart_id": "1722",
        "chart_name": "MTD P2M Onus L2 - UPI Tracker"
}}),
    
    source_tables="user_paytm_payments.upi_tracker_insight, user_paytm_payments.upi_tracker_insight_cm",
    
    source_columns="day_id, mau, n_txns, segment",
    
    derived_columns_mapping=json.dumps({{
        "mau_rolling": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau) over(partition by segment, date_Trunc('month', day_id) order by segment, day_id)"
        }},
        "Day_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, 'Day %d')"
        }},
        "month_": {{
                "source_column": "day_id",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "date_Format(day_id, '%b''%y')"
        }},
        "SUM(mau)": {{
                "source_column": "mau",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(mau)"
        }},
        "SUM(n_txns)": {{
                "source_column": "n_txns",
                "source_table": "user_paytm_payments.upi_tracker_insight",
                "logic": "sum(n_txns)"
        }}
}})
).with_inputs('sql_query', 'chart_metadata')

# ============================================================================
# Export all examples as a list
# ============================================================================
EXAMPLES = [
        example1,example2, example3, example4, example5, example6, example7, example8, example9, example10, example11, example12, example13, example14, example15, example16, example17, example18
]


# Optional: Group examples by type for better organization
EXAMPLES_BY_TYPE = {
    "simple_aggregation": [example1],
    "complex_with_case_and_window": [example2],
    # Add more categories as needed
}

