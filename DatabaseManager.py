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
            handler.close()
            for user in users:
                if user[0] == username and user[1] == password:
                    return "FOUND"
            
        return "NOT VALID"


def initialize_ssl(configuration: dict = False, toemail: str = False, message: str = False) -> bool: pass
#    if configuration and message and toemail:   
#         try:
#             with smtplib.SMTP(configuration['smtp_server'], configuration["port"],) as server:
#                 server.starttls(configuration["email"], configuration["password"])
#                 server.sendmail(configuration["email"], toemail, message)
#         except Exception as e:
#             print("SSL connection failed, maybe retry?.", e,sep="\n")
#             return False
#         else:
#             server.close()
#             return True
            

def request_password_change(username: str = False) -> str: pass
    # message = f"""
    # Atenção {username}, uma requesição de alteração de senha foi pedida, se não foi você que requisitou, por gentileza ignore este e-mail.\n
    # Se não, segue código de recuperação: {random.randint(3000, 9999)}.
    
    # E-mail enviado por {os.getlogin()}.
    # """
    
    # configuration = {
    #     "port": 587,
    #     "email": 'puphealthapp@gmail.com',
    #     "smtp_server": "smtp.gmail.com",
    #     "password": 'zvot nndi zwnc xxxxxxxxxxxxxxxx',
    # }    
    
    # try:
    #     handler = sqlite3.connect('database/database.db')
    #     cursor = handler.cursor()
    # except: 
    #     print("Connection to DB failed.")
    #     return "FAILED"
    # else:
    #     for user in cursor.execute("SELECT user, email FROM users").fetchall() :
    #         if username == user[0]:
    #             toemail = user[1]        
                
    #     has_it_been_sent = initialize_ssl(configuration=configuration, toemail=toemail, message=message)
    #     if has_it_been_sent:
    #         return "EMAIL SENT"
    #     else:
    #         return "FAILED TO SEND EMAIL TO TARGET"
    # finally:
    #     handler.close()
        
