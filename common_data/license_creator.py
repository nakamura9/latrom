import json
import hashlib

# Improve this program by providing the ability to split data into a private 
# and public key. Add the signature and the public key to the license file 
# while only allowing the public key to be used for verifying the license.

l = {
    'customer_id': 1,
    'customer_name': 'customer',
    'date_issued': '21/01/19',
    'expiry_date': '21/09/20',
    'number_users': 5,
    'number_employees': 4
}

data_string = json.dumps(l)
data_bytes = bytes(data_string, 'ascii')
hash = hashlib.sha3_512(data_bytes).hexdigest()

license_data = {
    'signature': hash,
    'license': l
}

with open('license.json', 'w') as f:
    json.dump(license_data, f)
