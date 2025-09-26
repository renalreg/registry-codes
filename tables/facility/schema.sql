CREATE TABLE "extract".facility (
    code character varying(256) NOT NULL,
    pkb_out boolean DEFAULT false,
    pkb_in boolean DEFAULT false,
    pkb_msg_exclusions text[],
    creation_date timestamp without time zone DEFAULT now() NOT NULL,
    update_date timestamp without time zone,
    ukrdc_out_pkb boolean DEFAULT false,
    pv_out_pkb boolean DEFAULT false
);