# Server crash upon altering table with NEXTVAL for default under exclusive lock

{code:sql}
CREATE SEQUENCE s;
CREATE TABLE t (a INT DEFAULT(NEXTVAL(s)), b INT);
ALTER TABLE t FORCE, ALGORITHM=COPY, LOCK=EXCLUSIVE;

# Cleanup
DROP TABLE t;
DROP SEQUENCE s;
{code}

{noformat:title=10.4 9854fb6f}
#3  <signal handler called>
#4  0x0000558656f6e46d in mysql_lock_merge (a=0x0, b=0x606000019ee8) at /data/src/10.4/sql/lock.cc:653
#5  0x0000558656327051 in open_and_lock_internal_tables (table=0x620000042088, lock_table=true) at /data/src/10.4/sql/sql_base.cc:4913
#6  0x0000558656a9b159 in THD::create_and_open_tmp_table (this=0x62b00005b208, frm=0x7fc0387741f0, path=0x7fc038775ece "./test/#sql-17297c_4", db=0x62b000062a60 "test", table_name=0x62b000062318 "t", open_internal_tables=true) at /data/src/10.4/sql/temporary_tables.cc:94
#7  0x000055865672b405 in mysql_alter_table (thd=0x62b00005b208, new_db=0x62b00005fa10, new_name=0x62b00005fe68, create_info=0x7fc038777250, table_list=0x62b000062368, recreate_info=0x7fc0387770b0, alter_info=0x7fc038777150, order_num=0, order=0x0, ignore=false) at /data/src/10.4/sql/sql_table.cc:10516
#8  0x00005586568b16bc in Sql_cmd_alter_table::execute (this=0x62b000062a98, thd=0x62b00005b208) at /data/src/10.4/sql/sql_alter.cc:531
#9  0x00005586564bae35 in mysql_execute_command (thd=0x62b00005b208) at /data/src/10.4/sql/sql_parse.cc:6216
#10 0x00005586564c66af in mysql_parse (thd=0x62b00005b208, rawbuf=0x62b000062228 "ALTER TABLE t FORCE, ALGORITHM=COPY, LOCK=EXCLUSIVE", length=51, parser_state=0x7fc038779860, is_com_multi=false, is_next_command=false) at /data/src/10.4/sql/sql_parse.cc:8010
#11 0x000055865649c97a in dispatch_command (command=COM_QUERY, thd=0x62b00005b208, packet=0x629000230209 "ALTER TABLE t FORCE, ALGORITHM=COPY, LOCK=EXCLUSIVE", packet_length=51, is_com_multi=false, is_next_command=false) at /data/src/10.4/sql/sql_parse.cc:1857
#12 0x00005586564994e9 in do_command (thd=0x62b00005b208) at /data/src/10.4/sql/sql_parse.cc:1378
#13 0x0000558656898a48 in do_handle_one_connection (connect=0x6080000009a8) at /data/src/10.4/sql/sql_connect.cc:1420
#14 0x000055865689835f in handle_one_connection (arg=0x6080000009a8) at /data/src/10.4/sql/sql_connect.cc:1324
#15 0x0000558657507cfc in pfs_spawn_thread (arg=0x615000003508) at /data/src/10.4/storage/perfschema/pfs.cc:1869
#16 0x00007fc0404a7fd4 in start_thread (arg=<optimized out>) at ./nptl/pthread_create.c:442
#17 0x00007fc0405285bc in clone3 () at ../sysdeps/unix/sysv/linux/x86_64/clone3.S:81
{noformat}
{noformat:title=10.4 9854fb6f, with InnoDB on debug build}
mysqld: /data/src/10.4/sql/sql_base.cc:5750: void close_tables_for_reopen(THD*, TABLE_LIST**, const MDL_savepoint&): Assertion `thd->transaction.stmt.is_empty() || (thd->state_flags & Open_tables_state::BACKUPS_AVAIL)' failed.
230731 21:19:16 [ERROR] mysqld got signal 6 ;

#8  0x00007ffabae45395 in __assert_fail_base (fmt=0x7ffabafb9a70 "%s%s%s:%u: %s%sAssertion `%s' failed.\n%n", assertion=assertion@entry=0x55d85619f320 "thd->transaction.stmt.is_empty() || (thd->state_flags & Open_tables_state::BACKUPS_AVAIL)", file=file@entry=0x55d85619ae40 "/data/src/10.4/sql/sql_base.cc", line=line@entry=5750, function=function@entry=0x55d85619f820 "void close_tables_for_reopen(THD*, TABLE_LIST**, const MDL_savepoint&)") at ./assert/assert.c:92
#9  0x00007ffabae53df2 in __GI___assert_fail (assertion=0x55d85619f320 "thd->transaction.stmt.is_empty() || (thd->state_flags & Open_tables_state::BACKUPS_AVAIL)", file=0x55d85619ae40 "/data/src/10.4/sql/sql_base.cc", line=5750, function=0x55d85619f820 "void close_tables_for_reopen(THD*, TABLE_LIST**, const MDL_savepoint&)") at ./assert/assert.c:101
#10 0x000055d853fc0849 in close_tables_for_reopen (thd=0x62b00009a208, tables=0x7ffaa624adf0, start_of_statement_svp=...) at /data/src/10.4/sql/sql_base.cc:5750
#11 0x000055d853fb9136 in open_tables (thd=0x62b00009a208, options=..., start=0x7ffaa624adf0, counter=0x7ffaa624ade0, flags=0, prelocking_strategy=0x7ffaa624ae10) at /data/src/10.4/sql/sql_base.cc:4418
#12 0x000055d853fbbf15 in open_and_lock_internal_tables (table=0x620000044088, lock_table=true) at /data/src/10.4/sql/sql_base.cc:4901
#13 0x000055d854730159 in THD::create_and_open_tmp_table (this=0x62b00009a208, frm=0x7ffaa624b1f0, path=0x7ffaa624cece "./test/#sql-172abe_9", db=0x62b0000a1a60 "test", table_name=0x62b0000a1318 "t", open_internal_tables=true) at /data/src/10.4/sql/temporary_tables.cc:94
#14 0x000055d8543c0405 in mysql_alter_table (thd=0x62b00009a208, new_db=0x62b00009ea10, new_name=0x62b00009ee68, create_info=0x7ffaa624e250, table_list=0x62b0000a1368, recreate_info=0x7ffaa624e0b0, alter_info=0x7ffaa624e150, order_num=0, order=0x0, ignore=false) at /data/src/10.4/sql/sql_table.cc:10516
#15 0x000055d8545466bc in Sql_cmd_alter_table::execute (this=0x62b0000a1a98, thd=0x62b00009a208) at /data/src/10.4/sql/sql_alter.cc:531
#16 0x000055d85414fe35 in mysql_execute_command (thd=0x62b00009a208) at /data/src/10.4/sql/sql_parse.cc:6216
#17 0x000055d85415b6af in mysql_parse (thd=0x62b00009a208, rawbuf=0x62b0000a1228 "ALTER TABLE t FORCE, ALGORITHM=COPY, LOCK=EXCLUSIVE", length=51, parser_state=0x7ffaa6250860, is_com_multi=false, is_next_command=false) at /data/src/10.4/sql/sql_parse.cc:8010
#18 0x000055d85413197a in dispatch_command (command=COM_QUERY, thd=0x62b00009a208, packet=0x629000299209 "ALTER TABLE t FORCE, ALGORITHM=COPY, LOCK=EXCLUSIVE", packet_length=51, is_com_multi=false, is_next_command=false) at /data/src/10.4/sql/sql_parse.cc:1857
#19 0x000055d85412e4e9 in do_command (thd=0x62b00009a208) at /data/src/10.4/sql/sql_parse.cc:1378
#20 0x000055d85452da48 in do_handle_one_connection (connect=0x608000000ba8) at /data/src/10.4/sql/sql_connect.cc:1420
#21 0x000055d85452d35f in handle_one_connection (arg=0x608000000ba8) at /data/src/10.4/sql/sql_connect.cc:1324
#22 0x000055d85519ccfc in pfs_spawn_thread (arg=0x615000006208) at /data/src/10.4/storage/perfschema/pfs.cc:1869
#23 0x00007ffabaea7fd4 in start_thread (arg=<optimized out>) at ./nptl/pthread_create.c:442
#24 0x00007ffabaf285bc in clone3 () at ../sysdeps/unix/sysv/linux/x86_64/clone3.S:81
{noformat}

Reproducible with at least MyISAM, InnoDB, Aria, on debug- and non-debug builds as above, on all existing versions, including earlier minor releases.
