# single quote in DATA DIRECTORY breaks SHOW CREATE TABLE

e.g.
{code:sql}
--mkdir $MYSQL_TMP_DIR/o'hara
eval create table t1 (a int) data directory="$MYSQL_TMP_DIR/o'hara";
show create table t1;
drop table t1;
{code}
this prints
{noformat}
CREATE TABLE `t1` (
  `a` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci DATA DIRECTORY='MYSQL_TMP_DIR/o'hara/'
{noformat}
