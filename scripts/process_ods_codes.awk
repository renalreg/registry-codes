# Usage: awk -v type=GP -f process_gp_practice.awk input.csv > /tmp/gp_processed.csv

BEGIN {
    FS = "\",\""
}

{

    # Remove leading " from first field
    sub(/^"/, "", $1)
    # Remove trailing " from last field
    sub(/"$/, "", $NF)
    
    # Store needed fields
    code = $1
    name = $2
    addr_line_3 = $5
    postcode = $10
    number = $18
    
    printf "%s;%s;%s;%s;%s;%s\n", code, name, addr_line_3, postcode, number, type
}