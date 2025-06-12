CREATE TABLE "extract".code_list (
    coding_standard character varying(256) NOT NULL,
    code character varying(256) NOT NULL,
    description character varying(256),
    object_type character varying(256),
    creation_date timestamp without time zone DEFAULT now() NOT NULL,
    update_date timestamp without time zone,
    units character varying(256),
    pkb_reference_range character varying(10),
    pkb_comment text
);