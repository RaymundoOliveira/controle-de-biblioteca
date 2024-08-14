import sqlite3
import tkinter as tk
from tkinter import messagebox


class BibliotecaDB:
    def __init__(self, db_name="biblioteca.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano INTEGER NOT NULL,
            copias INTEGER NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            id_usuario TEXT NOT NULL UNIQUE,
            contato TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_livro INTEGER NOT NULL,
            id_usuario TEXT NOT NULL,
            FOREIGN KEY(id_livro) REFERENCES livros(id),
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
        )
        ''')

        self.conn.commit()

    def adicionar_livro(self, titulo, autor, ano, copias):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO livros (titulo, autor, ano, copias) VALUES (?, ?, ?, ?)", (titulo, autor, ano, copias))
        self.conn.commit()

    def adicionar_usuario(self, nome, id_usuario, contato):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, id_usuario, contato) VALUES (?, ?, ?)", (nome, id_usuario, contato))
        self.conn.commit()

    def buscar_livro_por_titulo(self, titulo):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM livros WHERE titulo = ?", (titulo,))
        return cursor.fetchone()

    def buscar_livro_por_autor(self, autor):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM livros WHERE autor = ?", (autor,))
        return cursor.fetchall()

    def buscar_livro_por_ano(self, ano):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM livros WHERE ano = ?", (ano,))
        return cursor.fetchall()

    def buscar_usuario_por_id(self, id_usuario):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (id_usuario,))
        return cursor.fetchone()

    def emprestar_livro(self, titulo, id_usuario):
        livro = self.buscar_livro_por_titulo(titulo)
        usuario = self.buscar_usuario_por_id(id_usuario)
        if not livro:
            return "Livro não encontrado."
        if not usuario:
            return "Usuário não encontrado."
        if livro[4] == 0:
            return "Livro indisponível para empréstimo."

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO emprestimos (id_livro, id_usuario) VALUES (?, ?)", (livro[0], id_usuario))
        cursor.execute("UPDATE livros SET copias = copias - 1 WHERE id = ?", (livro[0],))
        self.conn.commit()
        return f"Livro '{titulo}' emprestado para o usuário '{usuario[1]}'."

    def devolver_livro(self, titulo, id_usuario):
        livro = self.buscar_livro_por_titulo(titulo)
        if not livro:
            return "Livro não encontrado."

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM emprestimos WHERE id_livro = ? AND id_usuario = ?", (livro[0], id_usuario))
        emprestimo = cursor.fetchone()
        if not emprestimo:
            return "Empréstimo não encontrado."

        cursor.execute("DELETE FROM emprestimos WHERE id = ?", (emprestimo[0],))
        cursor.execute("UPDATE livros SET copias = copias + 1 WHERE id = ?", (livro[0],))
        self.conn.commit()
        return f"Livro '{titulo}' devolvido com sucesso."

    def listar_livros(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM livros WHERE copias > 0")
        return cursor.fetchall()

    def listar_usuarios(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios")
        return cursor.fetchall()

    def listar_emprestimos(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT l.titulo, u.nome 
                          FROM emprestimos e
                          JOIN livros l ON e.id_livro = l.id
                          JOIN usuarios u ON e.id_usuario = u.id_usuario''')
        return cursor.fetchall()


