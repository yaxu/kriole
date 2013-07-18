drop table chunk;
create table chunk (
  id int primary key auto_increment,
  pid int,
  starttime double,
  chunk int,
  v_pitch double,
  v_flux double,
  v_centroid double,
  index(v_pitch),
  index(v_flux),
  index(v_centroid)
);
