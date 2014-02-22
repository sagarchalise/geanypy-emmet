function pySetupEditorProxy() {
	editorProxy._syntax = cur_doc_type;
    require('utils').setCaretPlaceholder("%cursor%");
	var nl = cur_doc.editor.eol_char;
	require('resources').setVariable('newline', nl);
    var actions = require('actions');
    var matchPairHighlight = function(editor) {
        var matcher = require('htmlMatcher');
		var content = String(editor.getContent());
		var caretPos = editor.getCaretPos();
		if (content.charAt(caretPos) == '<')
            // looks like caret is outside of tag pair
            caretPos++;
        var tag = matcher.tag(content, caretPos);
        if(tag){
            if(tag.open.range.inside(caretPos)){
                editor.setIndicator(tag.open.range);
                if(tag.close){
                    editor.setIndicator(tag.close.range);
                }
            }
            else if(tag.close && tag.close.range.inside(caretPos)){
                editor.setIndicator(tag.open.range);
                editor.setIndicator(tag.close.range);
            }
            return true;
        }
        return false;
    };
    actions.add('highlight_tag', matchPairHighlight, {hidden: true});
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
			scintilla.set_current_position(pos, true);
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
		},
        setIndicator: function(range){
            var geanyIndicators = [geanyIndicatorSearch, 1];
            for(var i=0;i<geanyIndicators.length;i++){
                var start = range.start;
                var stop = range.end;
                if(i == 1){
                    start += 1;
                    stop -= 1;
                }
                cur_doc.editor.indicator_set_on_range(geanyIndicators[i], start, stop);
            }
        },
	};
});

function require(name) {
	return emmet.require(name);
}
function pyDetectProfile(argument) {
	return require('actionUtils').detectProfile(editorProxy);
}