class BibliotecaApp:
    def __init__(self, root):
        self.biblioteca_db = BibliotecaDB()
        self.root = root
        self.root.title("Sistema de Gerenciamento de Biblioteca")

        # Configuração da interface gráfica
        self.configurar_janela()

    def configurar_janela(self):
        # Título
        tk.Label(self.root, text="Sistema de Gerenciamento de Biblioteca", font=("Arial", 16)).pack(pady=10)

        # Botões
        tk.Button(self.root, text="Cadastrar Livro", command=self.cadastrar_livro).pack(fill="x", pady=5)
        tk.Button(self.root, text="Cadastrar Usuário", command=self.cadastrar_usuario).pack(fill="x", pady=5)
        tk.Button(self.root, text="Empréstimo de Livro", command=self.emprestar_livro).pack(fill="x", pady=5)
        tk.Button(self.root, text="Devolução de Livro", command=self.devolver_livro).pack(fill="x", pady=5)
        tk.Button(self.root, text="Consultar Livros", command=self.consultar_livros).pack(fill="x", pady=5)
        tk.Button(self.root, text="Relatórios", command=self.gerar_relatorios).pack(fill="x", pady=5)
        tk.Button(self.root, text="Sair", command=self.root.quit).pack(fill="x", pady=20)

    def cadastrar_livro(self):
        self.janela_livro = tk.Toplevel(self.root)
        self.janela_livro.title("Cadastrar Livro")

        tk.Label(self.janela_livro, text="Título:").grid(row=0, column=0)
        tk.Label(self.janela_livro, text="Autor:").grid(row=1, column=0)
        tk.Label(self.janela_livro, text="Ano de Publicação:").grid(row=2, column=0)
        tk.Label(self.janela_livro, text="Número de Cópias:").grid(row=3, column=0)

        self.titulo_livro = tk.Entry(self.janela_livro)
        self.autor_livro = tk.Entry(self.janela_livro)
        self.ano_livro = tk.Entry(self.janela_livro)
        self.copias_livro = tk.Entry(self.janela_livro)

        self.titulo_livro.grid(row=0, column=1)
        self.autor_livro.grid(row=1, column=1)
        self.ano_livro.grid(row=2, column=1)
        self.copias_livro.grid(row=3, column=1)

        tk.Button(self.janela_livro, text="Cadastrar", command=self.salvar_livro).grid(row=4, column=0, columnspan=2)

    def salvar_livro(self):
        titulo = self.titulo_livro.get()
        autor = self.autor_livro.get()
        ano = self.ano_livro.get()
        copias = int(self.copias_livro.get())
        self.biblioteca_db.adicionar_livro(titulo, autor, ano, copias)
        self.janela_livro.destroy()

    def cadastrar_usuario(self):
        self.janela_usuario = tk.Toplevel(self.root)
        self.janela_usuario.title("Cadastrar Usuário")

        tk.Label(self.janela_usuario, text="Nome:").grid(row=0, column=0)
        tk.Label(self.janela_usuario, text="ID do Usuário:").grid(row=1, column=0)
        tk.Label(self.janela_usuario, text="Contato:").grid(row=2, column=0)

        self.nome_usuario = tk.Entry(self.janela_usuario)
        self.id_usuario = tk.Entry(self.janela_usuario)
        self.contato_usuario = tk.Entry(self.janela_usuario)

        self.nome_usuario.grid(row=0, column=1)
        self.id_usuario.grid(row=1, column=1)
        self.contato_usuario.grid(row=2, column=1)

        tk.Button(self.janela_usuario, text="Cadastrar", command=self.salvar_usuario).grid(row=3, column=0, columnspan=2)

    def salvar_usuario(self):
        nome = self.nome_usuario.get()
        id_usuario = self.id_usuario.get()
        contato = self.contato_usuario.get()
        self.biblioteca_db.adicionar_usuario(nome, id_usuario, contato)
        self.janela_usuario.destroy()

    def emprestar_livro(self):
        self.janela_emprestimo = tk.Toplevel(self.root)
        self.janela_emprestimo.title("Empréstimo de Livro")

        tk.Label(self.janela_emprestimo, text="Título do Livro:").grid(row=0, column=0)
        tk.Label(self.janela_emprestimo, text="ID do Usuário:").grid(row=1, column=0)

        self.titulo_emprestimo = tk.Entry(self.janela_emprestimo)
        self.id_emprestimo = tk.Entry(self.janela_emprestimo)

        self.titulo_emprestimo.grid(row=0, column=1)
        self.id_emprestimo.grid(row=1, column=1)

        tk.Button(self.janela_emprestimo, text="Emprestar", command=self.confirmar_emprestimo).grid(row=2, column=0, columnspan=2)

    def confirmar_emprestimo(self):
        titulo = self.titulo_emprestimo.get()
        id_usuario = self.id_emprestimo.get()
        mensagem = self.biblioteca_db.emprestar_livro(titulo, id_usuario)
        messagebox.showinfo("Resultado do Empréstimo", mensagem)
        self.janela_emprestimo.destroy()

    def devolver_livro(self):
        self.janela_devolucao = tk.Toplevel(self.root)
        self.janela_devolucao.title("Devolução de Livro")

        tk.Label(self.janela_devolucao, text="Título do Livro:").grid(row=0, column=0)
        tk.Label(self.janela_devolucao, text="ID do Usuário:").grid(row=1, column=0)

        self.titulo_devolucao = tk.Entry(self.janela_devolucao)
        self.id_devolucao = tk.Entry(self.janela_devolucao)

        self.titulo_devolucao.grid(row=0, column=1)
        self.id_devolucao.grid(row=1, column=1)

        tk.Button(self.janela_devolucao, text="Devolver", command=self.confirmar_devolucao).grid(row=2, column=0, columnspan=2)

    def confirmar_devolucao(self):
        titulo = self.titulo_devolucao.get()
        id_usuario = self.id_devolucao.get()
        mensagem = self.biblioteca_db.devolver_livro(titulo, id_usuario)
        messagebox.showinfo("Resultado da Devolução", mensagem)
        self.janela_devolucao.destroy()

    def consultar_livros(self):
        self.janela_consulta = tk.Toplevel(self.root)
        self.janela_consulta.title("Consultar Livros")

        tk.Label(self.janela_consulta, text="Consultar por:").grid(row=0, column=0, columnspan=2)
        tk.Label(self.janela_consulta, text="Título:").grid(row=1, column=0)
        tk.Label(self.janela_consulta, text="Autor:").grid(row=2, column=0)
        tk.Label(self.janela_consulta, text="Ano:").grid(row=3, column=0)

        self.consulta_titulo = tk.Entry(self.janela_consulta)
        self.consulta_autor = tk.Entry(self.janela_consulta)
        self.consulta_ano = tk.Entry(self.janela_consulta)

        self.consulta_titulo.grid(row=1, column=1)
        self.consulta_autor.grid(row=2, column=1)
        self.consulta_ano.grid(row=3, column=1)

        tk.Button(self.janela_consulta, text="Buscar", command=self.buscar_livros).grid(row=4, column=0, columnspan=2)

    def buscar_livros(self):
        titulo = self.consulta_titulo.get()
        autor = self.consulta_autor.get()
        ano = self.consulta_ano.get()

        resultados = []
        if titulo:
            livro = self.biblioteca_db.buscar_livro_por_titulo(titulo)
            if livro:
                resultados.append(livro)
        if autor:
            resultados.extend(self.biblioteca_db.buscar_livro_por_autor(autor))
        if ano:
            resultados.extend(self.biblioteca_db.buscar_livro_por_ano(ano))

        if resultados:
            resultados_str = "\n".join(f"{livro[1]} por {livro[2]} ({livro[3]}) - {livro[4]} cópias disponíveis" for livro in resultados)
            messagebox.showinfo("Resultados da Consulta", resultados_str)
        else:
            messagebox.showinfo("Resultados da Consulta", "Nenhum livro encontrado.")

        self.janela_consulta.destroy()

    def gerar_relatorios(self):
        self.janela_relatorios = tk.Toplevel(self.root)
        self.janela_relatorios.title("Relatórios")

        tk.Button(self.janela_relatorios, text="Livros Disponíveis", command=self.listar_livros_disponiveis).pack(fill="x", pady=5)
        tk.Button(self.janela_relatorios, text="Livros Emprestados", command=self.listar_livros_emprestados).pack(fill="x", pady=5)
        tk.Button(self.janela_relatorios, text="Usuários Cadastrados", command=self.listar_usuarios_cadastrados).pack(fill="x", pady=5)
        tk.Button(self.janela_relatorios, text="Fechar", command=self.janela_relatorios.destroy).pack(fill="x", pady=20)

    def listar_livros_disponiveis(self):
        livros = self.biblioteca_db.listar_livros()
        if livros:
            livros_str = "\n".join(f"{livro[1]} por {livro[2]} ({livro[3]}) - {livro[4]} cópias disponíveis" for livro in livros)
            messagebox.showinfo("Livros Disponíveis", livros_str)
        else:
            messagebox.showinfo("Livros Disponíveis", "Nenhum livro disponível.")

    def listar_livros_emprestados(self):
        emprestimos = self.biblioteca_db.listar_emprestimos()
        if emprestimos:
            emprestimos_str = "\n".join(f"{titulo} - Emprestado para {nome}" for titulo, nome in emprestimos)
            messagebox.showinfo("Livros Emprestados", emprestimos_str)
        else:
            messagebox.showinfo("Livros Emprestados", "Nenhum livro emprestado.")

    def listar_usuarios_cadastrados(self):
        usuarios = self.biblioteca_db.listar_usuarios()
        if usuarios:
            usuarios_str = "\n".join(f"{usuario[1]} (ID: {usuario[2]}) - Contato: {usuario[3]}" for usuario in usuarios)
            messagebox.showinfo("Usuários Cadastrados", usuarios_str)
        else:
            messagebox.showinfo("Usuários Cadastrados", "Nenhum usuário cadastrado.")


if __name__ == "__main__":
    root = tk.Tk()
    app = BibliotecaApp(root)
    root.mainloop()


