#  PREPARE with INTERVAL ? in Partition DDL Crashes the Server (DoS)

Executing PREPARE on a CREATE TABLE ... PARTITION BY RANGE COLUMNS ... INTERVAL ? DAY statement containing an INTERVAL ? parameter placeholder crashes the server process immediately (abort + core). The crash happens during the prepare/parse phase (the parameter is not yet bound); the yacc action calls val_int() on the unbound Item_param, hitting the Item_param::can_return_value() assertion.

Any client that can execute PREPARE (any authenticated user — not even CREATE TABLE privileges are needed since it crashes during parsing) can take down the server with a single statement, constituting a remote denial of service.


{code:java}
-- Single statement, server crashes immediately (assertion abort on debug builds;
-- release-build behavior to be verified, likely reads undefined values)
PREPARE s FROM 'CREATE TABLE db.t7(c DATE)
  PARTITION BY RANGE COLUMNS(c)
  INTERVAL ? DAY
  (PARTITION p0 VALUES LESS THAN (?))';
-- Client: ERROR 2026 (HY000): TLS/SSL error: unexpected eof while reading
-- Then:   ERROR 2002 (HY000): Can't connect to server (115)
{code}

