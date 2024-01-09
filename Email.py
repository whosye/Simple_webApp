from  werkzeug.security import generate_password_hash, check_password_hash

password ='123'
hashedP = generate_password_hash(password=password)

print(hashedP)

check_password_hash(pwhash='scrypt:32768:8:1$yJiBZjkbVEFa3o5B$82f81b14233fb3b0981d9ad1fcfc1a11e0144cb748613b14ae550acaf57d5263642ded4f52250194418a2fb919baa7d4cf13643de44ba7aed4b2cedd78601651', password=password )