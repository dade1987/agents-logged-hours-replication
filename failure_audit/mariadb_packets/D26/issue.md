# ALTER TABLE…IMPORT TABLESPACE may break MVCC

Oracle released a MySQL bug fix without a test case:
[Bug#36999166 ALTER TABLE ... IMPORT TABLESPACE may cause unsafe reads|https://github.com/mysql/mysql-server/commit/b1fc1e18b76ceb1204634beb65be81ddc6c4104a]
It is easy to reproduce this with a small change to an existing test case:
{code:diff}
diff --git a/mysql-test/suite/innodb/t/import_bugs.test b/mysql-test/suite/innodb/t/import_bugs.test
index 1b7edcf8f73..82aa6e0996c 100644
--- a/mysql-test/suite/innodb/t/import_bugs.test
+++ b/mysql-test/suite/innodb/t/import_bugs.test
@@ -53,6 +53,10 @@ CREATE TABLE t1(
 
 CREATE TABLE t2 LIKE t1;
 
+--connect mvcc,localhost,root
+START TRANSACTION WITH CONSISTENT SNAPSHOT;
+--connection default
+
 ALTER TABLE t2 DISCARD TABLESPACE;
 
 INSERT INTO t1() VALUES();
@@ -80,6 +84,11 @@ INSERT INTO t2() VALUES();
 INSERT INTO t2() VALUES();
 
 SELECT * FROM t2 ORDER BY id;
+
+--connection mvcc
+SELECT * FROM t2;
+--disconnect mvcc
+--connection default
 DROP TABLE t2;
 
 --echo #
{code}
We would expect the {{SELECT}} to fail with an error. Instead, it is returning the contents of the imported table, which does not correspond to the snapshot.
