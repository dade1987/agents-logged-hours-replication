# I_S.VECTOR_INDEXES: Unclear or inconsistent semantics of INDEX_SIZE

According to the [comment|https://jira.mariadb.org/browse/MDEV-34805?focusedCommentId=327583&page=com.atlassian.jira.plugin.system.issuetabpanels%3Acomment-tabpanel#comment-327583] in MDEV-34805, {{information_schema.vector_indexes.index_size}} value is "also available from MDEV-35821". MDEV-35821 was about {{information_schema.tables.index_length}} column, so, given the comment, I would expect their values to be identical. However, it is not so at least for non-InnoDB tables, see results below ({{isize}} vs {{ilength}}).

As for InnoDB, the values appear to be the same in {{VECTOR_INDEXES}} and in {{TABLES}}, but the meaning of these values remains unclear. In a nearly-empty table, the value coincides with InnoDB page size, although the on-disk file size is different. However, as can be seen in the test result below, after the first significant INSERT the value is still the page size, while it should be already bigger. After the next INSERT of the same size, the value jumps up. 

If it's really the intended behavior, it needs to be documented. So far the documentation stub does not provide any explanation of it.

{code:sql}
--source include/have_innodb.inc
--source include/have_sequence.inc

CREATE PROCEDURE check_ind()
  SELECT table_name, index_size isize,
         index_length ilength, total_nodes, table_rows
  FROM information_schema.vector_indexes JOIN
       information_schema.tables USING (table_schema, table_name)
  WHERE table_schema = 'test'
  ORDER BY table_name;

CREATE TABLE t1_myisam (
  pk int AUTO_INCREMENT PRIMARY KEY,
  a vector(1) NOT NULL, vector(a)
) ENGINE=MyISAM;
CREATE TABLE t99_myisam (
  pk int AUTO_INCREMENT PRIMARY KEY,
  a vector(99) NOT NULL, vector(a)
) ENGINE=MyISAM;
CREATE TABLE t1_innodb (
  pk int AUTO_INCREMENT PRIMARY KEY,
  a vector(1) NOT NULL, vector(a)
) ENGINE=InnoDB;
CREATE TABLE t99_innodb (
  pk int AUTO_INCREMENT PRIMARY KEY,
  a vector(99) NOT NULL, vector(a)
) ENGINE=InnoDB;

--echo #
--echo # Empty tables
--echo #

CALL check_ind();
--replace_regex /\/.*\/data\//DATADIR\//
--exec ls -s --block-size=1 $MARIADB_DATADIR/test/*#01*

--echo #
--echo # Inserting 1 row in each table
--echo #

INSERT INTO t1_myisam (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_1 s1, seq_1_to_1 s2 GROUP BY s2.seq;

INSERT INTO t99_myisam (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_99 s1, seq_1_to_1 s2 GROUP BY s2.seq;

INSERT INTO t1_innodb (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_1 s1, seq_1_to_1 s2 GROUP BY s2.seq;

INSERT INTO t99_innodb (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_99 s1, seq_1_to_1 s2 GROUP BY s2.seq;

CALL check_ind();
--replace_regex /\/.*\/data\//DATADIR\//
--exec ls -s --block-size=1 $MARIADB_DATADIR/test/*#01*

--echo #
--echo # Inserting 9,999 rows in each table
--echo #

INSERT INTO t1_myisam (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_1 s1, seq_1_to_9999 s2 GROUP BY s2.seq;

INSERT INTO t99_myisam (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_99 s1, seq_1_to_9999 s2 GROUP BY s2.seq;

INSERT INTO t1_innodb (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_1 s1, seq_1_to_9999 s2 GROUP BY s2.seq;

INSERT INTO t99_innodb (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_99 s1, seq_1_to_9999 s2 GROUP BY s2.seq;

CALL check_ind();
--replace_regex /\/.*\/data\//DATADIR\//
--exec ls -s --block-size=1 $MARIADB_DATADIR/test/*#01*

--echo #
--echo # ANALYZE does not help
--echo #

ANALYZE TABLE t1_myisam, t99_myisam, t1_innodb, t99_innodb;
CALL check_ind();

--echo #
--echo # Inserting 10,000 rows in each table
--echo #

INSERT INTO t1_myisam (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_1 s1, seq_1_to_10000 s2 GROUP BY s2.seq;

INSERT INTO t99_myisam (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_99 s1, seq_1_to_10000 s2 GROUP BY s2.seq;

INSERT INTO t1_innodb (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_1 s1, seq_1_to_10000 s2 GROUP BY s2.seq;

INSERT INTO t99_innodb (a)
  SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
  FROM seq_1_to_99 s1, seq_1_to_10000 s2 GROUP BY s2.seq;

CALL check_ind();
--replace_regex /\/.*\/data\//DATADIR\//
--exec ls -s --block-size=1 $MARIADB_DATADIR/test/*#01*

DROP TABLE t1_myisam, t99_myisam, t1_innodb, t99_innodb;
DROP PROCEDURE check_ind;
{code}

{code:sql|title=5dae70e86321916d219c465b19991c5261c3f26a}
CREATE TABLE t1_myisam (
pk int AUTO_INCREMENT PRIMARY KEY,
a vector(1) NOT NULL, vector(a)
) ENGINE=MyISAM;
CREATE TABLE t99_myisam (
pk int AUTO_INCREMENT PRIMARY KEY,
a vector(99) NOT NULL, vector(a)
) ENGINE=MyISAM;
CREATE TABLE t1_innodb (
pk int AUTO_INCREMENT PRIMARY KEY,
a vector(1) NOT NULL, vector(a)
) ENGINE=InnoDB;
CREATE TABLE t99_innodb (
pk int AUTO_INCREMENT PRIMARY KEY,
a vector(99) NOT NULL, vector(a)
) ENGINE=InnoDB;
#
# Empty tables
#
CALL check_ind();
table_name	isize	ilength	total_nodes	table_rows
t1_innodb	NULL	16384	0	0
t1_myisam	NULL	1024	0	0
t99_innodb	NULL	16384	0	0
t99_myisam	NULL	1024	0	0
98304 DATADIR/test/t1_innodb#i#01.ibd
    0 DATADIR/test/t1_myisam#i#01.MYD
 4096 DATADIR/test/t1_myisam#i#01.MYI
98304 DATADIR/test/t99_innodb#i#01.ibd
    0 DATADIR/test/t99_myisam#i#01.MYD
 4096 DATADIR/test/t99_myisam#i#01.MYI
#
# Inserting 1 row in each table
#
INSERT INTO t1_myisam (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_1 s1, seq_1_to_1 s2 GROUP BY s2.seq;
INSERT INTO t99_myisam (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_99 s1, seq_1_to_1 s2 GROUP BY s2.seq;
INSERT INTO t1_innodb (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_1 s1, seq_1_to_1 s2 GROUP BY s2.seq;
INSERT INTO t99_innodb (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_99 s1, seq_1_to_1 s2 GROUP BY s2.seq;
CALL check_ind();
table_name	isize	ilength	total_nodes	table_rows
t1_innodb	16384	16384	1	1
t1_myisam	24	2072	1	1
t99_innodb	16384	16384	1	1
t99_myisam	220	2268	1	1
98304 DATADIR/test/t1_innodb#i#01.ibd
 4096 DATADIR/test/t1_myisam#i#01.MYD
 4096 DATADIR/test/t1_myisam#i#01.MYI
98304 DATADIR/test/t99_innodb#i#01.ibd
 4096 DATADIR/test/t99_myisam#i#01.MYD
 4096 DATADIR/test/t99_myisam#i#01.MYI
#
# Inserting 9,999 rows in each table
#
INSERT INTO t1_myisam (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_1 s1, seq_1_to_9999 s2 GROUP BY s2.seq;
INSERT INTO t99_myisam (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_99 s1, seq_1_to_9999 s2 GROUP BY s2.seq;
INSERT INTO t1_innodb (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_1 s1, seq_1_to_9999 s2 GROUP BY s2.seq;
INSERT INTO t99_innodb (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_99 s1, seq_1_to_9999 s2 GROUP BY s2.seq;
CALL check_ind();
table_name	isize	ilength	total_nodes	table_rows
t1_innodb	16384	16384	10000	10000
t1_myisam	1040468	1145940	10000	10000
t99_innodb	16384	16384	10000	10000
t99_myisam	3001244	3106716	10000	10000
 9437184 DATADIR/test/t1_innodb#i#01.ibd
 1044480 DATADIR/test/t1_myisam#i#01.MYD
    4096 DATADIR/test/t1_myisam#i#01.MYI
11534336 DATADIR/test/t99_innodb#i#01.ibd
 3002368 DATADIR/test/t99_myisam#i#01.MYD
    4096 DATADIR/test/t99_myisam#i#01.MYI
#
# ANALYZE does not help
#
ANALYZE TABLE t1_myisam, t99_myisam, t1_innodb, t99_innodb;
Table	Op	Msg_type	Msg_text
test.t1_myisam	analyze	status	Engine-independent statistics collected
test.t1_myisam	analyze	status	OK
test.t99_myisam	analyze	status	Engine-independent statistics collected
test.t99_myisam	analyze	status	OK
test.t1_innodb	analyze	status	Engine-independent statistics collected
test.t1_innodb	analyze	status	OK
test.t99_innodb	analyze	status	Engine-independent statistics collected
test.t99_innodb	analyze	status	OK
CALL check_ind();
table_name	isize	ilength	total_nodes	table_rows
t1_innodb	16384	16384	10000	10000
t1_myisam	1040468	1145940	10000	10000
t99_innodb	16384	16384	10000	9513
t99_myisam	3001244	3106716	10000	10000
#
# Inserting 10,000 rows in each table
#
INSERT INTO t1_myisam (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_1 s1, seq_1_to_10000 s2 GROUP BY s2.seq;
INSERT INTO t99_myisam (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_99 s1, seq_1_to_10000 s2 GROUP BY s2.seq;
INSERT INTO t1_innodb (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_1 s1, seq_1_to_10000 s2 GROUP BY s2.seq;
INSERT INTO t99_innodb (a)
SELECT VEC_FromText(concat('[', GROUP_CONCAT(ROUND(RAND(1),3)), ']'))
FROM seq_1_to_99 s1, seq_1_to_10000 s2 GROUP BY s2.seq;
CALL check_ind();
table_name	isize	ilength	total_nodes	table_rows
t1_innodb	2637824	2637824	19938	19911
t1_myisam	2079140	2287012	20000	20000
t99_innodb	3686400	3686400	19837	19513
t99_myisam	6000024	6207896	20000	20000
11534336 DATADIR/test/t1_innodb#i#01.ibd
 2080768 DATADIR/test/t1_myisam#i#01.MYD
  421888 DATADIR/test/t1_myisam#i#01.MYI
16777216 DATADIR/test/t99_innodb#i#01.ibd
 6000640 DATADIR/test/t99_myisam#i#01.MYD
  204800 DATADIR/test/t99_myisam#i#01.MYI
{code}

