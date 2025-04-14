

from functools import partial
from PyQt5.QtCore import Qt, QRect, QRegExp, QSize
from PyQt5.QtGui import (QPainter, QColor, QFont, QTextFormat, 
                         QSyntaxHighlighter, QTextCharFormat)

from PyQt5.QtWidgets import (
    QPlainTextEdit, QWidget, QHBoxLayout, QPushButton, QLabel, QToolButton, QMenu, QTextEdit, QCompleter
)
import json


"""
Barra de título customizada:
    - Exibe o título e um botão "Arquivo" que abre um QMenu.
    - Botões para minimizar, maximizar/restaurar e fechar.
    - Permite arrastar a janela.
"""
class TitleBar(QWidget):
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

        self.btnHost = QPushButton("Host")
        self.btnHost.setFixedSize(40, 28)
        self.btnHost.setStyleSheet("background-color: #2b2b2b; color: #d4d4d4; border: none;")
        self.btnHost.clicked.connect(partial(self.parent.hostProject))

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
        self.layout.addWidget(self.btnHost)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.titleLabel)
        
        self.layout.addStretch()
        
        self.layout.addWidget(self.btnMinimize)
        self.layout.addWidget(self.btnMaximize)
        self.layout.addWidget(self.btnClose)

    def  updateTitle(self, title):
        self.titleLabel.setText("MyEnchantMarkDown // " + title)

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

        htmlTagNameFormat = QTextCharFormat()

        htmlTagNameFormat.setForeground(QColor("#ff7c22"))
        htmlTagNameFormat.setFontWeight(QFont.Bold)
        self.highlightingRules.append((QRegExp(r"</?[a-zA-Z]+\b"), htmlTagNameFormat))
        htmlBracketFormat = QTextCharFormat()

        htmlBracketFormat.setForeground(QColor("#ff7c22"))
        htmlBracketFormat.setFontWeight(QFont.Bold)
        self.highlightingRules.append((QRegExp(r">"), htmlBracketFormat))
        htmlAttrFormat = QTextCharFormat()

        htmlAttrFormat.setForeground(QColor("#b35a1d"))
        self.highlightingRules.append((QRegExp(r"\b[a-zA-Z-]+(?=\=)"), htmlAttrFormat))
        htmlAttrValueFormat = QTextCharFormat()

        htmlAttrValueFormat.setForeground(QColor("#efb48b"))
        self.highlightingRules.append((QRegExp(r'".*?"'), htmlAttrValueFormat))
        self.highlightingRules.append((QRegExp(r"'.*?'"), htmlAttrValueFormat))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlightingRules:
            index = pattern.indexIn(text)
            while index >= 0:
                length = pattern.matchedLength()
                if length == 0:
                    break
                self.setFormat(index, length, fmt)
                index = pattern.indexIn(text, index + length)


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

        if self.mode == "css":
            self.initCompleter()

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


    def initCompleter(self):
        with open("properties.json", "r", encoding="utf-8") as f:
            keywords = json.load(f)
            keywords = list(keywords.keys())
        self.completer = QCompleter(keywords, self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insertCompletion)
        self.completer.popup().setStyleSheet("""
            QListView {
                background-color: #2b2b2b;
                color: #d4d4d4;
                outline: none;
                border: 1px solid #444444;
                font-size: 12px;
            }
            QListView::item {
                padding: 4px 8px;
            }
            QListView::item:selected {
                background-color: #444444;
                color: #ffffff;
            }
        """)
    
    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)
    

    
    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(tc.WordUnderCursor)
        return tc.selectedText()
    
    def keyPressEvent(self, event):
        if self.mode == "markdown":
            return super(CodeEditor, self).keyPressEvent(event)

        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                event.ignore()
                return

        super(CodeEditor, self).keyPressEvent(event)

        prefix = self.textUnderCursor()

        if len(prefix) < 2:
            self.completer.popup().hide()
            return

        if prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(prefix)


        popup = self.completer.popup()
        width = popup.sizeHintForColumn(0) + popup.verticalScrollBar().sizeHint().width()

        cr = self.cursorRect()
        cr.setWidth(width)

        self.completer.complete(cr)

#
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)
