from datetime import datetime
from ReportGenerator import ReportCreator
import sqlite3
import smtplib
import random
import json
import re

class LoginManager():
    def __init__(self):
        # Parameters
        self.valid_user = r'^[0-9A-Za-z]{6,16}$'
        self.valid_pass = r'^(?=.*?[0-9])(?=.*?[A-Za-z]).{8,32}$' 
    
    # TODO refactor this to a class
    def login_validation(self, username: str = False, password: str = False) -> str:  
        if re.match(self.valid_user, username) and re.match(self.valid_pass, password):
            try:
                handler = sqlite3.connect('database/database.db')
                cursor = handler.cursor()
            except Exception as e:
                print("Connection to DB failed.", e)
                return "FAILED"
            else:
                    users = cursor.execute("SELECT user, password FROM users").fetchall()
                    handler.close()
                    for user in users:
                        if user[0] == username and user[1] == password:
                            return "FOUND"
        return "NOT VALID"

    
    def get_user_email(self, username: str):
        """Verifica se o usuário existe e retorna o e-mail associado."""
        if not re.match(self.valid_user, username):
            print("Username não é válido.")
            return False  
        
        try:
            handler = sqlite3.connect('database/database.db')
            cursor = handler.cursor()
        except sqlite3.Error:
            print("Connection to DB failed.")
            return False  

        users = cursor.execute("SELECT user, email FROM users").fetchall()
        handler.close()

        for user in users:
            print(user[0])
            if user[0] == username:
                # Retorna o e-mail associado ao usuário
                return user[1]  
        # Caso nada seja encontrado, assume que não existe o user na DB
        return False  


    def sender(self, email: str, password: str, email_body: str, to_email: str) -> bool:
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
                
                
    def send_password_change(self, username: str):
        """Gera um código de redefinição e envia um e-mail se o usuário existir."""
        email = 'puphealthapp@gmail.com'
        password = 'ujjf oirm izya jhvx'
        subject = "Redefinição de Senha."
        code = str(random.randint(1000, 9999))
        to_addr = self.get_user_email(username)
        
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
        # "Catcher" se a mensagem foi enviada com sucesso.
        ans = self.sender(email=email, password=password, email_body=message, to_email=to_addr)
        if ans:
            print('Retornando código e true')
            return code  # Retorna o código se o e-mail foi enviado com sucesso
        else:
            return False  # Retorna False se o envio falhar


    def is_code_valid(self, input_code: str, code: str) -> bool:
        return input_code == code


    def change_password(self, input_password: str, user: str) -> bool:
        input_password = input_password.get()
        print("Password", input_password)
        
        if re.match(self.valid_pass, input_password):
            try:
                handler = sqlite3.connect('database/database.db')
                cursor = handler.cursor()
                cursor.execute("UPDATE users SET password = ? WHERE user = ?", (input_password,user))
                handler.commit()
            except sqlite3.Error as e:
                print(e)
                return False
            else:
                print("PASSWORD CHANGED")
            finally:
                handler.close()
                return True
        else:
            print("NOT VALID")
            return False

    
