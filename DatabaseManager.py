import re
import sqlite3
import smtplib
import random

# Parameters
valid_user = r'^[0-9A-Za-z]{6,16}$'
valid_pass = r'^(?=.*?[0-9])(?=.*?[A-Za-z]).{8,32}$' 
  

def login_validation(username: str = False, password: str = False) -> str:
    
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

   
def get_user_email(username: str) -> str:
    """Verifica se o usuário existe e retorna o e-mail associado."""
    if not re.match(valid_user, username):
        print("Username não é válido.")
        return False  # Retorna None se o username não for válido

    try:
        handler = sqlite3.connect('database/database.db')
        cursor = handler.cursor()
    except sqlite3.Error:
        print("Connection to DB failed.")
        return False  # Retorna None se a conexão falhar

    users = cursor.execute("SELECT user, email FROM users").fetchall()
    handler.close()

    for user in users:
        print(user[0])
        if user[0] == username:
            return user[1]  # Retorna o e-mail associado ao usuário

    return False  # Retorna None se o usuário não for encontrado


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
            
            
def request_password_change(username: str) -> bool:
    """Gera um código de redefinição e envia um e-mail se o usuário existir."""
    email = 'puphealthapp@gmail.com'
    password = 'ujjf oirm izya jhvx'
    subject = "Redefinição de Senha."
    code = str(random.randint(1000, 9999))
    to_addr = get_user_email(username)
    
    if to_addr is False:
        return False  # Retorna False se o usuário não for encontrado

    # Conteúdo do e-mail
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
        print('Retornando código e true')
        return code  # Retorna o código se o e-mail foi enviado com sucesso
    else:
        return False  # Retorna False se o envio falhar


def is_code_valid(input_code, code) -> bool:
    print(input_code, code)    
