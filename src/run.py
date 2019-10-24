from src.feature_extraction.extract_features import *
from src.training.train_and_test import *
from src.internal_parameters import *

dataset = load_dataset('/home/sunji/')
column2pos, indexes_id, tables_id, columns_id, physic_ops_id, compare_ops_id, bool_ops_id = prepare_dataset(dataset)
print ('data prepared')
word_vectors = load_dictionary('/home/sunji/learnedcardinality/string_words/wordvectors_updated.kv')
print ('word_vectors loaded')
min_max_column = load_numeric_min_max('/home/sunji/learnedcardinality/min_max_vals.json')
print ('min_max loaded')
index_total_num = len(indexes_id)
table_total_num = len(tables_id)
column_total_num = len(columns_id)
physic_op_total_num = len(physic_ops_id)
compare_ops_total_num = len(compare_ops_id)
bool_ops_total_num = len(bool_ops_id)
condition_op_dim = bool_ops_total_num + compare_ops_total_num+column_total_num+1000
condition_op_dim_pro = bool_ops_total_num + column_total_num + 3
plan_node_max_num, condition_max_num, cost_label_min, cost_label_max, card_label_min, card_label_max = obtain_upper_bound_query_size('/home/sunji/learnedcardinality/train_100k_real_plans_seq_sample.json')
print ('query upper size prepared')

parameters = Parameters(condition_max_num, indexes_id, tables_id, columns_id, physic_ops_id, column_total_num,
                        table_total_num, index_total_num, physic_op_total_num, condition_op_dim, compare_ops_id, bool_ops_id,
                        bool_ops_total_num, compare_ops_total_num, dataset, min_max_column, word_vectors, cost_label_min,
                        cost_label_max, card_label_min, card_label_max)

encode_train_plan_seq_save(path='/home/sunji/learnedcardinality/train_100k_real_plans_seq_sample.json', parameters=parameters)