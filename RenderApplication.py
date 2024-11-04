from DatabaseManager import LoginManager, DashboardUtilities
from functools import partial as p 
import customtkinter
import json


title_font = 'Pacifico'
class LoginScreen(LoginManager):
    def __init__(self) -> None:
        super().__init__()
        self.app = customtkinter.CTk()
        
        customtkinter.set_appearance_mode('dark')
        customtkinter.set_default_color_theme('green')     

        self.app.geometry("450x450")
        self.app.title("Login")
        self.app.resizable(False, False)
        self.app.columnconfigure(0, weight=1)

        # Temporary Bypass
        # self.mainApp = mainApp(username='Bypass Login', instance=self)
        
        # Title
        self.label = customtkinter.CTkLabel(master=self.app, text="Pup Health", font=(title_font, 50),  padx = 20, pady = 20)
        self.label.grid(row = 0, column = 0, sticky="")
        
        # Login Field
        self.login_field = customtkinter.CTkFrame(master=self.app, corner_radius=10, fg_color="#333")
        self.login_field.grid(row = 1, column = 0, padx = 20, pady = (0,0))

        # Login & Password 
        self.login_input = customtkinter.CTkEntry(master=self.login_field, placeholder_text="Username", width=250, height=40,)
        self.password_input = customtkinter.CTkEntry(master=self.login_field, placeholder_text="Password", show="*", width=250, height=40,)
        
        self.login_input.grid(row = 0, sticky = "", padx=20, pady=20)
        self.password_input.grid(row = 1, sticky = "", padx=20, pady=(0,10))

        self.forgot_password = customtkinter.CTkLabel(master=self.login_field, text="Esqueceu a senha / Primeiro acesso?", font=("Open Sans Regular", 12))
  
        # Efeitos Hover
        self.forgot_password.bind('<Button-1>', lambda event: self.renderCodeVerify())
        self.forgot_password.bind('<Enter>', lambda event: self.change_color(mode='<Enter>'))
        self.forgot_password.bind('<Leave>', lambda event: self.change_color(mode='<Leave>'))
        self.forgot_password.configure(cursor='hand2')
        
        self.forgot_password.grid(row=2, sticky="w", padx=20, pady=(0,20))

        # Login Button
        self.login_button = customtkinter.CTkButton(master=self.app, text="Connect", font=("Open Sans Regular", 16, 'bold'), width=280, height=40, command=self.send_validation)
        self.login_button.grid(row=2, column=0, padx=20, pady=20, sticky = '')

        self.app.mainloop()

    
    def change_color(self, mode: str) -> None:
        """Usado exclusivamente para mudar a label de Esqueceu"""
        self.forgot_password.configure(text_color = '#555') if mode == '<Enter>' else self.forgot_password.configure(text_color = 'white')

    
    def send_validation(self) -> None:
        lg = self.login_input.get() 
        ps = self.password_input.get()

        match self.login_validation(lg, ps):
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
            catch = self.send_password_change(username=self.temp_input.get())
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
            
            self.temp_label = customtkinter.CTkLabel(master=self.temp_toplevel, text="Qual seu usuário?",)
            self.temp_label.grid(padx=20, pady=10, sticky='', row=0)

            self.temp_input = customtkinter.CTkEntry(master=self.temp_toplevel, placeholder_text="Usuário", width=250, height=30)
            self.temp_input.grid(padx=20, pady=5, sticky='', row=1)
        
            self.btn = customtkinter.CTkButton(master=self.temp_toplevel, text="Enviar Código", width=280,
                                                command=p(self.renderCodeVerify, True))
            self.btn.grid(padx=20, pady=20, sticky='', row=2)
            
            # Traduz para: Quando fechar a janela, novamente será atribuido as funções via bind.
            self.temp_toplevel.protocol("WM_DELETE_WINDOW",
                                        lambda: (self.forgot_password.bind('<Button-1>',
                                        lambda event: self.renderCodeVerify(has_been_sent=False)),
                                            self.temp_toplevel.destroy()))


    def send_code_validation(self, code, user) -> None:
        catch = self.is_code_valid(code=code, input_code=self.temp_input.get())
     
        if catch:
            self.temp_label.configure(text=f'Digite abaixo a nova senha com ao menos 8 caracteres, e ao menos um número:')
            self.temp_input.configure(placeholder_text='Nova Senha', show='*')
            self.temp_input.delete(0, 'end')        
            self.btn.configure(text="Alterar Senha",
                               command=p(self.request_password_change, self.temp_input, user))
        else:
            self.temp_label.configure(text='Código inválido, tente novamente:')
            
             
    def request_password_change(self, input, user) -> None:
        catch = self.change_password(input, user)
        if catch:
            self.temp_toplevel.destroy()
            self.forgot_password.bind('<Button-1>', lambda event: self.renderCodeVerify(has_been_sent=False))
            self.forgot_password.configure(text_color = 'green', text="Senha alterada com sucesso!") 
        
        else:
            self.temp_label.configure(text='Senha inválida, tente novamente:')
            
            
