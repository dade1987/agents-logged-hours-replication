# JSON_ARRAYAGG() returns garbage because of off-by-one error

{code:sql}
set session group_concat_max_len = 9;
create temporary table t (c varchar(20) character set latin1);
insert into t values ('ab'), ('cd'), ('ef');
select json_arrayagg(c order by c) from t;
drop temporary table t;
{code}

Reported by [Lukas Kupczyk|https://hackerone.com/lukas_kupczyk?type=user]
