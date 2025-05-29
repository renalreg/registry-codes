# Registry Table Definitions

This document outlines the database tables used in the registry-codes system. All tables reside within the `extract` schema.

## Table Definitions

### code_exclusion

Not sure what this does see here: https://github.com/renalreg/resources/tree/master/codes/code_exclusions

| Column | Type | Description |
|--------|------|-------------|
| `coding_standard` | varchar | The coding standard to exclude |
| `code` | varchar | The specific code to exclude |
| `system` | varchar | The system where exclusion applies |

### code_list

Definition of codes. See here https://github.com/renalreg/resources/tree/master/codes/code_lists

| Column | Type | Description |
|--------|------|-------------|
| `coding_standard` | varchar(256) | The coding standard |
| `code` | varchar(256) | The code value |
| `description` | varchar(256) | Description of the code |
| `object_type` | varchar(256) | Type of object the code represents |
| `units` | varchar(256) | Measurement units if applicable |
| `pkb_reference_range` | varchar(10) | PatientKnowsBest reference range |
| `pkb_comment` | text | PatientKnowsBest comments |

### code_map
The Registry works with many coding systems - both homebred RR codes and outside ones like SNOMED. These coding systems have shifted over time, but we still need to read old data. This table lets us map codes between different systems in both forward and backward ways, linking old and new codes. See here: https://github.com/renalreg/resources/tree/master/codes/code_conv_lists

| Column | Type | Description |
|--------|------|-------------|
| `source_coding_standard` | varchar(256) | Original coding system |
| `source_code` | varchar(256) | Original code |
| `destination_coding_standard` | varchar(256) | Target coding system |
| `destination_code` | varchar(256) | Target code |

### facility

** don't know what this does

| Column | Type | Description |
|--------|------|-------------|
| `code` | varchar(256) | Facility code |
| `pkb_out` | boolean | PKB output flag |
| `pkb_in` | boolean | PKB input flag |
| `pkb_msg_exclusions` | text[] | PKB message exclusions |
| `ukrdc_out_pkb` | boolean | UKRDC to PKB output flag |
| `pv_out_pkb` | boolean | PatientView to PKB output flag |

### modality_codes

Stores treatment modality definitions.

| Column | Type | Description |
|--------|------|-------------|
| `registry_code` | varchar(8) | Unique modality code |
| `registry_code_desc` | varchar(100) | Description of modality |
| `registry_code_type` | varchar(3) | Type of modality code |
| `acute` | bit(1) | Flag for acute treatments |
| `transfer_in` | bit(1) | Flag for patient transfers in |
| `ckd` | bit(1) | Chronic kidney disease flag |
| `cons` | bit(1) | Conservative care flag |
| `rrt` | bit(1) | Renal replacement therapy flag |
| `equiv_modality` | varchar(8) | Equivalent modality code |
| `end_of_care` | bit(1) | End of care flag |
| `is_imprecise` | bit(1) | Flag for imprecise codes |
| `nhsbt_transplant_type` | varchar(4) | NHS Blood and Transplant type |
| `transfer_out` | bit(1) | Flag for patient transfers out |

### rr_codes

Large picklist of codes and definitions. I think this is basically the same as code_list but it has been extracted out of the renalregistry db rather than the ukrdc. 

| Column | Type | Description |
|--------|------|-------------|
| `id` | varchar(10) | Unique ID |
| `rr_code` | varchar(10) | Registry code |
| `description_1` | varchar(255) | Main description |
| `old_value` | varchar(10) | Former value |
| `new_value` | varchar(10) | Current value |

### rr_data_definition

Defines data fields and their validation rules.

| Column | Type | Description |
|--------|------|-------------|
| `TABLE_NAME` | varchar(30) | Name of table |
| `field_name` | varchar(30) | Name of field |
| `mandatory` | numeric(1,0) | Whether field is required |
| `TYPE` | varchar(1) | Data type |
| `alt_constraint` | varchar(30) | Alternative constraint |
| `paed_mand` | numeric(1,0) | Mandatory for paediatric |
| `ckd5_mand` | numeric(1,0) | Mandatory for CKD5 |
| `ckd4_mand` | numeric(1,0) | Mandatory for CKD4 |
| `dependant_field` | varchar(30) | Field this depends on |
| `alt_validation` | varchar(30) | Alternative validation |
| `load_min` | numeric(38,4) | Minimum load value |
| `load_max` | numeric(38,4) | Maximum load value |
| `aki_mand` | numeric(1,0) | Mandatory for AKI |
| `rrt_mand` | numeric(1,0) | Mandatory for RRT |
| `cons_mand` | numeric(1,0) | Mandatory for consultant |
| `valid_before_dob` | numeric(1,0) | Valid before date of birth |
| `valid_after_dod` | numeric(1,0) | Valid after date of death |
| `in_quarter` | numeric(1,0) | Quarterly flag |

### satellite_map

Maps satellite units to their main units.

| Column | Type | Description |
|--------|------|-------------|
| `satellite_code` | varchar(10) | Unique code for satellite unit |
| `main_unit_code` | varchar(10) | Code for the main unit |