class mainApp(customtkinter.CTk):
    def __init__(self, username: str, instance) -> None:
        super().__init__()
        print("Main App is building......")

        self.dashboardManager = DashboardUtilities()
        
        self.title("Dashboard")
        self.geometry('1280x768')
        self.resizable(False, False)
        
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        self.is_panel_open = False
        self.is_already_filter = False
        self.temp_top_level = False

        self.nav = self.navBar(username=username, instance=instance)
        self.side = self.sideBar()

        self.mainloop()
        
        
    def navBar(self, username: str, instance) -> None:
        self.top_frame = customtkinter.CTkFrame(self, height=100)
        self.top_frame.grid(row=0, column=0, padx=20, pady=(20,10), sticky='new', columnspan=2)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)
        
        self.top_frame_user_label = customtkinter.CTkLabel(master=self.top_frame,
                                                           height=40,
                                                           anchor='center',
                                                           text=f"Bem-vindo de volta, {self.dashboardManager.get_user(usr=username)[0]}.",
                                                           font=('Arial', 20, 'bold'),)
        
        self.top_frame_user_label.grid(column=0, row=0, padx=20, pady=20, sticky='nw')
        
        self.top_frame_btn_exit = customtkinter.CTkButton(master=self.top_frame, anchor='center',
                                                          text="Sair (Login)",
                                                          fg_color="#333",
                                                          height=40,
                                                          command=p(self.exitApp, instance))

        self.top_frame_btn_exit.grid(column=1, row=0, padx=20, pady=20, sticky='ne')
        print("SUCESS_BUILDING_NAVBAR")

    
    def sideBar(self) -> None:
        self.button_names = ["Cadastrar Paciente", "Visualizar Pacientes", "Gerar Relatório"]
        self.side_frame = customtkinter.CTkFrame(self, width=300)
        self.side_frame.grid(row=1, column=0, padx=20, pady=(10,20), sticky='nws',)
        self.side_frame.grid_columnconfigure(0, weight=1)
        self.side_frame.grid_propagate(False)
        

        self.buttons = {}
        for i, btn_name in enumerate(self.button_names):
            temp_btn = customtkinter.CTkButton(master=self.side_frame,
                                                            text=f"{btn_name}",
                                                            fg_color="#333",
                                                            height=50)
            temp_btn.grid(column=0, row=i, padx=20, pady=(10,5), sticky='nwe')
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
    
           
    def createPanel(self, params: dict) -> None:
        self.panel = customtkinter.CTkScrollableFrame(master=self, label_text=params['title'], width=880)
        self.panel.grid(row=1, column=1, padx=20, pady=(10,20), sticky='nsew')
        self.panel.grid_columnconfigure(0, weight=1)
        
        self.buttons[params['btn']].configure(
            border_color='#719683', 
            border_width = 2,
        )
        
        self.generatePanelItems(params["title"])        
        print("SUCESS_BUILDING_PANEL")
        

    def generatePanelItems(self, mode: str) -> None:
        match mode:
            case "Cadastro de Pacientes":
                # -- Infelizmente a biblioteca consta com um bug que não destrói os paineis propriamente.
                self.panel.grid(row=1, column=1, padx=20, pady=(10,20), sticky='nws')
                self.grid_columnconfigure(1, weight=2)
                
                self.register_patients_elements = {}
                for i, item in enumerate(["Nome do Pet", "Genero", "Raca", "Tutor","Vacinas Tomadas", "Registrar"]):
                    if item == "Genero":
                        entry = customtkinter.CTkOptionMenu(self.panel,
                                                            values=["Macho", "Fêmea"],
                                                            width=300, 
                                                            height=50)
                    elif item == "Registrar":
                         entry = customtkinter.CTkButton(master=self.panel,
                                                        text=item,
                                                        width=300, 
                                                        height=50,
                                                        command=self.register_input_handler)                      
                    else:     
                        item = item if item != "Raca" else item.replace('c', 'ç')                             
                        entry = customtkinter.CTkEntry(master=self.panel,
                                                        placeholder_text=item,
                                                        width=300,
                                                        height=50)
                        
                    entry.grid(padx=20, pady=5, sticky='nwe', row=i)
                    if not item == "Registrar":
                        self.register_patients_elements[item.lower()
                                                        .replace(' ', '')
                                                        .replace('ç','c')] = entry
                self.register_patients_elements['vacinastomadas'].configure(placeholder_text='Exemplo: Antirrábica, Vermifungado 1, A, B')
                print("SUCESS_ADDING_ITENS")
                    
            case "Visualizar Pacientes": 
                # retorna os itens e renderiza
                self.generate_itens_by_mode()
            
            case "Gerar Relatório": pass        
            
    def generate_filter_buttons(self):
        self.filter_btns: dict = {}
        self.filter_btns_names = ["ID", "Tutor", "Nome Paciente"]
        self.panel.grid_rowconfigure(0, weight=1)

        
        for i, btn_name in enumerate(self.filter_btns_names):
            temp_btn = customtkinter.CTkButton(master=self.panel,
                                                text=f"{btn_name}",
                                                fg_color="#333",
                                                height=40)
            if i == 0:
                diff_sticky = 'nw'
            elif i== 2:
                diff_sticky = 'ne'
            else:
                diff_sticky = ''
                
            temp_btn.grid(column=i, row=0, pady=(10,5), padx=20, sticky=diff_sticky)
            self.panel.grid_columnconfigure(i, weight=1)
            self.filter_btns[btn_name] = temp_btn
            
        self.filter_btns["ID"].configure(
            command=p(self.generate_itens_by_mode, mode="INIT")
        )
        self.filter_btns["Tutor"].configure(
            command=p(self.generate_itens_by_mode, mode="Tutor")
        )
        self.filter_btns["Nome Paciente"].configure(
            command=p(self.generate_itens_by_mode, mode="Nome Paciente")
        )    

    def generate_itens_by_mode(self, mode: str = "INIT") -> None:            
        if self.is_already_filter:
            for frame in self.panel_itens_frames:
                if frame.winfo_exists():
                    frame.grid_forget()
        
        match mode:
            case "INIT":
                catch = self.dashboardManager.list_patients(mode=mode)
            case "Tutor":
                usr_input = customtkinter.CTkInputDialog(title="Qual o tutor?", text="Digite abaixo o tutor para filtrar.\nEX: Lestat").get_input().lower()
                # if usr_input.isalpha() and usr_input not in [None, "", " "]:
                if self.dashboardManager.does_tutor_or_patient_exist(usr_input):
                    catch = self.dashboardManager.list_patients(mode=mode, tutor=usr_input)
                else:
                    self.alert(title="Tutor não encontrado.", msg="Certifique-se que digitou corretamente.") 
            case "Nome Paciente":
                usr_input = customtkinter.CTkInputDialog(title="Qual o nome do animal?", text="Digite abaixo o animal para filtrar.\nEX: Lagostinha").get_input().lower()
                # if usr_input.isalpha() and usr_input not in [None, "", " "].
                if self.dashboardManager.does_tutor_or_patient_exist(usr_input):
                    catch = self.dashboardManager.list_patients(mode=mode, tutor=usr_input)
                else:
                    self.alert(title="Usuário não encontrado.", msg="Certifique-se que digitou corretamente.")
                               
        self.generate_filter_buttons()              
        if catch is not None: 
            self.is_already_filter = True
            self.panel_itens_frames = []
            for i, item in enumerate(catch):
                # Lado Esquerdo
                temp_frame = customtkinter.CTkFrame(master=self.panel, width=600, fg_color='#333', height=150)
                temp_frame.grid_columnconfigure(0, weight=1)
                temp_frame.grid_columnconfigure(1, weight=1)
                
                temp_frame.grid(row=i+1, column=0, padx=20, pady=(10,20), sticky='nwe', columnspan=3)
                temp_frame.propagate(False)
                
                name = customtkinter.CTkLabel(text=item[1].title(), master=temp_frame, text_color='#d9d9d9', font=('Arial', 28, 'bold'))
                name.grid(row=i, padx=20, pady=(10,0), sticky='nw')
                
                tutor = customtkinter.CTkLabel(text=item[2].title(), master=temp_frame, text_color='#a6a6a6', font=('Arial', 18, 'bold'))
                tutor.grid(row=i+1, padx=20, pady=(0,0), sticky='nw')

                vacinas_data = json.loads(item[3])
                vacinas_texto = "\t".join([f"{v['nome']}" for v in vacinas_data])

                vacinas = customtkinter.CTkLabel(text=vacinas_texto, master=temp_frame, text_color='#737373', font=('Arial', 14, 'italic'))
                vacinas.grid(row=i+2, padx=20, pady=(0, 10), sticky='nw')
                
                # Lado direito
                id_pet = customtkinter.CTkLabel(text=f'ID: {item[0]}', master=temp_frame, text_color='#d9d9d9', font=('Arial', 18, 'bold'))
                id_pet.grid(row=i+2, column = 1, padx=20, pady=(0,10), sticky='se')

                edit_button = customtkinter.CTkButton(master=temp_frame,
                                                        text="Editar",
                                                        font=("Arial", 14, 'bold'),
                                                        width=100, height=40,
                                                        corner_radius=10, fg_color='#282828',
                                                        command=p(self.edit_patient, item[0]))
                
                edit_button.grid(row=i, column=1, padx=20, pady=(10,0), sticky='ne')

                self.panel.grid_rowconfigure(i+1, weight=1)
                self.panel_itens_frames.append(temp_frame)
                print(item)    
        
        
    def edit_patient(self, pet_id: int) -> None:
        if self.temp_top_level and self.temp_top_level.winfo_exists():
            self.temp_top_level.destroy()

        self.temp_top_level = customtkinter.CTkToplevel()
    
        self.temp_top_level.title("Edição de Paciente")
        self.temp_top_level.resizable(False, False)
        self.temp_top_level.grid_columnconfigure(0, weight=1)
        
        for i, item in enumerate(["Alterar Nome", "Modificar Vacinas", "Alterar Gênero"]):
            self.temp_top_level.grid_rowconfigure(i, weight=1)
            btn = customtkinter.CTkButton(text=item, master=self.temp_top_level, width=250, height=30)        
            btn.grid(row=i, padx=20, pady=20, sticky='ew')
            btn.configure(command=p(self.alter_btns, pet_id, item))
            
            
    def alter_btns(self, pet_id, item) -> None:
        match item:
            case "Alterar Nome":
                new_name = customtkinter.CTkInputDialog(title="Alterar Nome", text="Digite o novo nome do paciente:").get_input()
                if new_name:
                    success = self.dashboardManager.update_patient_name(pet_id, new_name)
                    if success:
                        self.alert(title="Sucesso", msg="Nome atualizado com sucesso!")
                    else:
                        self.alert(title="Erro", msg="Falha ao atualizar o nome.")
                else:
                    self.alert(title="Entrada Inválida", msg="Nome não pode estar vazio.")

            case "Modificar Vacinas":
                current_vaccines = json.loads(self.dashboardManager.cursor.execute("SELECT vacinas_tomadas FROM patients WHERE id = ?", (pet_id,)).fetchone()[0])
                current_vaccines_text = ', '.join([vacina["nome"] for vacina in current_vaccines])

                updated_vaccines = customtkinter.CTkInputDialog(
                    title="Modificar Vacinas",
                    text=f"Vacinas atuais: {current_vaccines_text}\n\nDigite novas vacinas (separadas por vírgula):"
                ).get_input()
                if updated_vaccines:
                    vaccine_list = [vac.strip() for vac in updated_vaccines.split(',') if vac.strip()]
                    if vaccine_list:
                        success = self.dashboardManager.update_patient_vaccines(pet_id, vaccine_list)
                        if success:
                            self.alert(title="Sucesso", msg="Vacinas atualizadas com sucesso!")
                        else:
                            self.alert(title="Erro", msg="Falha ao atualizar as vacinas.")
                    else:
                        self.alert(title="Entrada Inválida", msg="Vacinas não podem estar vazias.")
                else:
                    self.alert(title="Entrada Inválida", msg="Vacinas não podem estar vazias.")

            case "Alterar Gênero":
                # Janela para seleção do novo gênero usando grid
                gender_window = customtkinter.CTkToplevel(self.temp_top_level)
                gender_window.title("Alterar Gênero")
                gender_window.geometry("300x200")
                gender_window.resizable(False,False)
                gender_window.grid_columnconfigure(0, weight=1)

                label = customtkinter.CTkLabel(gender_window, text="Selecione o novo gênero:")
                label.grid(row=0, column=0, padx=20, pady=10)

                new_gender_menu = customtkinter.CTkOptionMenu(
                    master=gender_window, values=["Macho", "Fêmea"]
                )
                new_gender_menu.grid(row=1, column=0, padx=20, pady=10)

                error_label = customtkinter.CTkLabel(gender_window, text="", text_color="red")
                error_label.grid(row=2, column=0)

                # Função para salvar a seleção
                def save_gender():
                    new_gender = new_gender_menu.get()
                    if new_gender in ["Macho", "Fêmea"]:
                        success = self.dashboardManager.update_patient_gender(pet_id, new_gender)
                        if success:
                            self.alert(title="Sucesso", msg="Gênero atualizado com sucesso!")
                        else:
                            self.alert(title="Erro", msg="Falha ao atualizar o gênero.")
                        gender_window.destroy()
                    else:
                        error_label.configure(text="Por favor, selecione um gênero válido.")

                save_button = customtkinter.CTkButton(gender_window, text="Salvar", command=save_gender)
                save_button.grid(row=3, column=0, padx=20, pady=10)

        # Atualizar visualização após qualquer edição
        self.generate_itens_by_mode(mode="INIT")

                
    def register_tutor(self) -> None:
        catch = customtkinter.CTkInputDialog(
            title="Tutor Não Encontrado",
            text=f"Tutor {self.register_patients_elements['tutor'].get().title()} não registrado, deseja incluir um novo tutor? (Sim)",)
        if catch.get_input().lower() in ['s', 'sim', 'y', 'yes']:
            self.register_input_handler(new_tutor=self.register_patients_elements['tutor'].get().title())
       
       
    def register_input_handler(self, new_tutor = False):
        if not new_tutor:                   
            catch = self.dashboardManager.validate_inputs(self.register_patients_elements, new_tutor=False)
        else:
            catch = self.dashboardManager.validate_inputs(self.register_patients_elements, new_tutor)           
            
        print(catch)
        match catch:
            case "ANIMAL_INSERTED_DB":
                for item in self.register_patients_elements:
                    if item != 'genero':
                        self.register_patients_elements[item].configure(
                            border_color = '#A0C1B9',
                            border_width = 2,
                        )
                        self.register_patients_elements[item].delete(0, 'end')       
                self.alert(title="Sucesso", msg="Incluido com sucesso!")
                print(">")
                   
            case "ANIMAL_ALREADY_ASSIGNED":
                for item in self.register_patients_elements:
                    if item != 'genero':
                        self.register_patients_elements[item].configure(
                            border_color = '#A0C1B9',
                            border_width = 2,
                        )
                self.register_patients_elements['nomedopet'].configure(
                    border_color = '#9e3333',
                    border_width = 2,
                )
                self.register_patients_elements['nomedopet'].focus()
                self.alert(title="Animal já cadastrado", msg="Animal já foi cadastrado neste ID, atualize-o.")
                
            case "ID_MISSING":
                for item in self.register_patients_elements:
                    if item != 'genero':
                        self.register_patients_elements[item].configure(
                            border_color = '#A0C1B9',
                            border_width = 2,
                        )
                self.register_patients_elements['tutor'].configure(
                    border_color = '#9e3333',
                    border_width = 2,
                )
                self.register_patients_elements['tutor'].focus()
                self.register_tutor()
            
       
    def changePanel(self, params: dict) -> None:
        if not self.is_panel_open:
            self.createPanel(params)
            self.is_panel_open = True
        else:
            catch = customtkinter.CTkInputDialog(
                title="Troca de Abas",
                text="Você tem uma aba aberta, por segurança digite: SIM para fechar."
                )
            if catch.get_input().lower() in ["yes", "sim", "s", 'y']:
                self.panel.destroy()
                for btn_name in self.button_names:
                    self.buttons[btn_name].configure(border_width=0)

                print("SUCESS_CHANGING_PANEL")
                self.panel.grid_forget()
                self.createPanel(params)


    def alert(self, title, msg):
        toplevel = customtkinter.CTkToplevel()
        toplevel.geometry('300')
        toplevel.title(title)
        toplevel.resizable(False, False)
        toplevel.columnconfigure(0, weight=1)
        
        temp_label = customtkinter.CTkLabel(master=toplevel, text=msg, font=('Open Sans Regular', 16))
        temp_label.grid(padx=20, pady=10, sticky='', row=0)
    
        btn = customtkinter.CTkButton(master=toplevel, text="Fechar", font=("Open Sans Regular", 16), command=toplevel.destroy)
        btn.grid(padx=20, pady=20, sticky='', row=1)

   
    def display_register_patient(self) -> None:
        self.changePanel(params={
            "title": "Cadastro de Pacientes",
            "btn": "Cadastrar Paciente",
        })        
        
        
    def visualize_patients(self) -> None:
        self.changePanel(params={
            "title": "Visualizar Pacientes",
            "btn": "Visualizar Pacientes",
        })          
        
        
    def generate_patient_report(self) -> None:
         self.changePanel(params={
            "title": "Gerar Relatório",
            "btn": "Gerar Relatório",
        })        
   
    
    def exitApp(self, instance) -> None:
        self.dashboardManager.close_db()
        self.destroy()
        instance.__init__()