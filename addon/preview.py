from typing import Literal

import anki.cards
import anki.notes
import aqt
from aqt import QDialog, QHBoxLayout, QKeySequence, QPushButton, QShortcut, Qt, QVBoxLayout
from aqt.sound import play_clicked_audio
from aqt.webview import AnkiWebView, AnkiWebViewKind


class PreviewDialog(QDialog):
    """Clean standalone preview dialog with full collection.media and audio support."""

    def __init__(self, note: anki.notes.Note, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint
        )

        self._note: anki.notes.Note = note
        # ord=0 corresponds to the 1st card template, ord=1 for 2nd, etc.
        self._card: anki.cards.Card = self._note.ephemeral_card(ord=0)
        self._state: Literal['q', 'a'] = 'q'

        self.setWindowTitle('Preview')
        self.resize(550, 650)

        main_layout = QVBoxLayout(self)

        # initialize AnkiWebView with PREVIEWER kind for correct media routing
        self._web = AnkiWebView(parent=self, kind=AnkiWebViewKind.PREVIEWER)
        # connect bridge commands so clicking audio icons plays media from collection.media
        self._web.set_bridge_command(self._on_bridge_cmd, self)
        main_layout.addWidget(self._web)

        # controls layout
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self._prev_btn = QPushButton('<', self)
        self._prev_btn.setToolTip('Show Front (Left Arrow)')
        self._prev_btn.clicked.connect(self.show_front)
        bottom_layout.addWidget(self._prev_btn)

        self._next_btn = QPushButton('>', self)
        self._next_btn.setToolTip('Show Back (Right Arrow)')
        self._next_btn.clicked.connect(self.show_back)
        bottom_layout.addWidget(self._next_btn)

        main_layout.addLayout(bottom_layout)

        # keyboard shortcuts
        self._left_shortcut = QShortcut(QKeySequence('Left'), self)
        self._left_shortcut.activated.connect(self.show_front)

        self._right_shortcut = QShortcut(QKeySequence('Right'), self)
        self._right_shortcut.activated.connect(self.show_back)

        self.render_current_state()

    def _on_bridge_cmd(self, cmd: str) -> None:
        """Play audio files stored in collection.media when clicked."""
        if cmd.startswith('play:'):
            play_clicked_audio(cmd, self._card)

    def show_front(self):
        if self._state != 'q':
            self._state = 'q'
            self.render_current_state()

    def show_back(self):
        if self._state != 'a':
            self._state = 'a'
            self.render_current_state()

    def update_content(self, front: str, back: str, css: str):
        model = self._note.note_type()
        if model is None:
            return
        model['css'] = css
        template = model['tmpls'][0]
        template['qfmt'] = front
        template['afmt'] = back
        self._card = self._note.ephemeral_card(ord=0)
        self.render_current_state()

    def render_current_state(self):
        rendered = self._card.render_output()

        body_content = rendered.question_text if self._state == 'q' else rendered.answer_text

        # converts sound placeholders
        if aqt.mw:
            body_content = aqt.mw.prepare_card_text_for_display(body_content)

        # construct inner HTML (without <html> or <body> tags)
        inner_html = f"""
        <style>
            {self._card.css()}
        </style>
        <div id="qa" class="card card1">
            {body_content}
        </div>
        """

        # stdHtml automatically wraps body, loads MathJax, and inserts
        # <base href="..."> pointing to Anki's local media web server.
        self._web.stdHtml(
            inner_html,
            css=['css/reviewer.css'],
            js=['js/mathjax.js', 'js/vendor/mathjax/tex-chtml-full.js', 'js/reviewer.js'],
            context=self,
        )
        self._update_button_states()

    def _update_button_states(self):
        self._prev_btn.setEnabled(self._state == 'a')
        self._next_btn.setEnabled(self._state == 'q')
