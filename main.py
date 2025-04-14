import os
import sys
import markdown  
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QTabWidget, QMessageBox, QVBoxLayout,QShortcut
)
from editor import CodeEditor, CustomHighlighter, TitleBar
from PyQt5.QtGui import QKeySequence

import threading
import http.server
import socketserver
import webbrowser



PORT = 8000

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("background-color: #1e1e1e;")

        self.titleBar = TitleBar(self)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background-color: #1e1e1e; }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #d4d4d4;
                padding: 6px 10px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #444444;
            }
            QTabBar::tab:hover {
                background-color: #3a3a3a;
            }
        """)

        self.md_editor = CodeEditor(mode="markdown")
        self.css_editor = CodeEditor(mode="css")
        self.md_highlighter = CustomHighlighter(self.md_editor.document(), mode="markdown")
        self.css_highlighter = CustomHighlighter(self.css_editor.document(), mode="css")
        self.tabs.addTab(self.md_editor, "mark.md")
        self.tabs.addTab(self.css_editor, "style.css")

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.titleBar)
        layout.addWidget(self.tabs)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.resize(900, 600)

        self.shortcut_compile = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_compile.activated.connect(self.compileProject)

        self.project_path = None
        self.md_editor.textChanged.connect(self.autoSave)
        self.css_editor.textChanged.connect(self.autoSave)

        sample_md = (
            "# Cabeçalho 1\n"
            "Texto de exemplo em *Markdown*.\n"
            "## Cabeçalho 2\n"
            "Mais texto com **negrito** e `código inline`.\n"
            "[Link](https://example.com)\n"
        )
        sample_css = (
            "/* Exemplo de CSS */\n"
            "body {\n"
            "    background-color: #1e1e1e;\n"
            "    color: #d4d4d4;\n"
            "}\n"
            ".container {\n"
            "    width: 100%;\n"
            "    margin: 0 auto;\n"
            "}\n"
        )
        self.md_editor.setPlainText(sample_md)
        self.css_editor.setPlainText(sample_css)

    def newProject(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione ou Crie a Pasta do Projeto")
        if folder:
            self.project_path = folder
            title = os.path.basename(folder)
            self.titleBar.updateTitle(f"Projeto: {title}")
            md_path = os.path.join(self.project_path, "mark.md")
            css_path = os.path.join(self.project_path, "style.css")
            html_path = os.path.join(self.project_path, "index.html")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(self.md_editor.toPlainText())
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(self.css_editor.toPlainText())
            with open(html_path, "w", encoding="utf-8") as f:
                f.write("")
            self.msgPopUp( "Projeto", f"Projeto criado em:\n{self.project_path}")


    def msgPopUp(self,title, message):
        msg = QMessageBox()
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                border: 2px solid #444444;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #444444;
                color: #d4d4d4;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()



    def openProject(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a Pasta do Projeto")
        if folder:
            
            md_path = os.path.join(folder, "mark.md")
            css_path = os.path.join(folder, "style.css")
            if os.path.exists(md_path) and os.path.exists(css_path):
                self.project_path = folder
                title = os.path.basename(folder)
                self.titleBar.updateTitle(f"Projeto: {title}")
                try:
                    with open(md_path, "r", encoding="utf-8") as f:
                        md_text = f.read()
                    with open(css_path, "r", encoding="utf-8") as f:
                        css_text = f.read()
                    self.md_editor.setPlainText(md_text)
                    self.css_editor.setPlainText(css_text)
                    self.msgPopUp( "Projeto", f"Projeto aberto com sucesso!\n{folder}")
                except Exception as e:
                    self.msgPopUp( "Erro", f"Erro ao abrir o projeto: {e}")
            else:
                self.msgPopUp( "Projeto", "A pasta selecionada não contém um projeto válido (mark.md e style.css não encontrados).")

    def autoSave(self):
        if self.project_path:
            md_path = os.path.join(self.project_path, "mark.md")
            css_path = os.path.join(self.project_path, "style.css")
            try:
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(self.md_editor.toPlainText())
                with open(css_path, "w", encoding="utf-8") as f:
                    f.write(self.css_editor.toPlainText())
            except Exception as e:
                print("Erro ao salvar arquivos:", e)

    def compileProject(self):
        if not self.project_path:
            self.msgPopUp( "Atenção", "Crie ou abra um projeto antes de compilar!")
            return
        md_path = os.path.join(self.project_path, "mark.md")
        html_path = os.path.join(self.project_path, "index.html")

        

        try:
            with open(md_path, "r", encoding="utf-8") as f:
                md_text = f.read()
        except Exception as e:
            self.msgPopUp( "Erro", f"Não foi possível ler os arquivos: {e}")
            return
        md_text = md_text.replace("<div", "<div markdown=1") 
        html_body = markdown.markdown(md_text, extensions=['extra','attr_list','md_in_html'])
        html_template = f"""<!DOCTYPE html>
                            <html lang="pt">
                            <head>
                                <meta charset="UTF-8">
                                <title>Projeto</title>
                                <link rel="stylesheet" href="style.css">
                                
                            </head>
                            <body>
                            {html_body}

                            </body>
                            <script>
                            setInterval(function() {{
                                // Se tiver ?print=1 na Url, Não atualiza a página
                                if (window.location.href.indexOf("?print=1") === -1) {{
                                    window.location.reload();   
                                }}
                                
                            }}, 5000);
                            </script>
                            </html>
                        """
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_template)
            self.msgPopUp( "Compile", "index.html compilado com sucesso!")
        except Exception as e:
            self.msgPopUp( "Erro", f"Erro ao compilar index.html: {e}")

    def hostProject(self):
        if not self.project_path:
            self.msgPopUp("Atenção", "Abra ou crie um projeto antes de hostear!")
            return

        self.compileProject()

        project_dir = self.project_path

        Handler = http.server.SimpleHTTPRequestHandler

        def serve():
            os.chdir(project_dir)  
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                print(f"Servidor rodando em http://localhost:{PORT}")
                httpd.serve_forever()

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()

        webbrowser.open(f"http://localhost:{PORT}")
        self.msgPopUp("Host", f"Servidor iniciado em http://localhost:{PORT}")

###############################################################################
# Execução da Aplicação
###############################################################################
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
