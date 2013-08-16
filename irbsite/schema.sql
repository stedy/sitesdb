DROP TABLE IF EXISTS createdby;
CREATE TABLE createdby (
  Protocol text,
  user_id text,
  pub_date integer
);

DROP TABLE IF EXISTS studystaff;
CREATE TABLE studystaff (
  Protocol text,
  Name text,
  role text,
  id Integer PRIMARY KEY AUTOINCREMENT
);

DROP TABLE IF EXISTS reviewtype;
CREATE TABLE reviewtype (
  Protocol text,
  radsafetyreview text,
  fhibc text,
  src text,
  uwehs text,
  cim text,
  pim text
);

DROP TABLE IF EXISTS dontype;
CREATE TABLE dontype (
  Protocol text,
  hctallo text,
  hctauto text,
  heme text,
  solidorgan text,
  autoimmune text,
  bv text
);

DROP TABLE IF EXISTS commreviews;
CREATE TABLE commreviews (
  Protocol text,
  full text,
  coop text,
  minimal text,
  irbauth text,
  exempt text,
  iacucauth text,
  nothumansubjects text
);

DROP TABLE IF EXISTS supplemental;
CREATE TABLE supplemental (
  Protocol text,
  consentwaiver text,
  hipaawaiver text,
  hipaaauth text,
  repository text,
  nihcert text,
  substudies text,
  mta text
);