class DashboardUtilities():
    def __init__(self):
        self.handler = sqlite3.connect('database/database.db')
        self.cursor = self.handler.cursor()
        self.vaccine_pattern = r"^([a-zA-Zá-úÁ-Ú0-9]+(?:\s+[a-zA-Zá-úÁ-Ú0-9]+)*)(,\s*([a-zA-Zá-úÁ-Ú0-9]+(?:\s+[a-zA-Zá-úÁ-Ú0-9]+)*))*$"


    def get_user(self, usr):
        res = self.cursor.execute('select name from users where user = ?', (usr,)).fetchone()
        return res


    def validate_inputs(self, itens: dict, new_tutor = False) -> bool:
        print("ARRIVED_VALIDATE_INPUTS")
        if re.fullmatch(self.vaccine_pattern, itens['vacinastomadas'].get()) is not None:
            
            vaccine_list = itens['vacinastomadas'].get().split(',')
            vacinas_json = json.dumps([
                {"nome": vacina.strip(), "data": datetime.now().strftime("%d-%m-%Y")}
                for vacina in vaccine_list
            ])
            
            # Criando variáveis modificadas para facilitar inserção no banco de dados...
            if new_tutor is not False:
                tutor = new_tutor.lower()
                self.cursor.execute("INSERT INTO tutor(nome_tutor) VALUES(?)", (tutor,))
                self.handler.commit()
            else:
                tutor = itens['tutor'].get().lower()
                
            pet_name = itens['nomedopet'].get().lower()
            genero = itens['genero'].get().lower()
            raca = itens['raca'].get().lower()           
            
            catch = self.test_tutor(tutor, pet_name)
            
            print(catch)
            
            match catch:
                case "ANIMAL_ALREADY_ASSIGNED":
                    print("ANIMAL_ALREADY_ASSIGNED")
                    return "ANIMAL_ALREADY_ASSIGNED"
                case "ID_MISSING":
                    print("ID_MISSING")
                    return "ID_MISSING"
                case _:
                    try:
                        self.cursor.execute(
                                "INSERT INTO patients (nome, race, vacinas_tomadas, tutor, genero) VALUES (?, ?, ?, ?, ?)",
                                (pet_name, raca, vacinas_json, catch, genero))
                        self.handler.commit()
                    except Exception as e: print("DB_ERROR", e)
                    else:
                        print("ANIMAL_INSERTED_DB")
                        return "ANIMAL_INSERTED_DB"
        return "VACCINE_PATTERN_WRONG"
            
            
    def test_tutor(self, tutor_name: str, petname: str):
        tutores = self.cursor.execute("SELECT nome_tutor, id FROM tutor").fetchall()
        for tutor in tutores:
            # Caso o tutor exista, verificar se o animal já não foi cadastrado
            if tutor[0] == tutor_name: 
                # Se não já não estiver cadastrado o nome do pet no ref do tutor...
                if len(self.cursor.execute("SELECT nome FROM patients WHERE nome = ? AND tutor = ?", (petname, tutor[1])).fetchall()) == 0:
                    # Retorne o ID do tutor.
                    return tutor[1]
                else:
                    return "ANIMAL_ALREADY_ASSIGNED"
        return "ID_MISSING"
    
    def list_patients(self, mode: str = "INIT", tutor: str = "") -> list:
        match mode:
            case "INIT":
                return self.cursor.execute('''
    SELECT p.id, p.nome AS paciente_nome, t.nome_tutor AS tutor_nome, p.vacinas_tomadas 
    FROM patients p 
    JOIN tutor t ON p.tutor = t.id 
    ORDER BY p.id
''').fetchall()
            case "Tutor":
                return self.cursor.execute('''
        SELECT p.id, p.nome AS paciente_nome, t.nome_tutor AS tutor_nome, p.vacinas_tomadas 
        FROM patients p 
        JOIN tutor t ON p.tutor = t.id 
        WHERE t.nome_tutor = ? 
        ORDER BY p.id
    ''', (tutor,)).fetchall() 
            case "Nome Paciente": 
                return self.cursor.execute('''
        SELECT p.id, p.nome AS paciente_nome, t.nome_tutor AS tutor_nome, p.vacinas_tomadas 
        FROM patients p 
        JOIN tutor t ON p.tutor = t.id 
        WHERE paciente_nome = ? 
        ORDER BY p.id
    ''', (tutor,)).fetchall() 
        

    def does_tutor_or_patient_exist(self, nome: str, is_tutor: bool= False):
        if is_tutor:
            return self.cursor.execute('SELECT * FROM tutor WHERE nome_tutor = ?', (nome,))
        else:
            return self.cursor.execute('SELECT * FROM patients WHERE nome = ?', (nome,))

    
    def update_patient_name(self, pet_id: int, new_name: str) -> bool:
        """Atualiza o nome de um paciente no banco de dados."""
        try:
            self.cursor.execute("UPDATE patients SET nome = ? WHERE id = ?", (new_name, pet_id))
            self.handler.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar o nome: {e}")
            return False


    def update_patient_vaccines(self, pet_id: int, vaccines_list: list) -> bool:
        """Atualiza as vacinas de um paciente no banco de dados."""
        try:
            vacinas_json = json.dumps([
                {"nome": vacina.strip(), "data": datetime.now().strftime("%d-%m-%Y")}
                for vacina in vaccines_list
            ])
            self.cursor.execute("UPDATE patients SET vacinas_tomadas = ? WHERE id = ?", (vacinas_json, pet_id))
            self.handler.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar vacinas: {e}")
            return False


    def update_patient_gender(self, pet_id: int, new_gender: str) -> bool:
        """Atualiza o gênero de um paciente no banco de dados."""
        try:
            self.cursor.execute("UPDATE patients SET genero = ? WHERE id = ?", (new_gender.lower(), pet_id))
            self.handler.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar o gênero: {e}")
            return False


    def get_report(self, name: str) -> None:
        instance = ReportCreator()
        # catch = ReportCreator.generatePDF(tutor_name=name)
        catch = instance.generatePDF(name)
            
        return catch

        
    def close_db(self): self.handler.close()
