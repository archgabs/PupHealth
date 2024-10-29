import customtkinter
from functools import partial as p 
from DatabaseManager import login_validation, send_password_change, is_code_valid, change_password


class LoginScreen:
    def __init__(self) -> None:
        self.app = customtkinter.CTk()
        customtkinter.set_appearance_mode('dark')
        customtkinter.set_default_color_theme('green')                  

        self.app.geometry("450x500")
        self.app.title("Login")
        self.app.resizable(False, False)
        self.app.columnconfigure(0, weight=1)
        
        # Title
        self.label = customtkinter.CTkLabel(master=self.app, text="Pup Health", font=("Pacifico", 48),  padx = 20, pady = 20)
        self.label.grid(row = 0, column = 0, sticky="")
        
        # Login Field
        self.login_field = customtkinter.CTkFrame(master=self.app, corner_radius=10, fg_color="#333")
        self.login_field.grid(row = 1, column = 0, padx = 20, pady = (10,20))

        # Login & Password 
        self.login_input = customtkinter.CTkEntry(master=self.login_field, placeholder_text="Username", width=250, height=30)
        self.password_input = customtkinter.CTkEntry(master=self.login_field, placeholder_text="Password", show="*", width=250, height=30)
        
        self.login_input.grid(row = 0, sticky = "", padx=20, pady=20)
        self.password_input.grid(row = 1, sticky = "", padx=20, pady=(0,10))

        self.forgot_password = customtkinter.CTkLabel(master=self.login_field, text="Esqueceu a senha / Primeiro acesso?", font=("arial", 12))
  
        # Efeitos Hover
        self.forgot_password.bind('<Button-1>', lambda event: self.renderCodeVerify())
        self.forgot_password.bind('<Enter>', lambda event: self.change_color(mode='<Enter>'))
        self.forgot_password.bind('<Leave>', lambda event: self.change_color(mode='<Leave>'))
        self.forgot_password.configure(cursor='hand2')
        
        self.forgot_password.grid(row=2, sticky="w", padx=20, pady=(0,20))

        # Login Button
        self.login_button = customtkinter.CTkButton(master=self.app, text="Connect", font=("Arial", 16), width=280,
                                                    command=self.send_validation)
        self.login_button.grid(row=2, column=0, padx=20, pady=20, sticky = '')

        self.app.mainloop()

    
    def change_color(self, mode: str) -> None:
        """Usado exclusivamente para mudar a label de Esqueceu"""
        self.forgot_password.configure(text_color = '#555') if mode == '<Enter>' else self.forgot_password.configure(text_color = 'white')

    
    def send_validation(self) -> None:
        lg = self.login_input.get() 
        ps = self.password_input.get()

        match login_validation(lg, ps):
            case "FOUND":
                self.login_input.configure(border_color = "#A0C1B9") 
                self.password_input.configure(border_color = "#A0C1B9") 
                self.app.destroy()
                self.mainApp = mainApp(username=lg, instance=self)

            case "NOT VALID":
                self.login_input.configure(border_color = "#96031A") 
                self.password_input.configure(border_color = "#96031A") 
                self.forgot_password.configure(text="Usuário/Senha incorreta!")          

            case "FAILED":
                self.forgot_password.configure(text="Servidor Offline!")         
                                   
       
    def renderCodeVerify(self, has_been_sent: bool = False) -> None: 
        """
        has_been_sent atua como uma flag para o direcionamento das mudanças na UI;
        Se não estiver como True (parametro padrão -> False) será criado a janela de recuperação de senha/code verify;
        Caso contrário, será enviado a requisição para o e-mail;
        Funções adjacentes: request_password_change, send_code_validation.
        """
        # Retira a possibilidade de Spam
        self.forgot_password.unbind('<Button-1>')    
        
        if has_been_sent:
            # Responsável pelo envio do e-mail
            catch = send_password_change(username=self.temp_input.get())
            if catch is not False:  
                user = self.temp_input.get()
                
                self.temp_label.configure(text=f'Digite o código enviado para o e-mail do(a): {self.temp_input.get().title()}:')
                self.temp_input.configure(placeholder_text='Código', show='*')
                self.temp_input.delete(0, 'end')        
                # Validação do código:
                self.btn.configure(text='Verificar', command=p(self.send_code_validation, code=catch, user=user))
            else:
                # Volta para pedir usuário
                self.temp_label.configure(text="Usuário não encontrado. Tente novamente.")
                self.temp_input.delete(0, 'end')  
                self.btn.configure(text='Enviar Código')               
        else:
            # Se código não foi enviado, desenha tela de recuperação.
            self.render_topLevel()


    def render_topLevel(self):
            self.temp_toplevel = customtkinter.CTkToplevel()
            self.temp_toplevel.geometry('450')
            self.temp_toplevel.title('Esqueceu a senha?')
            self.temp_toplevel.columnconfigure(0, weight=1)
            self.temp_toplevel.resizable(False, False)
            
            self.temp_label = customtkinter.CTkLabel(master=self.temp_toplevel, text="Qual seu usuário?", font=('Arial', 16))
            self.temp_label.grid(padx=20, pady=10, sticky='', row=0)

            self.temp_input = customtkinter.CTkEntry(master=self.temp_toplevel, placeholder_text="Usuário", width=250, height=30)
            self.temp_input.grid(padx=20, pady=5, sticky='', row=1)
        
            self.btn = customtkinter.CTkButton(master=self.temp_toplevel, text="Enviar Código", font=("Arial", 16), width=280,
                                                command=p(self.renderCodeVerify, True))
            self.btn.grid(padx=20, pady=20, sticky='', row=2)
            
            # Traduz para: Quando fechar a janela, novamente será atribuido as funções via bind.
            self.temp_toplevel.protocol("WM_DELETE_WINDOW",
                                        lambda: (self.forgot_password.bind('<Button-1>',
                                        lambda event: self.renderCodeVerify(has_been_sent=False)),
                                            self.temp_toplevel.destroy()))


    def send_code_validation(self, code, user) -> None:
        catch = is_code_valid(code=code, input_code=self.temp_input.get())
     
        if catch:
            self.temp_label.configure(text=f'Digite abaixo a nova senha com ao menos 8 caracteres, e ao menos um número:')
            self.temp_input.configure(placeholder_text='Nova Senha', show='*')
            self.temp_input.delete(0, 'end')        
            self.btn.configure(text="Alterar Senha",
                               command=p(self.request_password_change, self.temp_input, user))
        else:
            self.temp_label.configure(text='Código inválido, tente novamente:')
            
             
    def request_password_change(self, input, user) -> None:
        catch = change_password(input, user)
        if catch:
            self.temp_toplevel.destroy()
            self.forgot_password.bind('<Button-1>', lambda event: self.renderCodeVerify(has_been_sent=False))
            self.forgot_password.configure(text_color = 'green', text="Senha alterada com sucesso!") 
        
        else:
            self.temp_label.configure(text='Senha inválida, tente novamente:')
            
            
