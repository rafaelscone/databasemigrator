import mysql.connector
import sys
import os
from pathlib import Path
import time

mydb = False

# Import .env variables
from dotenv import load_dotenv
load_dotenv()


# Define folder
# Here you take the folder and file directory
path_folder = Path("/databases")

# Checking if environment are set
if 'MYSQL_HOST' not in os.environ or 'MYSQL_DATABASE' not in os.environ or 'MYSQL_USER' not in os.environ or 'MYSQL_PASSWORD' not in os.environ:
    print("not founded environment vars")
    sys.exit(1)


# Define vars
host = os.environ['MYSQL_HOST']
database = os.environ['MYSQL_DATABASE']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD'] 
port = os.environ['MYSQL_PASSWORD'] 
additional = False
if 'ADDITIONAL' in os.environ and os.environ['ADDITIONAL'] != '':
        additional = os.environ['ADDITIONAL']
        additional = additional.split("§")
        if len(additional)%2 !=0 :
            print("additional databases must be declare using character § example : user§password")
            sys.exit(1)

def change(sql):
    global mydb
    try:
        # Instanciando banco 
        instance = mydb.cursor()
        
        # Executando inserção
        instance.execute(sql)
        instance.close()
        return True
    except:
        print("Error executing changes to database...")
        return False
def execSQL(sql):
    global mydb
    try:
        # Instanciando banco 
        instance = mydb.cursor()
        
        # Executando inserção
        instance.execute(sql)
        
        result = instance.fetchall()
        return result
    except:
        print("Error connecting to database...")
        return False
def restoreDatabase(file,database):
    code = f'mysql -u{user} -p{password} -h{host} {database} < {file}'
    #print(code)
    exec = os.system(code)

    if exec != 0:
        print("Error inserting database...")
        sys.exit(1)
    return True

def main():
    global mydb
    # Let database ready
    mydb = False
    print("waiting to database ready")
    time.sleep(3)
    enter = True
    counter = 1

    while enter:
        print(f"try to connect {counter}/5")
        try:
            mydb = mysql.connector.connect(
                host= host,
                user= user,
                password= password, 
                auth_plugin= 'mysql_native_password',
                #database= database
            )
            enter = False
        except:
            print("error connecting...")
        counter = counter+1
        if counter >= 5:
            enter = False
            print("stopping try connect to database")
            sys.exit(1)
            break
        time.sleep(3)
    
    # Getting users from BD
    result = execSQL("select user from mysql.user;")
    users = []
    if result == False:
        print("Error connecting to database check the credentials...")
        sys.exit(1)
    [users.append(x[0].decode("utf-8") ) for x in result]

    # Validating database option
    result = execSQL("show databases;")
    databases= []
    # Checking connection
    if result == False:
        print("Error connecting to database check the credentials...")
        sys.exit(1)
    [databases.append(x[0]) for x in result]

    # Checking for new
    new_databases =[]
    new = {
        "database": database,
        "passwd": password
    }
    new_databases.append(new)
    if additional != False:
        base = []
        paswd =[]
        counter = 1
        for item in additional:
            if counter % 2 == 0:
                paswd.append(item)
            else:
                base.append(item)
            counter = counter +1
        
        counter = 0
        for item in base:
            
            new = {
                "database": item,
                "passwd": paswd[counter]
            }
            new_databases.append(new)
            counter = counter+1


    # Making changes on database
    for item in new_databases:
        if item['database'] not in databases:
            # Creating database
            print(f"creating database {item['database']}")
            sql = f"CREATE  database {item['database']};"
            if change(sql)== False:
                print("Error creating database ...")
                sys.exit(1)
        if item['database'] not in users:
            # Creating user
            print(f"creating user {item['database']}")
            sql = f"CREATE USER IF NOT EXISTS '{item['database']}'@'%' IDENTIFIED BY '{item['passwd']}';"
            
            if change(sql)== False:
                print("Error creating user ...")
                sys.exit(1)
            # Give user permissions
            print(f"Give user {item['database']} permissions")
            sql = f"GRANT USAGE ON *.* TO '{item['database']}'@'%' REQUIRE NONE WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;"
            sql2 = f"GRANT ALL PRIVILEGES ON `{item['database']}`.* TO '{item['database']}'@'%';"
            sql3 = f"GRANT ALL PRIVILEGES ON `{item['database']}\_%`.* TO '{item['database']}'@'%'; "
            
            if change(sql)== False or change(sql2)== False or change(sql3)== False:
                print("Error changing user permissions ...")
                sys.exit(1)

        # Checking restore file
        file = path_folder / (item['database']+".sql")
        if file.is_file():
            print(f"Verify restoring database...{item['database']}.sql")
            
            # Getting size of tables
            tables = execSQL(f"show tables from {item['database']}")

            # Checking connection
            if tables == False:
                print("Error connecting to database to check tables...")
                sys.exit(1)

            # Validate necessary update database
            if len(tables) != 0:
                print(f"Not necessary update database {item['database']}")
                continue
            # Update database
            print("update database...")
            exec_update = restoreDatabase(file, item['database'])
            if exec_update != True:
                print(f"Error retoring database {file}")
                sys.exit(1)
            print("Database restored")

    print("all operations executed")
    sys.exit(0)

if __name__ == "__main__":
    main()




