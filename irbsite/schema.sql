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
  radsafetyreview_date text,
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
  iacuc_number text,
  nothumansubjects text
);

DROP TABLE IF EXISTS supplemental;
CREATE TABLE supplemental (
  Protocol text,
  consentwaiver text,
  consentwaiver_type text,
  hipaawaiver text,
  hipaawaiver_type text,
  hipaaauth text,
  repository text,
  nihcert text,
  substudies text,
  mta text
);

DROP TABLE IF EXISTS safety;
CREATE TABLE safety (
  Protocol text,
  submit_date date,
  Submission_type text,
  Report_ID text,
  Report_type text,
  FU_report_no text,
  reportdate text,
  investigator text,
  investigator_det_date text,
  date_IRB_review text,
  date_back_IRB text,
  comments text
);
