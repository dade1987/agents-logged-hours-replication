# Numeric aggregates should end up with an error for xmltype

{noformat}
MariaDB [test]>   CREATE TABLE t (x XMLTYPE);
Query OK, 0 rows affected (0,062 sec)

MariaDB [test]>   INSERT INTO t VALUES ('<a/>');
Query OK, 1 row affected (0,010 sec)

MariaDB [test]> INSERT INTO t VALUES ('<a/>'),('<b>1</b>'),('<n>4.5</n>'),('<c/>');
Query OK, 4 rows affected (0,014 sec)
Records: 4  Duplicates: 0  Warnings: 0

MariaDB [test]> select x+1 from t;
ERROR 4078 (HY000): Illegal parameter data types xmltype and int for operation '+'

MariaDB [test]> select sum(x) from t;
+--------+
| sum(x) |
+--------+
|      0 |
+--------+
1 row in set, 5 warnings (0,003 sec)

Warning (Code 1292): Truncated incorrect DOUBLE value: '<a/>'
Warning (Code 1292): Truncated incorrect DOUBLE value: '<a/>'
Warning (Code 1292): Truncated incorrect DOUBLE value: '<b>1</b>'
Warning (Code 1292): Truncated incorrect DOUBLE value: '<n>4.5</n>'
Warning (Code 1292): Truncated incorrect DOUBLE value: '<c/>'
{noformat}
it should be error (as in e.g. geometry - 
ERROR 4079 (HY000): Illegal parameter data type geometry for operation 'sum'
) Currently it is trucated to 0, which does not make sense
