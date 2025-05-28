CREATE TABLE "extract"."satellite_map" (
    satellite_code character varying(10) NOT NULL,
    main_unit_code character varying(10) NOT NULL,
    creation_date timestamp without time zone DEFAULT now() NOT NULL,
    update_date timestamp without time zone
);