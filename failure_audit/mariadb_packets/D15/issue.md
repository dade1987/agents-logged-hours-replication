# ambiguous view frm parsing when username includes \n

{code:sql}
create user 'root
definer_host=localhost
suid=1'@localhost;

--connect u,localhost,'root
definer_host=localhost
suid=1';

--error ER_TABLEACCESS_DENIED_ERROR
select group_concat(user,'@',host) from mysql.global_priv;

create function f() returns text sql security invoker
  return (select group_concat(user,'@',host) from mysql.global_priv);

create view v as select f();

select * from v;
{code}

Reported by Ben Bidner (Automattic.com Security Team).
