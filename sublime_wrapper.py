import sublime
import sublime_plugin


class Vars:
    all_pos_row_cols = []
    wrapper_activated = False


class ToggleWrapper:
    @staticmethod
    def on():
        Vars.wrapper_activated = True

    @staticmethod
    def off():
        Vars.wrapper_activated = False


WRAPPERS = [
    [
        ['Packages/PHP/PHP.sublime-syntax'],
        [
            ['if', 'Wrap with if condition'],
            ['if / else', 'Wrap with if {} else {} block'],
            ['while', 'Wrap with while{} block'],
            ['for', 'Wrap with for() {} block'],
            ['foreach', 'Wrap with foreach() {} block'],
            ['try / catch', 'Wrap with TryCatch'],
            ['public function', 'Wrap with Public Function'],
            ['protected function', 'Wrap with Protected Function'],
            ['private function', 'Wrap with Private Function']
        ],
        [
            [['if (${1}) {'], ['}']],
            [['if (${1}) {'], ['} else {', '\t${2}', '}']],
            [['while (${1}) {'], ['}']],
            [['for (${1}) {'], ['}']],
            [['foreach (${1}) {'], ['}']],
            [['try {'], ['} catch (${2}) {', '\t${1}', '}']],
            [['public function ${1}()', '{'], ['}']],
            [['protected function ${1}()', '{'], ['}']],
            [['private function ${1}()', '{'], ['}']]

        ]
    ],
    [
        [
            'Packages/JavaScript/JavaScript.sublime-syntax',
            'Packages/JavaScriptNext - ES6 Syntax/JavaScriptNext.tmLanguage'
        ],
        [
            ['if', 'Wrap with if condition'],
            ['if / else', 'Wrap with if {} else {} block'],
            ['for', 'Wrap with for() {} block'],
            ['while', 'Wrap with while{} block'],
            ['function', 'Wrap with Function'],
            ['try / catch', 'Wrap with TryCatch']
        ],
        [
            [['if (${1}) {'], ['}']],
            [['if (${1}) {'], ['} else {', '\t${2}', '}']],
            [['for (${1}) {'], ['}']],
            [['while (${1}) {'], ['}']],
            [['function ${1}()', '{'], ['}']],
            [['try {'], ['}', 'catch (${1}) {', '\t${2}', '}']]
        ]
    ],
    [
        [
            'Packages/Python/Python.sublime-syntax',
            'Packages/Python 3/Python3.tmLanguage',
            'Packages/Python Improved/PythonImproved.tmLanguage',
            'Packages/MagicPython/grammars/MagicPython.tmLanguage'
        ],
        [
            ['if', 'Wrap with if condition'],
            ['if / else', 'Wrap with: if - else block'],
            ['if / elif', 'Wrap with: if - elif block'],
            ['for', 'Wrap with: for block'],
            ['while', 'Wrap with: while block'],
            ['def', 'Wrap with function declaration'],
            ['try / except', 'Wrap with: try - except block'],
            ['with', 'Wrap with: with block'],
        ],
        [
            [['if ${1}:'], ['']],
            [['if ${1}:'], ['else:', '\t${2}']],
            [['if ${1}:'], ['elif:', '\t${2}']],
            [['for ${1}:'], ['']],
            [['while ${1}:'], ['']],
            [['def ${1}():'], ['']],
            [['try:'], ['except Exception as e:', '\t${1}']],
            [['with open(${1}) as f:'], ['']],
        ]
    ],
    [
        ['Packages/JavaScript/JSON.sublime-syntax'],
        [
            ['[ ]', 'Wrap with Array'],
            ['[ ],', 'Wrap with Array and comma'],
            ['{ }', 'Wrap with Object'],
            ['{ },', 'Wrap with Object and comma']
        ],
        [
            [['['], [']']],
            [['['], ['],']],
            [['{'], ['}']],
            [['{'], ['},']],
        ]
    ]
]


