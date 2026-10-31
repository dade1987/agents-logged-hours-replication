# wrong result with json_overlaps when one of the arguments has an empty nested array element

probably affecting earlier versions too.

{noformat}
MariaDB [test]> select json_overlaps('[[1]]', '[[]]');
+--------------------------------+
| json_overlaps('[[1]]', '[[]]') |
+--------------------------------+
|                              1 |
+--------------------------------+
1 row in set (0.000 sec)

MariaDB [test]> select json_overlaps('[[1]]', '[[],123]');
+------------------------------------+
| json_overlaps('[[1]]', '[[],123]') |
+------------------------------------+
|                                  1 |
+------------------------------------+
1 row in set (0.001 sec)

{noformat}

MySQL 9.6:
{code}
mysql>  select json_overlaps('[[1]]', '[[]]');
+--------------------------------+
| json_overlaps('[[1]]', '[[]]') |
+--------------------------------+
|                              0 |
+--------------------------------+
1 row in set (0.002 sec)
{code}

{code}
mysql>  select json_overlaps('[[1]]', '[[],123]');
+------------------------------------+
| json_overlaps('[[1]]', '[[],123]') |
+------------------------------------+
|                                  0 |
+------------------------------------+
1 row in set (0.001 sec)
{code}

