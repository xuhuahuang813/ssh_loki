#!/bin/bash

python bi_0_0_sql_process.py
python bi_0_1_sql_to_qrep.py

python bi_0_2_get_query_cardinalities.py --card_type pg --key_name expected
python bi_0_2_get_query_cardinalities.py --card_type actual --key_name actual
python bi_0_2_get_query_cardinalities.py --card_type total --key_name total


python bi_1_ParsingSQLs.py    

python bi_2_get_const_rowcounts.py 
python bi_3_loki.py
python bi_4_create_table.py 
python bi_5_eval_data.py

