import os
import sys
import markdown  
from functools import partial
from PyQt5.QtCore import Qt, QRect, QPoint, QRegExp, QSize
from PyQt5.QtGui import (QPainter, QColor, QFont, QTextFormat, QPolygon, 
                         QSyntaxHighlighter, QTextCharFormat, QTextCursor)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QWidget, QFileDialog, QTabWidget,
QMessageBox, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QToolButton, QMenu, QTextEdit, 
)


###############################################################################
# TitleBar Customizada com Menu Integrado
###############################################################################
class TitleBar(QWidget):
    """
    Barra de título customizada:
      - Exibe o título e um botão "Arquivo" que abre um QMenu.
      - Botões para minimizar, maximizar/restaurar e fechar.
      - Permite arrastar a janela.
    """
    def __init__(self, parent=None):
        super(TitleBar, self).__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(self.layout)

        self.menuButton = QToolButton()
        self.menuButton.setText("Arquivo")
        self.menuButton.setStyleSheet("""
            QToolButton {
                color: #d4d4d4;
                background-color: #2b2b2b;
                border: none;
                padding: 4px 8px;
            }
            QToolButton::menu-indicator { image: none; }
        """)
        self.menuButton.setFixedHeight(28)
        self.arquivoMenu = QMenu()
        self.arquivoMenu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: #d4d4d4;
                border: 1px solid #444444;
            }
            QMenu::item:selected {
                background-color: #444444;
            }
        """)
        self.arquivoMenu.addAction("Criar Projeto", partial(self.parent.newProject))
        self.arquivoMenu.addAction("Abrir Projeto", partial(self.parent.openProject))
        self.arquivoMenu.addAction("Compile", partial(self.parent.compileProject))
        self.arquivoMenu.addSeparator()
        self.arquivoMenu.addAction("Sair", partial(self.parent.close))
        self.menuButton.setMenu(self.arquivoMenu)
        self.menuButton.setPopupMode(QToolButton.InstantPopup)

        self.titleLabel = QLabel("MyEnchantMarkDown")
        self.titleLabel.setStyleSheet("color: #d4d4d4; font-size: 14px;")

        self.btnMinimize = QPushButton("–")
        self.btnMinimize.setFixedSize(40, 28)
        self.btnMinimize.setStyleSheet("background-color: #2b2b2b; color: #d4d4d4; border: none;")
        self.btnMinimize.clicked.connect(self.minimizeWindow)

        self.isMaximized = False
        self.btnMaximize = QPushButton("▭")
        self.btnMaximize.setFixedSize(40, 28)
        self.btnMaximize.setStyleSheet("background-color: #2b2b2b; color: #d4d4d4; border: none;")
        self.btnMaximize.clicked.connect(self.maximizeRestoreWindow)

        self.btnClose = QPushButton("X")
        self.btnClose.setFixedSize(40, 28)
        self.btnClose.setStyleSheet("background-color: #d32f2f; color: #ffffff; border: none;")
        self.btnClose.clicked.connect(self.closeWindow)

        self.layout.addWidget(self.menuButton)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.titleLabel)
        self.layout.addStretch()
        self.layout.addWidget(self.btnMinimize)
        self.layout.addWidget(self.btnMaximize)
        self.layout.addWidget(self.btnClose)

    def minimizeWindow(self):
        self.parent.showMinimized()

    def maximizeRestoreWindow(self):
        if not self.isMaximized:
            self.parent.showMaximized()
            self.isMaximized = True
            self.btnMaximize.setText("❐")
        else:
            self.parent.showNormal()
            self.isMaximized = False
            self.btnMaximize.setText("▭")

    def closeWindow(self):
        self.parent.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.move(self.parent.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

###############################################################################
# Custom Highlighter: Regras para CSS e Markdown
###############################################################################
class CustomHighlighter(QSyntaxHighlighter):
    def __init__(self, document, mode="markdown"):
        super(CustomHighlighter, self).__init__(document)
        self.mode = mode
        self.highlightingRules = []
        if self.mode == "css":
            self.setupCssRules()
        elif self.mode == "markdown":
            self.setupMarkdownRules()

    def setupCssRules(self):
        cssCommentFormat = QTextCharFormat()
        cssCommentFormat.setForeground(QColor("#6A9955"))
        self.highlightingRules.append((QRegExp(r"/\*.*\*/"), cssCommentFormat))
        cssStringFormat = QTextCharFormat()
        cssStringFormat.setForeground(QColor("#D69D85"))
        self.highlightingRules.append((QRegExp(r'".*?"'), cssStringFormat))
        self.highlightingRules.append((QRegExp(r"'.*?'"), cssStringFormat))
        cssPropFormat = QTextCharFormat()
        cssPropFormat.setForeground(QColor("#569CD6"))
        cssPropFormat.setFontWeight(QFont.Bold)
        self.highlightingRules.append((QRegExp(r"\b[a-zA-Z-]+(?=\s*:)"), cssPropFormat))
        cssSelectorFormat = QTextCharFormat()
        cssSelectorFormat.setForeground(QColor("#C586C0"))
        self.highlightingRules.append((QRegExp(r"^[^\{\}]+\{"), cssSelectorFormat))

    def setupMarkdownRules(self):
        # Cabeçalhos
        mdHeadingFormat = QTextCharFormat()
        mdHeadingFormat.setForeground(QColor("#569CD6"))
        mdHeadingFormat.setFontWeight(QFont.Bold)
        self.highlightingRules.append((QRegExp(r"^#{1,6} .*$"), mdHeadingFormat))
        # Negrito
        mdBoldFormat = QTextCharFormat()
        mdBoldFormat.setFontWeight(QFont.Bold)
        mdBoldFormat.setForeground(QColor("#CE9178"))
        self.highlightingRules.append((QRegExp(r"\*\*.*?\*\*"), mdBoldFormat))
        # Itálico
        mdItalicFormat = QTextCharFormat()
        mdItalicFormat.setFontItalic(True)
        mdItalicFormat.setForeground(QColor("#D4D4D4"))
        self.highlightingRules.append((QRegExp(r"\*[^*\n]+\*"), mdItalicFormat))
        # Código inline
        mdCodeFormat = QTextCharFormat()
        mdCodeFormat.setForeground(QColor("#DCDCAA"))
        mdCodeFormat.setFontFamily("Consolas")
        self.highlightingRules.append((QRegExp(r"`[^`]+`"), mdCodeFormat))
        # Links
        mdLinkFormat = QTextCharFormat()
        mdLinkFormat.setForeground(QColor("#3794FF"))
        self.highlightingRules.append((QRegExp(r"\[[^\]]+\]\([^)]+\)"), mdLinkFormat))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlightingRules:
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                if length == 0:
                    break
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)

###############################################################################
# CodeEditor: Editor com Numeração de Linha e Tema Dark
###############################################################################
class CodeEditor(QPlainTextEdit):
    def __init__(self, mode="markdown", parent=None):
        super(CodeEditor, self).__init__(parent)
        self.mode = mode
        self.foldedBlocks = {}
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #D4D4D4;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 12pt;
                selection-background-color: #3a3a3a;
            }
        """)

    def lineNumberAreaWidth(self):
        digits = len(str(self.blockCount()))
        space = 5 + self.fontMetrics().width("9") * digits + 20
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super(CodeEditor, self).resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(30, 30, 30))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#111111"))
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, top, self.lineNumberArea.width() - 20, self.fontMetrics().height(),
                                 Qt.AlignRight, number)
                # Desenha marcador de folding para blocos dobráveis
                text = block.text().lstrip()
                
            block = block.next()
            top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1



