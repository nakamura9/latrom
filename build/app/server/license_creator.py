import datetime
import json
import hashlib
import sys

# Improve this program by providing the ability to split data into a private 
# and public key. Add the signature and the public key to the license file 
# while only allowing the public key to be used for verifying the license.
data = {}
if len(sys.argv) == 1:
    customer = input('Enter the name of the customer: ')
    duration = input("Enter the duration of the license in days: ")
    users = input("Enter the number of users: ")
    employees =  input("State the number of Employees: ")

    data = {
        'customer_name': customer,
        'expiry_date': (datetime.date.today() + datetime.timedelta(
            days=int(duration))).strftime('%d/%m/%y'),
        'customer_id': 1,# fix
        'date_issued': datetime.date.today().strftime('%d/%m/%y'),
        'number_users': users,
        'number_employees': employees
    }

else:
    if not sys.argv[1].endswith('.json'):
        raise Exception('The file type is incorrect')
    with open(sys.argv[1], 'r') as fil:
        data = json.load(fil)

    if data["customer_name"] == "Trial User":
        data["date_issued"] = datetime.date.today().strftime("%d/%m/%y")
        data["expiry_date"] = (datetime.date.today() + datetime.timedelta(
            days=14)).strftime("%d/%m/%y")


data_string = json.dumps(data)
data_bytes = bytes(data_string, 'ascii')
hash = hashlib.sha3_512(data_bytes).hexdigest()

license_data = {
    'signature': hash,
    'license': data
}

with open('license.json', 'w') as f:
    json.dump(license_data, f)
