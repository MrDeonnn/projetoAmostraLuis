from flask import Flask, render_template, redirect, request, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)
    horario_chegada = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(20), nullable=False)
    
@app.route('/')
def home():
    return render_template('escolha.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['firstname']
        sobrenome = request.form['lastname']
        cargo = request.form['oqvce']
        horario_chegada = request.form['horario']
        cpf = request.form['CPF']
        
        novo_usuario = Usuarios(nome=nome, sobrenome=sobrenome, cargo=cargo, horario_chegada=horario_chegada, cpf=cpf)
        db.session.add(novo_usuario)
        db.session.commit()

        ultimo_usuario = nome
        print(ultimo_usuario)
        return redirect(url_for('cadastro', ultimousuario=ultimo_usuario))
            
    ultimo_usuario = request.args.get('ultimousuario', None)
    return render_template('index.html', ultimousuario=ultimo_usuario)

@app.route('/relatorios')
def relatorio():
    usuarios = Usuarios.query.all()
    return render_template('relatorios.html', usuarios=usuarios)

@app.route('/gerar_pdf')
def gerar_pdf():
    usuarios = Usuarios.query.all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Relatório de Usuários", ln=True, align='C')
    
    for usuario in usuarios:
        pdf.cell(200, 10, txt=f"{usuario.nome} {usuario.sobrenome} - {usuario.cargo} - {usuario.horario_chegada}", ln=True)
    
    pdf_file_path = 'relatorio_usuarios.pdf'
    pdf.output(pdf_file_path)
    
    if os.path.exists(pdf_file_path):
        return send_file(pdf_file_path, as_attachment=True)
    else:
        return "Erro: O arquivo PDF não foi gerado corretamente.", 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)