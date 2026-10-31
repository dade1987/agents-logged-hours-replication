# SELECT INTO row_type_of.field crashes the server

This script crashes the server:
{code:sql}
CREATE OR REPLACE TABLE t1 (a INT,b VARCHAR(10));
INSERT INTO t1 VALUES (10,'b10');
DELIMITER $$
CREATE OR REPLACE PROCEDURE p1()
BEGIN
  DECLARE r0 ROW TYPE OF t1;
  SELECT a,b INTO r0.a,r0.b FROM t1;
  SELECT r0.a, r0.b;
END;
$$
DELIMITER ;
{code}
with the following stack:
{noformat}
#0  0x00007ffff7082e7c in __pthread_kill_implementation ()
   from /lib64/libc.so.6
#1  0x00007ffff7028f0e in raise () from /lib64/libc.so.6
#2  0x00007ffff70106d0 in abort () from /lib64/libc.so.6
#3  0x00007ffff7010639 in __assert_fail_base.cold () from /lib64/libc.so.6
#4  0x0000555555ab0c81 in Type_handler_row::make_outvar_field (
    this=0x555558015e00 <type_handler_row_internal>, thd=0x7fffa0000dc8, 
    name=..., addr=..., field=..., sphead=0x7fffa009b1e0, validate_only=false)
    at /home/bar/maria-git/12.1.m37863.trm2/sql/sql_type_row.cc:164
#5  0x00005555556f331f in LEX::create_outvar (this=0x7fffa00a00c0, 
    thd=0x7fffa0000dc8, a=..., b=...)
    at /home/bar/maria-git/12.1.m37863.trm2/sql/sql_lex.cc:8896
#6  0x0000555555af10d1 in MYSQLparse (thd=0x7fffa0000dc8)
    at /home/bar/maria-git/12.1.m37863.trm2/sql/sql_yacc.yy:13529
#7  0x000055555573d9f6 in parse_sql (thd=0x7fffa0000dc8, 
    parser_state=0x7ffff40e8f60, creation_ctx=0x0, do_pfs_digest=true)
    at /home/bar/maria-git/12.1.m37863.trm2/sql/sql_parse.cc:10305
#8  0x0000555555737989 in mysql_parse (thd=0x7fffa0000dc8, 
    rawbuf=0x7fffa0034da0 "CREATE OR REPLACE PROCEDURE p1()\nBEGIN\n  DECLARE r0 ROW TYPE OF t1;\n  SELECT a,b INTO r0.a,r0.b FROM t1;\n  SELECT r0.a, r0.b;\nEND", length=129, parser_state=0x7ffff40e8f60)
{noformat}

This script also crashes:
{code:sql}
CREATE OR REPLACE TABLE t1 (a INT,b VARCHAR(10));
INSERT INTO t1 VALUES (10,'b10');
DELIMITER $$
CREATE OR REPLACE PROCEDURE p1()
BEGIN
  DECLARE c1 CURSOR FOR SELECT * FROM t1;
  BEGIN
    DECLARE r0 ROW TYPE OF c1;
    SELECT a,b INTO r0.a,r0.b FROM t1;
    SELECT r0.a, r0.b;
  END;
END;
$$
DELIMITER ;
{code}

