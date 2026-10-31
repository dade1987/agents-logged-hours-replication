# GRANT PROXY with empty password incorrectly checks grantor's privileges

{code:sql}
CREATE USER u1@localhost;

CREATE USER u2@localhost IDENTIFIED BY 'oldpassword';
GRANT ALL PRIVILEGES ON *.* TO u2@localhost WITH GRANT OPTION;

show create user u2@localhost;

connect u,localhost,u1;
SHOW GRANTS;
GRANT PROXY ON u1@localhost TO u2@localhost IDENTIFIED VIA
  '' OR mysql_native_password USING PASSWORD('newpassword');

connection default;
show create user u2@localhost;

drop user u1@localhost;
drop user u2@localhost;
{code}

Reported by [Kévin GERVOT|https://mizu.re]
