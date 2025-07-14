
CREATE TABLE "extract".rr_codes (
    id character varying(10) NOT NULL,
    rr_code character varying(10) NOT NULL,
    description_1 character varying(255),
    description_2 character varying(70),
    description_3 character varying(60),
    old_value character varying(10),
    old_value_2 character varying(10),
    new_value character varying(10)
);