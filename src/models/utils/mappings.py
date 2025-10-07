APPLICATION_FIELD_MAPPING: dict[str, list[str]] = {
    # Business Info
    "Business Legal Name": [
        "business name", 
        "business legal name", 
        "LegalCorporate Name"
    ],
    "DBA": [
        "business dba",
        "dba",
        "doing business as"
    ],
    "Entity Type": [
        "business entity type",
        "business legal entity type",
        "business type of entity",
        "entity type",
        "legal entity type",
        "type of entity"
    ],
    "EIN": [
        "business tax id", 
        "business ein", 
        "business e i n", 
        "business federal tax-id", 
        "business federal taxid", 
        "business federal tax id", 
        "business federal tax-i d", 
        "business federal tax i d",
        "tax id", 
        "ein", 
        "e i n", 
        "federal tax-id", 
        "federal taxid", 
        "federal tax id", 
        "federal tax-i d", 
        "federal tax i d"
    ],
    "Business Start Date": [
        "business start date",
        "start date", 
        "Date Business Started", 
        "Date of Organization"
    ],
    "Business Phone Number": [
        "business phone",
        "business phone number",
        "phone"
    ],
    "Business Fax Number": [
        "fax",
        "business fax"
    ],
    "Business Email": [
        "business email",
        "email 1"
    ],
    "Business Address": [
        "Address", 
        "Business Address", 
        "Corporate Legal Address", 
        "business address", 
        "address", 
        "address,", 
        "business address street", 
        "address street", 
        "address street,", 
        "business address: address line 1"
    ],
    "Business Suite/Floor": [
        "business suite/floor",
        "business suite",
        "business floor"
    ],
    "Business City": [
        "city", 
        "city,", 
        "business city", 
        "business city,", 
        "business address: city"
    ],
    "Business State": [
        "State", 
        "State of Incorporation", 
        "State of Organization", 
        "state", 
        "state,", 
        "business state", 
        "business state,", 
        "business address: state"
    ],
    "Business Zip": [
        "Zip", 
        "Zip Code",  
        "business zip", 
        "business address: zip/postal code"
    ],
    "Business Industry": [
        "industry",
        "business industry",
        "type of business"
    ],
    "Business Description": [
        "description",
        "Business Description",
        "Describe your Business",
    ],

    # Owner Info
    "Owner Name": [
        "Owner Name", 
        "Primary Owner Name", 
        "Corporate OfficerOwner Name", 
        "Print Name", 
        "Name of Officer Signing Application", 
        "Name of Principal OwnerGuarantor", 
        "primary owner name: first"
    ],
    "Owner SSN": [
        "owner SSN", 
        "owner Social Sec", 
        "owner Social Security Number",
        "owner s s n", 
        "owner social",
        "SSN", 
        "Social Sec", 
        "Social Security Number",
        "s s n", 
        "social"
    ],
    "Owner Ownership Percent": [
        "owner ownership",
        "owner ownership %",
        "owner ownership percent",
        "ownership",
        "ownership %",
        "ownership percent"
    ],
    "Owner Date of Birth": [
        "owner date of birth", 
        "owner birth date", 
        "owner dob",
        "date of birth", 
        "birth date", 
        "dob"
    ],
    "Owner Email": [
        "owner email",
        "owner personal email",
        "email",
        "email 2"
    ],
    "Owner Phone Number": [
        "owner mobile phone",
        "owner mobile",
        "owner phone",
        "owner phone number",
        "cell phone",
        "owner cell phone",
        "mobile phone",
        "mobile",
        "mobile 1"
    ],
    "Owner Fax Number": [
        "personal fax",
        "owner personal fax",
        "owner fax",
        "mobile 2"
    ],
    "Owner Credit Score" :[
        "owner estimated fico score",
        "estimated fico score",
        "credit score",
        "owner credit score",
        "Estimated Credit Score",
        "owner Estimated Credit Score",
        "fico score",
        "owner fico score"
    ],
    "Owner Address": [
        "Address_2", 
        "Busin ss Address", 
        "owner Address",
        "owner address", 
        "owner address,", 
        "owner address street", 
        "owner address street,", 
        "owner address: address line 1",
        "Address", 
        "Business Address", 
        "Corporate Legal Address", 
        "business address", 
        "address", 
        "address,", 
        "business address street", 
        "address street", 
        "address street,", 
        "business address: address line 1"
    ],
    "Owner Suite/Floor": [
        "owner suite/floor",
        "owner suite",
        "owner floor"
    ],
    "Owner City": [
        "owner city", 
        "owner address: city",
        "city",
        "city,", 
        "City_2",
        "business city", 
        "business city,", 
        "business address: city"
    ],
    "Owner State": [
        "owner state",
        "owner address: state",
        "State", 
        "State of Incorporation", 
        "State of Organization", 
        "state", 
        "state,", 
        "business state", 
        "business state,", 
        "business address: state"
    ],
    "Owner Zip": [
        "owner zip",
        "owner zip code",
        "owner address: zip/postal Code",
        "Zip_2", 
        "Zip Code_2",
        "Zip", 
        "Zip Code",  
        "business zip", 
        "business address: zip/postal code"
    ],

    # Co-Owner Info
    "Co-Owner Name": [
        "Co-Owner Name", 
        "Primary Co-Owner Name", 
        "Corporate OfficerCo-Owner Name", 
        "primary Co-Owner name: first"
    ],
    "Co-Owner SSN": [
        "Co-Owner SSN", 
        "Co-Owner Social Sec", 
        "Co-Owner Social Security Number",
        "Co-Owner s s n", 
        "Co-Owner social"
    ],
    "Co-Owner Ownership Percent": [
        "Co-Owner ownership",
        "Co-Owner ownership %",
        "Co-Owner ownership percent"
    ],
    "Co-Owner Date of Birth": [
        "co-owner date of birth", 
        "co-owner birth date", 
        "co-owner dob"
    ],
    "Co-Owner Email": [
        "Co-Owner email",
        "Co-Owner personal email",
        "email 3"
    ],
    "Co-Owner Phone Number": [
        "Co-Owner mobile phone",
        "Co-Owner mobile",
        "Co-Owner phone",
        "Co-Owner phone number",
        "mobile 3"
    ],
    "Co-Owner Fax Number": [
        "Co-Owner personal fax",
        "Co-Owner fax",
        "mobile 4"
    ],
    "Co-Owner Credit Score" :[
        "Co-Owner estimated fico score",
        "Co-Owner credit score",
        "Co-Owner fico score"
    ],
    "Co-Owner Address": [
        "Address_3", 
        "Co-Owner Address",
        "Co-Owner address", 
        "Co-Owner address,", 
        "Co-Owner address street", 
        "Co-Owner address street,", 
        "Co-Owner address: address line 1"
    ],
    "Co-Owner Suite/Floor": [
        "Co-Owner suite/floor",
        "Co-Owner suite",
        "Co-Owner floor"
    ],
    "Co-Owner City": [
        "Co-Owner city", 
        "Co-Owner address: city"
    ],
    "Co-Owner State": [
        "Co-Owner state",
        "Co-Owner address: state"
    ],
    "Co-Owner Zip": [
        "Co-Owner zip",
        "Co-Owner zip code",
        "Co-Owner address: zip/postal Code"
    ],

    # Funding Info
    "Purpose of Funds": [
        "purpose of funds",
        "business purpose of funds"
    ],
    "Annual Business Revenue":[
        "annual business revenue",
        "business annual business revenue",
        "Total Annual Sales"
    ],
    "Requested Funding Amount": [
        "requested funding amount",
        "business requested funding amount",
        "How much cash funding are you applying for", 
        "Total Cash Needed"
    ],
    "Average Monthly Credit Card Volume": [
        "Average Monthly Credit Card Volume",
        "business Average Monthly Credit Card Volume",
        "CC Processing Monthly Volume"
    ],
    "Outstanding Receivables": [
        "outstanding receivables",
        "business outstanding receivables"
    ]
}


