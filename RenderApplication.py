import customtkinter
from functools import partial as p 
from DatabaseManager import login_validation, request_password_change


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
        self.forgot_password.bind('<Button-1>', self.send_forget_password_request)
        self.forgot_password.grid(row=2, sticky="w", padx=20, pady=(0,20))

        # Login Button
        self.login_button = customtkinter.CTkButton(master=self.app, text="Connect", font=("Arial", 16), width=280,
                                                    command=p(self.send_validation),)
        self.login_button.grid(row=2, column=0, padx=20, pady=20, sticky = '')
        
        self.app.mainloop()

    
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
                
            
            
    def send_forget_password_request(self, username: str = False) -> None:
        lg = self.login_input.get()
        print(lg)
        # catch_ans = request_password_change(lg)
        # print(catch_ans)    
            
            
    def renderMainMenu(self) -> None: pass
    