class mainApp(customtkinter.CTk):
    def __init__(self, username: str, instance):
        super().__init__()
        print("Main App is building......")
        
        self.title("Dashboard")
        self.geometry('1280x768')
        self.resizable(False, False)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.nav = self.navBar(username=username, instance=instance)
        self.side = self.sideBar()
        
        
        self.mainloop()
        
        
    def navBar(self, username, instance) -> None:
        self.top_frame = customtkinter.CTkFrame(self, height=100)
        self.top_frame.grid(row=0, column=0, padx=20, pady=20, sticky='new', columnspan=2)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)
        
        self.top_frame_user_label = customtkinter.CTkLabel(master=self.top_frame,
                                                           height=40,
                                                           anchor='center',
                                                           text=f"Bem-vindo de volta, {username.title()}.",
                                                           font=('Arial', 16, 'bold'),)
        
        self.top_frame_user_label.grid(column=0, row=0, padx=20, pady=20, sticky='nw')
        
        self.top_frame_btn_exit = customtkinter.CTkButton(master=self.top_frame, anchor='center',
                                                          text="Sair (Login)",
                                                          fg_color="#333",
                                                          height=40,
                                                          command=p(self.exitApp, instance))

        self.top_frame_btn_exit.grid(column=1, row=0, padx=20, pady=20, sticky='ne')
        print("SUCESS_BUILDING_NAVBAR")

         
    
    def sideBar(self) -> None:
        self.side_frame = customtkinter.CTkFrame(self, width=300)
        self.side_frame.grid(row=1, column=0, padx=20, pady=(10,20), sticky='nws', rowspan=5)
        self.side_frame.grid_columnconfigure(0, weight=1)
        self.side_frame.grid_propagate(False)
        

        self.buttons = {}
        for i, btn_name in enumerate(["Cadastrar Paciente", "Visualizar Pacientes", "Gerar Relatório"]):
            temp_btn = customtkinter.CTkButton(master=self.side_frame,
                                                            text=f"{btn_name}",
                                                            fg_color="#333",
                                                            height=50)
            temp_btn.grid(column=0, row=i, padx=20, pady=20, sticky='nwe')
            self.buttons[btn_name] = temp_btn
        
        
        self.buttons["Cadastrar Paciente"].configure(
            command=self.display_register_patient
        )
        self.buttons["Visualizar Pacientes"].configure(
            command=self.visualize_patients
        )
        self.buttons["Gerar Relatório"].configure(
            command=self.generate_patient_report
        )
        print("SUCESS_BUILDING_SIDEBAR")
    

    def display_register_patient(self):
        print("Hello, world!")
        
        
    def visualize_patients(self):
        print("Hello, world!")

        
    def generate_patient_report(self):
        print("Hello, world!")
    
    
    def exitApp(self, instance) -> None:
        self.destroy()
        instance.__init__()