from flask import Flask, render_template, redirect, request, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF
import os
from cryptography.fernet import Fernet
import logging

# Configuração do Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)  # Para proteger formulários e sessões
db = SQLAlchemy(app)

# Gerador de chave de criptografia (salve esta chave em um local seguro)
key = Fernet.generate_key()
cipher = Fernet(key)

# Setup do logging
logging.basicConfig(level=logging.INFO)

# Modelo de Usuários
class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)
    horario_chegada = db.Column(db.String(100), nullable=False)
    cpf_encriptado = db.Column(db.String(200), nullable=False)  # CPF criptografado
    
    # Método para criptografar o CPF
    def set_cpf(self, cpf):
        self.cpf_encriptado = cipher.encrypt(cpf.encode()).decode()

    # Método para descriptografar o CPF
    def get_cpf(self):
        return cipher.decrypt(self.cpf_encriptado.encode()).decode()

# Pagina de escolha
@app.route('/')
def escolha():
    return render_template('escolha.html')

# Página Inicial (Cadastro de Usuários)
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['firstname']
        sobrenome = request.form['lastname']
        cargo = request.form['oqvce']
        horario_chegada = request.form['horario']
        cpf = request.form['CPF']
        
        # Validação simples para garantir que os campos não estejam vazios
        if not nome or not sobrenome or not cpf:
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('cadastro'))

        # Criptografando o CPF antes de armazenar
        novo_usuario = Usuarios(
            nome=nome, 
            sobrenome=sobrenome, 
            cargo=cargo, 
            horario_chegada=horario_chegada
        )
        novo_usuario.set_cpf(cpf)
        
        db.session.add(novo_usuario)
        db.session.commit()

        ultimo_usuario = nome
        logging.info(f"Novo usuário cadastrado: {ultimo_usuario}")
        
        return redirect(url_for('cadastro', ultimousuario=ultimo_usuario))
    
    ultimo_usuario = request.args.get('ultimousuario', None)
    return render_template('index.html', ultimousuario=ultimo_usuario)

# Página de Relatórios
@app.route('/relatorios')
def relatorio():
    usuarios = Usuarios.query.all()
    return render_template('relatorios.html', usuarios=usuarios)

# Geração de PDF
@app.route('/gerar_pdf')
def gerar_pdf():
    usuarios = Usuarios.query.all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Relatório de Usuários", ln=True, align='C')
    
    for usuario in usuarios:
        cpf_descriptografado = usuario.get_cpf()  # Descriptografando o CPF para exibir no PDF
        pdf.cell(200, 10, txt=f"{usuario.nome} {usuario.sobrenome} - {usuario.cargo} - {usuario.horario_chegada} - {cpf_descriptografado}", ln=True)
    
    pdf_file_path = 'relatorio_usuarios.pdf'
    pdf.output(pdf_file_path)
    
    if os.path.exists(pdf_file_path):
        return send_file(pdf_file_path, as_attachment=True)
    else:
        return "Erro: O arquivo PDF não foi gerado corretamente.", 500

# Função principal para rodar o app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria o banco de dados e as tabelas
        
    app.run(debug=True)
