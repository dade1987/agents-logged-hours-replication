# DROP PACKAGE leaves PACKAGE BODY grant in mysql.procs_priv

Originally reported at https://hackerone.com/reports/3908943

I run this script:

{code:sql}
SET sql_mode=ORACLE;

DELIMITER $$
CREATE PACKAGE pkg1 AS
  FUNCTION f RETURN VARCHAR2(64);
END
$$
CREATE PACKAGE BODY pkg1 AS
  FUNCTION f RETURN VARCHAR2(64) AS
    BEGIN RETURN 'benign';
  END;
END$$
DELIMITER ;

CREATE OR REPLACE USER reader@localhost;
GRANT EXECUTE ON PACKAGE test.pkg1 TO reader@localhost;
GRANT EXECUTE ON PACKAGE BODY test.pkg1 TO reader@localhost;

SELECT host,db,user,routine_name,routine_type,proc_priv FROM mysql.procs_priv ORDER BY routine_type;
{code}
It returns the following output:
{noformat}
+-----------+------+--------+--------------+--------------+-----------+
| host      | db   | user   | routine_name | routine_type | proc_priv |
+-----------+------+--------+--------------+--------------+-----------+
| localhost | test | reader | pkg1         | PACKAGE      | Execute   |
| localhost | test | reader | pkg1         | PACKAGE BODY | Execute   |
+-----------+------+--------+--------------+--------------+-----------+
{noformat}
Looks ok so far.

Now I drop the package and re-run the query to mysql.procs_priv:
{code}
DROP PACKAGE pkg1;
SELECT host,db,user,routine_name,routine_type,proc_priv FROM mysql.procs_priv ORDER BY routine_type;
{code}
It returns the following output:
{noformat}
+-----------+------+--------+--------------+--------------+-----------+
| host      | db   | user   | routine_name | routine_type | proc_priv |
+-----------+------+--------+--------------+--------------+-----------+
| localhost | test | reader | pkg1         | PACKAGE BODY | Execute   |
+-----------+------+--------+--------------+--------------+-----------+
{noformat}

Notice, the grant for PACKAGE BODY is still there. This is an unexpected behaviour. It should be removed by the DROP PACKAGE.

Reported by [heyoimjeb|https://hackerone.com/heyoimjeb]