###############################################################################
# Área de Números de Linha
###############################################################################
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

###############################################################################
# MainWindow: Janela Principal Sem Moldura com Aba de Editor
###############################################################################
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

        # Instancia editores e seus highlighters
        self.md_editor = CodeEditor(mode="markdown")
        self.css_editor = CodeEditor(mode="css")
        self.md_highlighter = CustomHighlighter(self.md_editor.document(), mode="markdown")
        self.css_highlighter = CustomHighlighter(self.css_editor.document(), mode="css")
        self.tabs.addTab(self.md_editor, "mark.md")
        self.tabs.addTab(self.css_editor, "style.css")

        # Layout principal: TitleBar acima, abas abaixo
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.titleBar)
        layout.addWidget(self.tabs)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.resize(900, 600)

        # Lógica do projeto
        self.project_path = None
        self.md_editor.textChanged.connect(self.autoSave)
        self.css_editor.textChanged.connect(self.autoSave)

        # Conteúdo de exemplo inicial
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

    # Métodos de Projeto
    def newProject(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione ou Crie a Pasta do Projeto")
        if folder:
            self.project_path = folder
            md_path = os.path.join(self.project_path, "mark.md")
            css_path = os.path.join(self.project_path, "style.css")
            html_path = os.path.join(self.project_path, "index.html")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(self.md_editor.toPlainText())
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(self.css_editor.toPlainText())
            with open(html_path, "w", encoding="utf-8") as f:
                f.write("")
            QMessageBox.information(self, "Projeto", f"Projeto criado em:\n{self.project_path}")

    def openProject(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a Pasta do Projeto")
        if folder:
            md_path = os.path.join(folder, "mark.md")
            css_path = os.path.join(folder, "style.css")
            if os.path.exists(md_path) and os.path.exists(css_path):
                self.project_path = folder
                try:
                    with open(md_path, "r", encoding="utf-8") as f:
                        md_text = f.read()
                    with open(css_path, "r", encoding="utf-8") as f:
                        css_text = f.read()
                    self.md_editor.setPlainText(md_text)
                    self.css_editor.setPlainText(css_text)
                    QMessageBox.information(self, "Projeto", f"Projeto aberto com sucesso!\n{folder}")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao abrir o projeto: {e}")
            else:
                QMessageBox.warning(self, "Projeto", "A pasta selecionada não contém um projeto válido (mark.md e style.css não encontrados).")

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
            QMessageBox.warning(self, "Atenção", "Crie ou abra um projeto antes de compilar!")
            return
        md_path = os.path.join(self.project_path, "mark.md")
        html_path = os.path.join(self.project_path, "index.html")
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                md_text = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível ler os arquivos: {e}")
            return
        html_body = markdown.markdown(md_text, extensions=['attr_list','md_in_html'])
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
</html>"""
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_template)
            QMessageBox.information(self, "Compile", "index.html compilado com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao compilar index.html: {e}")

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
