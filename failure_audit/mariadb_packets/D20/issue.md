# Collation mix issue after update

After update some queries fail with "Illegal mix of collations"

{code:java}
CREATE TABLE file ( `ID` int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY, `Path` varchar(800) NOT NULL DEFAULT '')  ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
Query OK, 0 rows affected (0.020 sec)

INSERT INTO file VALUES (1,"text");
Query OK, 1 row affected (0.003 sec)

SELECT IF((@p:=(SELECT f.Path FROM file f WHERE f.ID=1 AND f.Path REGEXP "^xx"))!="",1,2);
ERROR 1267 (HY000): Illegal mix of collations (utf8mb3_unicode_ci,COERCIBLE) and (utf8mb3_uca1400_ai_ci,COERCIBLE) for operation '<>'

SELECT  @@character_set_collations,  @@collation_connection;
+-----------------------------------------------------------------------------------------------------------------------------------------+------------------------+
| @@character_set_collations                                                                                                              | @@collation_connection |
+-----------------------------------------------------------------------------------------------------------------------------------------+------------------------+
| utf8mb3=utf8mb3_uca1400_ai_ci,ucs2=ucs2_uca1400_ai_ci,utf8mb4=utf8mb4_uca1400_ai_ci,utf16=utf16_uca1400_ai_ci,utf32=utf32_uca1400_ai_ci | utf8mb3_uca1400_ai_ci  |
+-----------------------------------------------------------------------------------------------------------------------------------------+------------------------+


{code}


Setting the connection-collection works

{code:java}
SET collation_connection="utf8mb3_unicode_ci";
Query OK, 0 rows affected (0.001 sec)

 SELECT IF((@p:=(SELECT f.Path FROM file f WHERE f.ID=1 AND f.Path REGEXP "^xx"))!="",1,2);
+------------------------------------------------------------------------------------+
| IF((@p:=(SELECT f.Path FROM file f WHERE f.ID=1 AND f.Path REGEXP "^xx"))!="",1,2) |
+------------------------------------------------------------------------------------+
|                                                                                  2 |
+------------------------------------------------------------------------------------+

{code}

But there is no server variable to adjust this variable.
The query above worked in 11.4 without issues.
