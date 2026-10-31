# SET AUTHORIZATION un-expired passwords

{code:sql}
create user u1@localhost;
alter user u1@localhost password expire;
connect con1,localhost,u1;
--error ER_MUST_CHANGE_PASSWORD
select 1;
set session authorization u1@localhost;
select 2;
set password=password('');
select 3;
disconnect con1;
connection default;
drop user u1@localhost;
{code}

Reported by https://github.com/uaaw
