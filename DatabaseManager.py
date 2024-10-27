import re
import sqlite3
import smtplib
import random
  

def login_validation(username: str = False, password: str = False) -> str:
    valid_user = r'^[0-9A-Za-z]{6,16}$'
    valid_pass = r'^(?=.*?[0-9])(?=.*?[A-Za-z]).{8,32}$' 
    
    if re.match(valid_user, username) and re.match(valid_pass, password):
        try:
            handler = sqlite3.connect('database/database.db')
            cursor = handler.cursor()
        except:
            print("Connection to DB failed.")
            return "FAILED"
        else:
                users = cursor.execute("SELECT user, password FROM users").fetchall()
                handler.close()
                for user in users:
                    if user[0] == username and user[1] == password:
                        return "FOUND"
    else:            
        return "NOT VALID"

        

def request_password_change(username: str = False) -> bool:
    email = 'puphealthapp@gmail.com'
    password = ''
    subject = "Redefinição de Senha."
    to_addr = 'archgabscontato@gmail.com'   
    code = str(random.randint(4000,9999))

    content = f"""
<html>
    <body>
        <h1>Redefinição de senha!</h1>
        <p>
            Este e-mail foi enviado automaticamente através do sistema de recuperação de senha do PupHealth.<br>
            Se este e-mail não foi requisitado por você, por favor entre em contato com: contato.joaogabriel@proton.me ou responda este e-mail.
        </p>
        <p style="font-size: 16px;">Código de redefinição: <b>{code}</b></p> 
    </body>
</html>

"""
    
    message = f"""From: {email}
To: {to_addr}
Subject: {subject}
MIME-Version: 1.0
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: 7bit

{content}
"""
    
    ans = sender(email=email, password=password, email_body=message, to_email=to_addr)
    if ans:
        return (ans, code)
    else:
        return (ans)

def sender(email: str, password: str, email_body: str, to_email: str) -> bool:
    print("SENDER")
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        try:
            server.starttls()
            server.login(email, password)
            server.sendmail(email, to_email, email_body.encode('utf-8'))
            server.close()
        except Exception as e: 
            print("Error Ocurred", e)
            return False
        else:
            return True
            
            