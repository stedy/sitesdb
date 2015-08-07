DROP TABLE IF EXISTS user;
CREATE TABLE user (user_id integer primary key autoincrement, username string,
                     email string, pw_hash string);

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
	uwconf_date text
);

DROP TABLE IF EXISTS createdby;
CREATE TABLE createdby (
	Protocol text,
	user_id text,
	pub_date integer
      );
