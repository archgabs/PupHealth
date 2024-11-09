from fpdf import FPDF
import os
import sqlite3
import json


class ReportCreator(FPDF):
    def __init__(self) -> None:
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font("Arial", size=12)

    def retrieve_data(self, target):
        handler = sqlite3.connect('database/database.db')
        cursor = handler.cursor()

        cursor.execute('''
            SELECT p.id, p.nome AS paciente_nome, t.nome_tutor AS tutor_nome, p.vacinas_tomadas 
            FROM patients p 
            JOIN tutor t ON p.tutor = t.id 
            WHERE t.nome_tutor = ? 
            ORDER BY p.id
        ''', (target,))

        data = cursor.fetchall()
        handler.close()
        
        return data

    def format_vaccine_data(self, vaccine_data):
        vaccines = json.loads(vaccine_data)
        formatted = [(v['nome'], v['data']) for v in vaccines]
        return formatted

    def generatePDF(self, tutor_name) -> None:
        # Título 
        self.set_font("Arial", "B", 24)
        self.set_text_color(0, 0, 0) 
        self.cell(0, 10, f'Relatório para os Pets da {tutor_name.title()}', ln=True, align='L')
        self.ln(10)

        # Recuperar dados
        data = self.retrieve_data(tutor_name)

        # Verificar se há dados
        if not data:
            return None

        # Configuração para exibição 
        self.set_text_color(0, 0, 0)  
        for row in data:
            pet_name = row[1]
            vaccines = self.format_vaccine_data(row[3])

            # Nome do pet como subtítulo
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, f'Pet: {pet_name.title()}', ln=True, align='L')
            self.ln(5)

            # Cabeçalho da tabela de vacinas
            self.set_font("Arial", "B", 12)
            self.set_fill_color(200, 220, 255)  
            self.cell(60, 10, "Vacina", border=1, align='C', fill=True)
            self.cell(40, 10, "Data", border=1, align='C', fill=True)
            self.ln()

            # Listagem das vacinas com datas
            self.set_font("Arial", size=10)
            for vacina, data in vaccines:
                self.cell(60, 10, vacina, border=1, align='C')
                self.cell(40, 10, data.replace('-', '/'), border=1, align='C')
                self.ln()

            self.ln(10)


        self.output(name=f"{tutor_name}_relatorio_pets.pdf")
        return True

