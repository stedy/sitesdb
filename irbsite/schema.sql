DROP TABLE IF EXISTS dontype;
CREATE TABLE dontype (
    Protocol text,
    Studypop text
);

DROP TABLE IF EXISTS reviewtype;
CREATE TABLE reviewtype (
    Protocol text,
    Reviewcomm text
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

DROP TABLE IF EXISTS supplemental;
CREATE TABLE supplemental (
	Protocol text,
	consentwaiver text,
	consentwaiver_type text,
	hipaawaiver text,
	hipaawaiver_type text,
	repository text,
	nihcert text,
	substudies text,
	mta text,
	childrens_supp text,
	multi_supp text,
	mta_dua text,
	CRDGeneral text,
	Studyspecific text,
	UWHIPAA text,
	CRD text,
	uw_conf text
);

DROP TABLE IF EXISTS createdby;
CREATE TABLE createdby (
	Protocol text,
	user_id text,
	pub_date integer
);

DROP TABLE IF EXISTS personnel;
CREATE TABLE personnel (
  Protocol text,
  added_date date,
  name text,
  role text,
  removed_date text,
  responsibility text
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

DROP TABLE IF EXISTS status_list;
CREATE TABLE status_list (
    statustype text,
    reviewtype text
);

DROP TABLE IF EXISTS sponsor;
CREATE TABLE sponsor (
  Protocol text,
  Sponsor_protocol text,
  Sponsor text,
  Ind text,
  Ind_number text,
  Drug_name text,
  Study_total text,
  Local_total text
);

INSERT INTO status_list (statustype) VALUES ("Pending");
INSERT INTO status_list (statustype) VALUES ("Recruitment not yet begun (UW only)");
INSERT INTO status_list (statustype) VALUES ("Approved, Open to Accrual");
INSERT INTO status_list (statustype) VALUES ("Approved with minor modifications");
INSERT INTO status_list (statustype) VALUES ("Disapproved");
INSERT INTO status_list (statustype) VALUES ("Closed to Accrual - Accrual on hold");
INSERT INTO status_list (statustype) VALUES ("Closed to Accrual - Activity limited to LTFU collection");
INSERT INTO status_list (statustype) VALUES ("Closed to Accrual - Limited to Analysis");
INSERT INTO status_list (statustype) VALUES ("Closed");
INSERT INTO status_list (statustype) VALUES ("Research never began");
INSERT INTO status_list (statustype) VALUES ("Other");
INSERT INTO status_list (reviewtype) VALUES ("Full");
INSERT INTO status_list (reviewtype) VALUES ("Minimal Risk (UW Expedited)");
INSERT INTO status_list (reviewtype) VALUES ("Exempt");
INSERT INTO status_list (reviewtype) VALUES ("Use of identifiable data/specimens");
INSERT INTO status_list (reviewtype) VALUES ("Coop");
INSERT INTO status_list (reviewtype) VALUES ("IRB Authorization");
INSERT INTO status_list (reviewtype) VALUES ("IACUC Authorization");
INSERT INTO status_list (reviewtype) VALUES ("Non-human subjects");
