# Unexpected ERROR: Found out of order GTID after replaying binlog read from remote

{code:sql}
--source include/have_log_bin.inc

reset master;
create table t1 (a int);
create table t2 (a int);
drop table t1, t2;
flush binary logs;

--exec $MYSQL_BINLOG --read-from-remote-server -uroot --protocol=tcp --port=$MASTER_MYPORT master-bin.000001 | $MYSQL test 2>&1

drop table if exists t1, t2;
flush binary logs;

--let $datadir= `select @@datadir`
--exec $MYSQL_BINLOG $datadir/master-bin.000001 $datadir/master-bin.000002
{code}

{noformat:title=10.8 618d8206}
ERROR: Found out of order GTID. Got 0-1-1 after 0-1-3
mysqltest: At line 15: exec of '/mnt8t/bld/10.8-nightly/bin/mysqlbinlog --defaults-file=/mnt8t/bld/10.8-nightly/mysql-test/var/my.cnf --local-load=/mnt8t/bld/10.8-nightly/mysql-test/var/tmp /mnt8t/bld/10.8-nightly/mysql-test/var/mysqld.1/data//master-bin.000001 /mnt8t/bld/10.8-nightly/mysql-test/var/mysqld.1/data//master-bin.000002' failed, error: 256, status: 1, errno: 11
{noformat}

The error started happening on 10.8 after MDEV-4989:
{noformat}
commit 79e3ee00fa61f809d3e230905beac1d2ae26d5d0
Author: Brandon Nesterenko
Date:   Wed Aug 11 11:29:37 2021 -0600

    MDEV-4989: Support for GTID in mysqlbinlog
{noformat}
