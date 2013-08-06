function pySetupEditorProxy() {
	editorProxy._syntax = cur_doc_type;
    require('utils').setCaretPlaceholder("%cursor%");
	var ind = (cur_doc.editor.indent_prefs.type === 0) ? "\s" : "\t";
    if(ind != "\t"){
        require("utils").repeatString(" ", cur_doc.editor.indent_prefs.width)
    }
	var nl = cur_doc.editor.eol_char;
	require('resources').setVariable('indentation', ind);
	require('resources').setVariable('newline', nl);
}
function getScintilla() {
	return cur_doc.editor.scintilla;
}

var editorProxy = emmet.exec(function(require, _) {
    return {
		getSelectionRange: function() {
			var scintilla = getScintilla();
			return {
				start: scintilla.get_selection_start(),
                end: scintilla.get_selection_end()
			};
		},

		createSelection: function(start, end) {
			var scintilla = getScintilla();
            scintilla.set_selection_start(start);
            scintilla.set_selection_end(end);
		},

		getCurrentLineRange: function() {
			var scintilla = getScintilla();
            var line = scintilla.get_current_line();
			return {
				start: scintilla.get_position_from_line(line),
				end: scintilla.get_line_end_position(line)
			};
		},

		getCaretPos: function() {
			var scintilla = getScintilla();
			return scintilla.get_current_position();
		},

		setCaretPos: function(pos){
            var scintilla = getScintilla();
			scintilla.set_current_position(pos);
		},

		getCurrentLine: function() {
			var scintilla = getScintilla();
			return scintilla.get_line(scintilla.get_current_line());
		},

		replaceContent: function(value, start, end, noIndent) {
            if (_.isUndefined(end))
				end = _.isUndefined(start) ? this.getContent().length : start;
			if (_.isUndefined(start)) start = 0;
            var sel_range = this.getSelectionRange();
            if (sel_range.start === sel_range.end){
                this.createSelection(start, end);
            }
            // indent new value
			if (!noIndent) {
                var utils = require('utils');
				value = utils.padString(value, utils.getLinePadding(this.getCurrentLine()));
			}
            var scintilla = getScintilla();
            scintilla.replace_sel("");
            cur_doc.editor.insert_snippet(start, value);
		},

		getContent: function() {
			var scintilla = getScintilla();
			return scintilla.get_contents(scintilla.get_length()+1);

		},

		getSyntax: function() {
			return require('actionUtils').detectSyntax(this, cur_doc_type);;
		},

		getProfileName: function() {
			return pyDetectProfile();
		},

		prompt: function(title) {
            if (_.isUndefined(title)){
                var title = 'Enter Abbreviation'; 
            }
			return prompt(title);
		},

		getSelection: function() {
			var scintilla = getScintilla();
			return scintilla.get_selection_contents();
		},

		getFilePath: function() {
			return cur_doc.file_name;
		}
	};
});

function require(name) {
	return emmet.require(name);
}
function pyDetectProfile(argument) {
	return require('actionUtils').detectProfile(editorProxy);
}