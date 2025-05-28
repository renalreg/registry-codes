
CREATE TABLE "extract".modality_codes (
    registry_code character varying(8) NOT NULL,
    registry_code_desc character varying(100),
    registry_code_type character varying(3) NOT NULL,
    acute bit(1) NOT NULL,
    transfer_in bit(1) NOT NULL,
    ckd bit(1) NOT NULL,
    cons bit(1) NOT NULL,
    rrt bit(1) NOT NULL,
    equiv_modality character varying(8),
    end_of_care bit(1) NOT NULL,
    is_imprecise bit(1) NOT NULL,
    nhsbt_transplant_type character varying(4),
    transfer_out bit(1)
);