import re, sqlite3
  
    
def login_validation(username: str = False, password: str = False) -> str:
    valid_user = r'^[0-9A-Za-z]{6,16}$'
    valid_pass = r'^(?=.*?[0-9])(?=.*?[A-Za-z]).{8,32}$'

    try:
        handler = sqlite3.connect('database/database.db')
        cursor = handler.cursor()
    except:
        print("Connection to DB failed.")
        return "FAILED"
    else:
        if re.match(valid_user, username) and re.match(valid_pass, password):
            users = cursor.execute("SELECT user, password FROM users").fetchall()
            for user in users:
                if user[0] == username and user[1] == password:
                    return "FOUND"
            
        return "NOT VALID"