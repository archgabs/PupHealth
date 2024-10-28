import customtkinter
from functools import partial as p 
from DatabaseManager import login_validation, request_password_change, is_code_valid 


class RenderApplication:
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
        self.login_field.grid(row = 1, column = 0, padx = 20, pady = 20)

        # Login & Password 
        self.login_input = customtkinter.CTkEntry(master=self.login_field, placeholder_text="Username", width=250, height=30)
        self.password_input = customtkinter.CTkEntry(master=self.login_field, placeholder_text="Password", show="*", width=250, height=30)
        
        self.login_input.grid(row = 0, sticky = "", padx=20, pady=20)
        self.password_input.grid(row = 1, sticky = "", padx=20, pady=(0,10))

        self.forgot_password = customtkinter.CTkLabel(master=self.login_field, text="Esqueceu a senha / Primeiro acesso?", font=("arial", 12))
  
        # Efeitos Hover
        self.forgot_password.bind('<Button-1>', lambda event: self.send_forget_password_request())
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

            case "NOT VALID":
                self.login_input.configure(border_color = "#96031A") 
                self.password_input.configure(border_color = "#96031A") 
                self.forgot_password.configure(text="Usuário/Senha incorreta!")          

            case "FAILED":
                self.forgot_password.configure(text="Servidor Offline!")         
                
            
            
    def send_forget_password_request(self) -> None:
        print("SEND_FORGET_PASSWORD_REQUEST")
        # ans = request_password_change(lg)
        self.renderCodeVerify(has_been_sent=False)
                    
       
    def renderCodeVerify(self, has_been_sent: bool = False) -> None: 
        self.forgot_password.unbind('<Button-1>')    
        if has_been_sent:
            catch = request_password_change(username=self.temp_input.get())
            if catch is not False:  # Verifica se o retorno não é False (Usuário válido)
                self.temp_label.configure(text=f'Digite o código enviado para o e-mail do(a): {self.temp_input.get().title()}:')
                self.temp_input.configure(placeholder_text='Código', show='*')
                self.temp_input.delete(0, 'end')        
                self.btn.configure(text='Verificar', command=p(self.send_code_validation, code=catch))
            else:
                # Volta para pedir usuário
                self.temp_label.configure(text="Usuário não encontrado. Tente novamente.")
                self.temp_input.delete(0, 'end')  # Limpa o campo de entrada
                self.btn.configure(text='Enviar Código')               
        else:
            self.temp_toplevel = customtkinter.CTkToplevel()
            self.temp_toplevel.geometry('450x150')
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
            
            self.temp_toplevel.protocol("WM_DELETE_WINDOW",
                                        lambda: (self.forgot_password.bind('<Button-1>',
                                        lambda event: self.send_forget_password_request()),
                                            self.temp_toplevel.destroy()))

    def send_code_validation(self, code) -> bool:
        is_code_valid(code=code, input_code=self.temp_input.get())
