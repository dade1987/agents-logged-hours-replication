# MEMORY tables incorrectly restart index scan on DELETE

When a {{DELETE}} is done during the index scan it can happen that the current record was just deleted and {{index_next}} cannot move the cursor from the current record to the next one. In this case the engine has to restart the search from the root of the tree.

{{MEMORY}} engine with a {{BTREE}} index restarts the search using the original key, not the last found, so it repeats the search visiting again all keys that were not deleted.
Example:

{code:sql}
source include/have_sequence.inc;

create table t1 (a int, b int, c int, key (a, b) using btree) engine=heap;

insert t1 select seq % 10, seq, seq from seq_1_to_80;
flush status;
delete from t1 where a=3 and c>60;
select * from information_schema.session_status where variable_name like 'handler_r%' and variable_value>0;

delete from t1;
insert t1 select seq % 10, seq, seq from seq_1_to_80;
flush status;
delete from t1 where a=3;
select * from information_schema.session_status where variable_name like 'handler_r%' and variable_value>0;

drop table t1;
{code}
results in
{noformat}
create table t1 (a int, b int, c int, key (a, b) using btree) engine=heap;
insert t1 select seq % 10, seq, seq from seq_1_to_80;
flush status;
delete from t1 where a=3 and c>60;
select * from information_schema.session_status where variable_name like 'handler_r%' and variable_value>0;
VARIABLE_NAME   VARIABLE_VALUE
HANDLER_READ_KEY        1
HANDLER_READ_NEXT       20
delete from t1;
insert t1 select seq % 10, seq, seq from seq_1_to_80;
flush status;
delete from t1 where a=3;
select * from information_schema.session_status where variable_name like 'handler_r%' and variable_value>0;
VARIABLE_NAME   VARIABLE_VALUE
HANDLER_READ_KEY        1
HANDLER_READ_NEXT       8
{noformat}
There were 8 matching rows (3, 13, 23, 33, 43, 53, 63, 73) and the second case with {{where a=3}} did one {{rfirst}} and 8 {{rnext}} to read them all and hit EOF on the last search.

But the first case with {{where a=3 and c>60}} did 20 {{rnext}} calls, reading (remember, that the first 3 was read by {{rfirst}}) 13, 23, 33, 43, 53, 63 (deleted), 3, 13, 23, 33, 43, 53, 73 (deleted), 3, 13, 23, 33, 43, 53, EOF.

The correct fix is to restart the search from the previously found key value, not from the original one.