CONTRACT_FIELD_MAPPING: dict[str, list[str]] = {
    "Merchant Name": [
        "Business Legal Name",
        "Merchant Name",
        "LegalCorporate Name", 
        "business name",
    ],
    "Tele No": [
        "mobile phone",
        "mobile",
        "mobile 1"
        "owner mobile phone",
        "owner mobile",
        "owner phone",
        "owner phone number",
        "cell phone",
        "owner cell phone",
        "Phone",
        "Tele no",
        "business phone",
        "business phone number",
        "fax",
        "business fax",
    ],
    "Fee": [
        "fee",
        "fee percent"
    ],
    "EIN": [
        "business tax id", 
        "business ein", 
        "business e i n", 
        "business federal tax-id", 
        "business federal taxid", 
        "business federal tax id", 
        "business federal tax-i d", 
        "business federal tax i d",
        "tax id", 
        "ein", 
        "e i n", 
        "federal tax-id", 
        "federal taxid", 
        "federal tax id", 
        "federal tax-i d", 
        "federal tax i d"
    ],
    "Merchant Address": [
        "merchant address",
        "Address", 
        "Business Address", 
        "Corporate Legal Address", 
        "business address", 
        "address", 
        "address,", 
        "business address street", 
        "address street", 
        "address street,", 
        "business address: address line 1",
        "Address_2", 
        "Busin ss Address", 
        "owner Address",
        "owner address", 
        "owner address,", 
        "owner address street", 
        "owner address street,", 
        "owner address: address line 1",
        "Address", 
        "Business Address", 
        "Corporate Legal Address", 
        "business address", 
        "address", 
        "address,", 
        "business address street", 
        "address street", 
        "address street,", 
        "business address: address line 1"
    ],
    "City": [
        "city", 
        "city,", 
        "business city", 
        "business city,", 
        "business address: city",\
        "owner city", 
        "owner address: city",
        "city,", 
        "City_2",
        "business city", 
        "business city,", 
        "business address: city"
    ],
    "State": [
        "State", 
        "State of Incorporation", 
        "State of Organization", 
        "state", 
        "state,", 
        "business state", 
        "business state,", 
        "business address: state",
        "owner state",
        "owner address: state",
        "State", 
        "State of Incorporation", 
        "State of Organization", 
        "state", 
        "state,", 
        "business state", 
        "business state,", 
        "business address: state"
    ],
    "Zip": [
        "Zip", 
        "Zip Code",  
        "business zip", 
        "business address: zip/postal code",
        "owner zip",
        "owner zip code",
        "owner address: zip/postal Code",
        "Zip_2", 
        "Zip Code_2",
        "Zip", 
        "Zip Code",  
        "business zip", 
        "business address: zip/postal code"
    ],
    "Bank": [
        "bank",
        "bank name"
    ],
    "Routing": [
        "routing number",
        "routing"
        "Routing Number"
    ],
    "Account": [
        "account number",
        "account"
    ],
    "Line of Credit": [
        "line of credit",
        "loc",
        "loc amount",
        "Of The Line Of Credit Amount Of", 
        "Line of Credit amount of"
    ],
    "Initial Funding": [
        "initial funding",
        "funding",
        "funding amount",
        "initial funding amount",
        "initial funding of", 
        "Additional Funding Can Be Accepted After The Initial Funding of", 
        "No additional funding can be accepted after the initial funding of", 
        "Additional Funding Can Be Accepted After The Initial Funding", 
        "No additional funding can be accepted after the initial funding"
    ],
    "Print Name": [
        "primary owner name",
        "print name",
        "Owner Name", 
        "Primary Owner Name", 
        "Corporate OfficerOwner Name", 
        "Print Name", 
        "Name of Officer Signing Application", 
        "Name of Principal OwnerGuarantor", 
        "primary owner name: first"
    ]
}