# MariaDB crash triggered by ST_CONVEXHULL and ST_SIMPLIFY string concatenation

~~~sql
SELECT ST_ASTEXT ( ST_CONVEXHULL ( ST_GEOMFROMTEXT ( x ) ) ) ; SELECT ST_ASTEXT ( ST_CONVEXHULL ( ST_GEOMFROMTEXT ( x ) ) ) ; SELECT ST_ASTEXT ( ST_CONVEXHULL ( ST_GEOMFROMTEXT ( 'LINESTRING(0 0,-0.00 0,0.0 0)' ) ) ) ; SELECT ST_ASTEXT ( ST_CONVEXHULL ( ST_GEOMFROMTEXT ( 'LINESTRING(0 0,0 5,5 5,5 0,0 0)' ) ) ) ; SELECT CONCAT_WS ( ST_SIMPLIFY ( ST_GEOMFROMTEXT ( 'MULTILINESTRING((0 0,5 5,0 10),(0 0,-5 5,0 10))' ) , 5 ) , 7 , 5 ) ;
~~~

## Expected result
The server should either execute the query or return a normal SQL error without crashing.

## Actual result
The fuzzing run observed a server crash. The deduplicated stack signature is:
~~~
stack:pthread_kill|raise|abort|__fsetlocking|__fortify_fail|__stack_chk_fail|_ZN19Item_func_concat_ws7val_strEP6String|_ZNK12Type_handler13Item_send_strEP4ItemP8ProtocolP8st_value
~~~

Top frames:
~~~
pthread_kill
raise
abort
__fsetlocking
__fortify_fail
__stack_chk_fail
_ZN19Item_func_concat_ws7val_strEP6String
_ZNK12Type_handler13Item_send_strEP4ItemP8ProtocolP8st_value
~~~

