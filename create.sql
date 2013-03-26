drop table chunk;
create table chunk (
  id int primary key auto_increment,
  pid int,
  starttime double,
  chunk int,
  v_pitch double,
  v_flux double,
  index(value)
);
