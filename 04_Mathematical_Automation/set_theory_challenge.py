def is_member(element, linear_sequence):
    # Manual scan loop
    # The sequence is a list/iterable and will return a boolean
    # Return True if found, otherwise Return False







# How to Find Power Set?
# In order to find a power set, follow these steps:
#
# Start with a null or empty set.
# Then add all combinations of subsets with one element.
# Then add all combinations of subsets with two elements.
# Do this till you reach the subsets with N-1 elements (where N is the total number of elements in the original set).
# Then add the original set.



    """
    DESIGN MATRIX: 3-TOKEN POWER SET GENERATION
    ======================================================================
    Counter (Int) | Binary Pattern | Protocol Switch  | Resulting Subset
    ----------------------------------------------------------------------
    0             | 000            | All Switches OFF | [] (Empty Set)
    1             | 001            | SNMP Only ON     | ["SNMP"]
    2             | 010            | HTTPS Only ON    | ["HTTPS"]
    3             | 011            | HTTPS & SNMP ON  | ["HTTPS", "SNMP"]
    4             | 100            | SSH Only ON      | ["SSH"]
    5             | 101            | SSH & SNMP ON    | ["SSH", "SNMP"]
    6             | 110            | SSH & HTTPS ON   | ["SSH", "HTTPS"]
    7             | 111            | All Switches ON  | ["SSH", "HTTPS", "SNMP"]
    ======================================================================
    Switch Bitwise Index Alignment:
    Position 2 (Bit Value 4): Controls "SSH"
    Position 1 (Bit Value 2): Controls "HTTPS"
    Position 0 (Bit Value 1): Controls "SNMP"
    """