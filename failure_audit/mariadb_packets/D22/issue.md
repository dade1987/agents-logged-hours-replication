# Changing INTERVAL of SYSTEM_TIME partitioning does not move history to the new partitions

h3. Reproduce
{code:sql}
set @@session.time_zone='+00:00';
create table t1 (x int,
  row_start timestamp(6) as row start invisible,
  row_end timestamp(6) as row end invisible,
  period for system_time (row_start, row_end)) with system versioning
partition by system_time interval 1 hour
starts '2000-01-01 00:00:00' partitions 4;
set timestamp= unix_timestamp('2000-01-01 00:30:00');
insert t1 values (0);
set timestamp= unix_timestamp('2000-01-01 01:30:00');
update t1 set x= 1;
set timestamp= unix_timestamp('2000-01-01 02:30:00');
update t1 set x= 2;
alter table t1 partition by system_time interval 2 hour
starts '2000-01-01 00:00:00';
select x, row_end from t1 partition (p0);
select x, row_end from t1 partition (p1);
{code}

h3. Result
{code:sql}
select x, row_end from t1 partition (p0);
x	row_end
select x, row_end from t1 partition (p1);
x	row_end
0	2000-01-01 01:30:00.000000
{code}

h3. Expected
{code:sql}
select x, row_end from t1 partition (p0);
x	row_end
0	2000-01-01 01:30:00.000000
select x, row_end from t1 partition (p1);
x	row_end
1	2000-01-01 02:30:00.000000
{code}

After the ALTER the layout is p0 = [00:00, 02:00), p1 = [02:00, 04:00), but the history rows stay where the old INTERVAL 1 HOUR layout put them: the row with row_end 01:30 is left in p1, and p0 is empty. A changed INTERVAL (or STARTS) must rebuild the table and redistribute the history.

h3. Notes

Caused by MDEV-29873 (commit 732d1ec3aef). It replaced
{code:cpp}
memcmp(&part_info->vers_info->interval,
       &tab_part_info->vers_info->interval,
       sizeof(Vers_part_info::interval))
{code}
(true when the intervals differ) with
{code:cpp}
part_info->vers_info->interval == tab_part_info->vers_info->interval
{code}
(true when they are equal) in prep_alter_part_table(). Since then a changed interval takes the fast ALTER path, which keeps the rows in their partitions, and an unchanged interval takes the copy path. The comment above still says "If interval is changed we can not do fast alter".

Affects 10.9.8, 10.10.6, 10.11.5 and later.

