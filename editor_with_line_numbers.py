from kivy.effects.scroll import ScrollEffect
from kivy.graphics import Color, Rectangle
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.text import Label as CoreLabel
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, BooleanProperty


kv = '''
<Editor>:
    bar_width: 10
    code_input: code_input
    line_number: line_number
    RelativeLayout:
        id: rel
        size_hint: 1, None
        height: max(root.height, box.minimum_height)
        BoxLayout:
            id: box
            Label:
                id: line_number
                canvas.before:
                    Color:
                        rgba: (.1, .1, .1, 1)
                    Rectangle:
                        size: self.size
                        pos: self.pos
                size_hint: None, None
                font_name: code_input.font_name
                font_size: code_input.font_size
                text_size: self.size
                height: code_input.height
                width: 40
                valign: 'top'
                padding_y: code_input.padding[1]
            CodeInput:
                id: code_input
                size_hint_y: None
                height: root.height + self.minimum_height - self.line_height - self.padding[1]
'''
Builder.load_string(kv)


class Editor(ScrollView):
    code_input = ObjectProperty()
    line_number = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.effect_cls = ScrollEffect
        self.cursor_row_trigger = Clock.create_trigger(self.on_cursor_row)
        self.lines_trigger = Clock.create_trigger(self.on_lines_changed)
        self.code_input.bind(_lines=self.lines_trigger)
        self.code_input.bind(cursor_row=self.cursor_row_trigger)
        self.code_input.bind(height=self.on_content_height)
        self._cached_content_height = self.code_input.height

    def on_content_height(self, *args):
        old_height = self._cached_content_height
        height = self.code_input.height
        dh = height - old_height
        old_max_y = self.height + self.scroll_y * (old_height - self.height)
        if self.code_input.height > self.height:
            sy = ( old_max_y - self.height + dh ) / (height - self.height)
            self.scroll_y = sy
            self.cursor_row_trigger()
        self._cached_content_height = self.code_input.height

    def on_cursor_row(self, *args):
        pos = self.code_input.cursor_pos
        max_y = self.height + self.scroll_y * (self.code_input.height - self.height)
        min_y = max_y - self.height
        if max_y < pos[1]:
            scroll = self.convert_distance_to_scroll(0, max(0, pos[1] - self.height + 1))
            self.scroll_y = scroll[1]
        elif min_y > pos[1] - self.code_input.line_height:
            scroll = self.convert_distance_to_scroll(0, max(0, pos[1] - self.code_input.line_height - 1))
            self.scroll_y = scroll[1]

    def on_lines_changed(self, *args):
        n = len(self.code_input._lines)
        self.line_number.text = '\n'.join("%4d" % i for i in range(1, n + 1))


if __name__ == '__main__':
    from kivy.base import runTouchApp
    editor = Editor(size_hint=(None, None), size=(200, 300), 
                    pos_hint= {'center_x': 0.5, 'center_y': 0.5} )
    editor.code_input.text = '\n'.join(str(i) for i in range(1, 33))
    runTouchApp(editor)
