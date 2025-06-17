CREATE TABLE "extract".code_map (
    source_coding_standard character varying(256) NOT NULL,
    source_code character varying(256) NOT NULL,
    destination_coding_standard character varying(256) NOT NULL,
    destination_code character varying(256) NOT NULL,
    creation_date timestamp without time zone DEFAULT now() NOT NULL,
    update_date timestamp without time zone
);