class ActivateWrapCommand(sublime_plugin.WindowCommand):

    chosen_wrappers = []

    def run(self):
        """ Detect current file syntax and return the associated wrapper.
        In case the syntax is not supported a will be shown in the bottom status bar """
        if self.detect_wrapper():
            self.window.show_quick_panel(self.chosen_wrappers[1], self.on_done)
        else:
            self.window.status_message('Current Syntax NOT Supported')

    def detect_wrapper(self):
        active_syntax = self.window.active_view().settings().get('syntax')
        for wrapper in WRAPPERS:
            syntaxes = wrapper[0]
            for syntax in syntaxes:
                if syntax == active_syntax:
                    self.chosen_wrappers = wrapper
                    return True
        # return False  # None is falsy as well, no need for explicit False

    def on_done(self, index):
        # Panel Canceled
        if index == -1:
            self.window.status_message('Sublime Wrap Cancelled.')
        # Item Selected
        else:
            active_view = self.window.active_view()
            active_view.run_command(
                'wrap', {"wrapper": self.chosen_wrappers[2][index]})


class WrapCommand(sublime_plugin.TextCommand):

    def run(self, edit, wrapper):
        # Store all the selected regions
        BODY_REGIONS = []
        for region in self.view.sel():
            if region.empty():
                BODY_REGIONS.append(self.view.line(region.begin()))
            else:
                BODY_REGIONS.append(sublime.Region(
                    region.begin(), region.end()))
            self.view.add_regions('BODY_REGIONS', BODY_REGIONS,
                                  'mark', 'dot', sublime.HIDDEN | sublime.PERSISTENT)
        for r in self.view.sel():
            region = self.view.line(r)
            begin_line = self.view.line(region.begin())
            end_line = self.view.line(region.end())

            # Upper defined content exists
            if wrapper[1]:
                end_line_match = self.view.find('[^\t\s]+', end_line.begin())
                tab_and_space = ''
                if end_line_match:
                    tab_and_space = self.view.substr(sublime.Region(
                        end_line.begin(), end_line_match.begin()))
                    end_line_contents = ''
                    for str_index, string in enumerate(wrapper[1]):
                        if str_index == len(wrapper[1]) - 1:
                            end_line_contents += tab_and_space + string
                        else:
                            end_line_contents += tab_and_space + string + '\n'
                self.view.insert(edit, end_line.end(),
                                 '\n' + end_line_contents)

            # Downside defined content exists
            if wrapper[0]:
                begin_line_match = self.view.find(
                    '[^\t\s]+', begin_line.begin())
                tab_and_space = ''
                if begin_line_match:
                    tab_and_space = self.view.substr(sublime.Region(
                        begin_line.begin(), begin_line_match.begin()))
                    begin_line_contents = ''
                    for string in wrapper[0]:
                        begin_line_contents += tab_and_space + string + '\n'
                self.view.insert(edit, begin_line.begin(), begin_line_contents)
        body_regions = self.view.get_regions('BODY_REGIONS')
        self.view.sel().clear()
        self.view.sel().add_all(body_regions)
        self.view.run_command('indent')  # ???
        self.view.erase_regions('BODY_REGIONS')

        # Store all defined positions(${1}, ${2}, etc.) in the defined content
        # in group
        positions = []

        # Store all defined positions(${1}, ${2}, etc.) found from start point
        # to the end in the current view
        order_defined_regions = []
        for i in range(1, 10):
            pattern = '\$\{' + str(i) + '\}'
            defined_regions = self.view.find_all(pattern, 0)
            if defined_regions:
                positions.append(defined_regions)

        order_defined_regions = self.view.find_all('\$\{\d+\}', 0)
        if positions:
            Vars.all_pos_row_cols = []
            for defined_regions in positions:
                pos_row_cols = []
                for defined_region in defined_regions:
                    pos_row_cols.append(
                        self.view.rowcol(defined_region.begin()))
                Vars.all_pos_row_cols.append(pos_row_cols)
            # Erase all ${num} from end to start
            if order_defined_regions:
                for order_defined_region in order_defined_regions[::-1]:
                    self.view.replace(edit, order_defined_region, '')

            if Vars.all_pos_row_cols:
                ToggleWrapper.on()
                self.view.run_command('move_caret')
            else:
                ToggleWrapper.off()


class MoveCaretCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if Vars.all_pos_row_cols:
            pos_row_cols = Vars.all_pos_row_cols.pop(0)
            points = []
            for pos_row_col in pos_row_cols:
                row = pos_row_col[0]
                col = pos_row_col[1]
                point = self.view.text_point(row, col)
                points.append(sublime.Region(point, point))
            self.view.sel().clear()
            self.view.sel().add_all(points)


class CheckWrapperStatus(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        if Vars.wrapper_activated:
            # Activate wrapper setting when defined positions remains in this
            # global list
            if Vars.all_pos_row_cols:
                ToggleWrapper.on()
            else:
                ToggleWrapper.off()
