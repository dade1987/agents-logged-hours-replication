# MariaDB crash triggered by INFORMATION_SCHEMA query with ROW_NUMBER and GIS simplify

~~~sql
SELECT table_name FROM information_schema . TABLES WHERE TABLE_SCHEMA = 'performance_schema' ORDER BY table_name ; SELECT table_name FROM information_schema . TABLES WHERE TABLE_SCHEMA = 'performance_schema' ORDER BY table_name ; SELECT TABLE_SCHEMA , CONCAT ( ROW_NUMBER ( ) OVER ( ) , 1 ) x , ORDINAL_POSITION FROM INFORMATION_SCHEMA . COLUMNS WHERE TABLE_SCHEMA = 'performance_schema' AND 'MULTIPOINT(1 189.7654,41,-1032.34324 9,6.4 1,4 9)' IN ( 'accounts' , 'cond_instances' , 'setup_consumers' , 'setup_objects' , ST_SIMPLIFY ( ST_GEOMFROMTEXT ( 'POLYGON((10 2,5 2,5 10,-5 10,-5 2,-10 2,-10 -2,-5 -2,-5 -10,5 -10,5 -2,10 -2,10 2))' ) , 3 ) , 'global_status' ) ORDER BY TABLE_SCHEMA + 2 DESC , TABLE_NAME , ORDINAL_POSITION , ( SELECT COLUMN_NAME ORDER BY 1 ) ;
~~~

## Expected result
The server should either execute the query or return a normal SQL error without crashing.

## Actual result
The fuzzing run observed a server crash. The deduplicated stack signature is:
~~~
stack:_ZN6String6appendEPKcm|_ZNK11Gis_polygon8simplifyEP6Stringd|_ZN18Item_func_simplify7val_strEP6String|_ZN9in_string3setEjP4Item|_ZN12Item_func_in13fix_in_vectorEv|_ZNK26Type_handler_string_result44Item_func_in_fix_comparator_compatible_typesEP3THDP12Item_func_in|_ZN12Item_func_in18fix_length_and_decEP3THD|_ZN9Item_func10fix_fieldsEP3THDPP4Item
~~~

