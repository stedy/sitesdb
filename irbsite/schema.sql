DROP TABLE IF EXISTS createdby;
CREATE TABLE createdby (
  Protocol text,
  user_id text,
  pub_date integer
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

DROP TABLE IF EXISTS personnel;
CREATE TABLE personnel (
  Protocol text,
  added_date date,
  name text,
  role text,
  removed_date date,
  responsibility text
);

DROP TABLE IF EXISTS reviewcomm;
CREATE TABLE reviewcomm (
  Protocol text,
  Title text, IR text, PI text,
  Primary_IRB text, Committee text,
  Review_Type text, cim text, FH_IBC text,
  pim text, UW_ehs text, src text,
  iacuc text,
  rad_safety text, other text,
  init_approval_date text,
  irb_expires text, fhcrc_renewal text,
  uw_renewal text, rad_safety_renewal text
);

DROP TABLE IF EXISTS status_list;
CREATE TABLE status_list (
  statustype text
);
