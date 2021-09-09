#import libraries
import random 
import string
import xml.etree.ElementTree as xml
from cryptography.fernet import Fernet
import psycopg2

def GenerateXML(fileName):
    #Creating the first item of the XML Tree
    root = xml.Element("AccountDB")

    #Creating the child of the first item (which is AccountDB)
    accounts = xml.Element("Accounts")

    #Adding the child (accounts) to the parent (root)
    root.append(accounts)

    #Creating sub childs
    xusername = xml.SubElement(accounts, "Username")
    xusername.text = username
    
    xpassword = xml.SubElement(accounts, "Password")
    xpassword.text = password
    
    xwebsite = xml.SubElement(accounts, "Website")
    xwebsite.text = weblink
    
    #Giving an 'ID' starting from 0 for the entries
    for (id, accounts) in enumerate(root.findall('Accounts')):
        accounts.set('id', str(id))

    #Append root to the XML Tree
    tree=xml.ElementTree(root)
    with open(fileName, "wb") as files:
        tree.write(files)

#Generate a key and save it into a file
def write_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

#Loads the key from the current directory named 'key.key'
def load_key():
    return open("key.key", "rb").read()

#Given a filename (str) and key (bytes), it encrypts the file and writes it
def encrypt(filename, key):
    f = Fernet(key)
    with open(filename, "rb") as file:
        # read all file data
        file_data = file.read()

    # encrypt data
    encrypted_data = f.encrypt(file_data)

    # write the encrypted file
    with open(filename, "wb") as file:
        file.write(encrypted_data)

#Given a filename (str) and key (bytes), it decrypts the file and writes it
def decrypt(filename, key):
    f = Fernet(key)
    with open(filename, "rb") as file:
        # read the encrypted data
        encrypted_data = file.read()

    # decrypt data
    decrypted_data = f.decrypt(encrypted_data)

    # write the original file
    with open(filename, "wb") as file:
        file.write(decrypted_data)

#welcome screen & request input from the user
print('+===========================================+')
print('|          Password Generator v1.2          |')
print('+===========================================+')
print('1 --- Generate Password')
print('2 --- Password Management')
select_option = int(input('\nOption number: '))

if select_option == 1:
    #Generate the key, if it has already generated then you can comment it so that it doesn't regenerate and mess up the previous encryption.
    #write_key()
    key = load_key()
    f = Fernet(key)
    
    #custom variables
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    symbols = string.punctuation
    combined = lower + upper + num + symbols
    
    #time to pop the question
    weblink = input('\nPlease enter the website URL: ')
    username = input('\nPlease enter the username for this account: ')
    pw_length = int(input('\nPlease enter the lengh of the password you wish to generate: '))
    
    #randomize everything
    temp = random.sample(combined,pw_length)
    password = "".join(temp)
    
    #encrypting password
    #encoded_password = password.encode()
    #encrypted_password = f.encrypt(encoded_password)

    #Connect to postgresql
    con = psycopg2.connect(
    database="pypassdb", 
    user="postgres", 
    password="flykite123", 
    host="127.0.0.1", 
    port="5432")
    print("Database opened successfully!")
    
    #create a cursor which lets you interact with postgresql
    cur = con.cursor()
    
    #use the cursor to insert data to the db (pgcrypto encrypted)
    #cur.execute("insert into public.accounts (website,username,password) values (%s,%s,crypt(%s,gen_salt('bf',8)))", (weblink,username,password)) 
    
    #use the cursor to insert data to the db (python encrypted)
    cur.execute("insert into public.accounts (website,username,password) values (%s,%s,%s)", (weblink,username,password)) 

    cur.execute("select website,username,password from ACCOUNTS")
    rows = cur.fetchall()
    for r in rows:
        #decrypted_password = r[2]
        #decrypted_password = decrypted_password.encode()
        #decrypted_password = f.decrypt(decrypted_password)
        print(f"Website: {r[0]} \nUsername: {r[1]} \nPassword: {r[2]}")
        print("-------------------------------------------------------------")

    #Commit (save) the changes to the actual DB
    con.commit()
    #Always remember to close the connection
    cur.close()
    con.close()

    #show them the money
    #print('Website: ', weblink)
    #print('Username: ', username)
    #print('Generated Password: ', password)
    
    #GenerateXML("AccountDB.xml")
    #encrypt("AccountDB.xml",key)

elif select_option == 2:
    print('\nAccount information')
    print('------------------------------')
    key = load_key()
    decrypt('AccountDB.xml', key)
    mytree = xml.parse('AccountDB.xml')
    myroot = mytree.getroot()
    for x in myroot.findall('Accounts'):
        website =  x.find('Website').text
        username = x.find('Username').text
        password = x.find('Password').text
        print("Website: ", website + "\nUsername: ", username +"\nPassword: ", password)
        print('------------------------------')
    encrypt("AccountDB.xml",key)

else:
    print('Haiyooooo... There is only one option and you still fucked up')