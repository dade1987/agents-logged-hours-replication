# JSON path functions with no charset on path crash server

PoC:
{code:sql}
SELECT ( WITH x ( x ) AS ( WITH x ( x ) AS ( SELECT json_array_append ( 'x' , ( 'x' % 'x' ) , 1 , 'x' , 1 ) ) SELECT CASE WHEN x * x THEN x END FROM x ) ( SELECT 1 FROM x WHERE x ) ) ;
{code}

docker log:
{code}
mariadbd(my_print_stacktrace+0x32)[0x563066b2c7c2]
mariadbd(handle_fatal_signal+0x488)[0x563066605cf8]
/lib/x86_64-linux-gnu/libc.so.6(+0x42520)[0x7f4a0d2ba520]
mariadbd(json_string_set_cs+0xf)[0x563066b9272f]
mariadbd(json_find_path+0x3a)[0x563066b93dca]
mariadbd(_ZN27Item_func_json_array_append7val_strEP6String+0x22d)[0x56306651ba3d]
mariadbd(_ZN13Item_str_func8val_realEv+0x6b)[0x5630666ae4eb]
mariadbd(_ZN13Item_func_mul7real_opEv+0x38)[0x56306667ba08]
mariadbd(_ZNK28Type_handler_temporal_result13Item_val_boolEP4Item+0x14)[0x563066548374]
mariadbd(_ZN23Item_func_case_searched9find_itemEv+0x4a)[0x56306664255a]
mariadbd(_ZN14Item_func_case6str_opEP6String+0x1a)[0x56306663fafa]
mariadbd(_ZN27Item_func_hybrid_field_type23val_decimal_from_str_opEP10my_decimal+0x25)[0x56306667f115]
mariadbd(_ZN18Item_cache_decimal11val_decimalEP10my_decimal+0x5c)[0x563066621adc]
mariadbd(_ZN4VDecC2EP4Item+0x2f)[0x5630665549bf]
mariadbd(_ZN14Arg_comparator15compare_decimalEv+0x27)[0x5630666446d7]
mariadbd(_ZN12Item_func_ne7val_intEv+0x34)[0x56306664c884]
mariadbd(_ZNK23Type_handler_int_result13Item_val_boolEP4Item+0x14)[0x5630665483a4]
mariadbd(_ZN15Item_bool_func215remove_eq_condsEP3THDPN4Item11cond_resultEb+0x79)[0x5630663c9f39]
mariadbd(+0x870e91)[0x5630663d0e91]
mariadbd(_ZN4JOIN14optimize_innerEv+0x8bb)[0x563066411d7b]
mariadbd(_ZN4JOIN8optimizeEv+0xda)[0x563066412e2a]
mariadbd(+0x7ec60c)[0x56306634c60c]
mariadbd(_Z27mysql_handle_single_derivedP3LEXP10TABLE_LISTj+0x95)[0x56306634be35]
mariadbd(_ZN4JOIN14optimize_innerEv+0xb27)[0x563066411fe7]
mariadbd(_ZN4JOIN8optimizeEv+0xda)[0x563066412e2a]
mariadbd(_ZN13st_select_lex31optimize_unflattened_subqueriesEb+0x115)[0x56306636ca55]
mariadbd(_ZN4JOIN28optimize_constant_subqueriesEv+0x35)[0x56306650bd55]
mariadbd(_ZN4JOIN14optimize_innerEv+0x503)[0x5630664119c3]
mariadbd(_ZN4JOIN8optimizeEv+0xda)[0x563066412e2a]
mariadbd(_Z12mysql_selectP3THDP10TABLE_LISTR4ListI4ItemEPS4_jP8st_orderS9_S7_S9_yP13select_resultP18st_select_lex_unitP13st_select_lex+0xd1)[0x563066412f21]
mariadbd(_Z13handle_selectP3THDP3LEXP13select_resulty+0x154)[0x563066413774]
mariadbd(+0x826f55)[0x563066386f55]
mariadbd(_Z21mysql_execute_commandP3THDb+0x419e)[0x563066395f0e]
mariadbd(_Z11mysql_parseP3THDPcjP12Parser_state+0x1e7)[0x563066397237]
mariadbd(_Z16dispatch_command19enum_server_commandP3THDPcjb+0x14bd)[0x563066399a1d]
mariadbd(_Z10do_commandP3THDb+0x138)[0x56306639b818]
mariadbd(_Z24do_handle_one_connectionP7CONNECTb+0x3bf)[0x5630664c33af]
mariadbd(handle_one_connection+0x5d)[0x5630664c36fd]
mariadbd(+0xcd1906)[0x563066831906]
/lib/x86_64-linux-gnu/libc.so.6(+0x94b43)[0x7f4a0d30cb43]
/lib/x86_64-linux-gnu/libc.so.6(clone+0x44)[0x7f4a0d39dbb4]

Trying to get some variables.
Some pointers may be invalid and cause the dump to abort.
Query (0x7f49ac0130d8): SELECT ( WITH x ( x ) AS ( WITH x ( x ) AS ( SELECT json_array_append ( 'x' , ( 'x' % 'x' ) , 1 , 'x' , 1 ) ) SELECT CASE WHEN x * x THEN x END FROM x ) ( SELECT 1 FROM x WHERE x ) )

Connection ID (thread ID): 4
Status: NOT_KILLED

Optimizer switch: index_merge=on,index_merge_union=on,index_merge_sort_union=on,index_merge_intersection=on,index_merge_sort_intersection=off,engine_condition_pushdown=off,index_condition_pushdown=on,derived_merge=on,derived_with_keys=on,firstmatch=on,loosescan=on,materialization=on,in_to_exists=on,semijoin=on,partial_match_rowid_merge=on,partial_match_table_scan=on,subquery_cache=on,mrr=off,mrr_cost_based=off,mrr_sort_keys=off,outer_join_with_cache=on,semijoin_with_cache=on,join_cache_incremental=on,join_cache_hashed=on,join_cache_bka=on,optimize_join_buffer_size=on,table_elimination=on,extended_keys=on,exists_to_in=on,orderby_uses_equalities=on,condition_pushdown_for_derived=on,split_materialized=on,condition_pushdown_for_subquery=on,rowid_filter=on,condition_pushdown_from_having=on,not_null_range_scan=off,hash_join_cardinality=on
{code}
