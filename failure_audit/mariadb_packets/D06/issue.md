# `+DEFAULT` is valid syntax for `CHANGE MASTER TO master_heartbeat_period=`

Mismerge of MDEV-38454 into MDEV-28302.

{code:sql}
CHANGE MASTER TO master_heartbeat_period= +DEFAULT;
{code}
Expected: syntax error; Actual: accepted, equivalent to {{...= DEFAULT}}
