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
            //
            var index = value.indexOf('{0}');
            var tabstopData = require('tabStops').extract(value, {
				escape: function(ch) {
					return ch;
				}
			});
            value = tabstopData.text;
            var firstTabStop = tabstopData.tabstops[0];
            if(!firstTabStop){
                firstTabStop= {
                        start: index-1,
                        end: index
                    }
            }
            if (sel_range.start === sel_range.end){
                this.createSelection(start, end);
            }
            var scintilla = getScintilla();
            scintilla.replace_sel(value);
            var cur_pos = (start <= end) ? start+firstTabStop.start : end+firstTabStop.end;
            this.setCaretPos(cur_pos);
		},

		getContent: function() {
			var scintilla = getScintilla();
			return scintilla.get_contents(scintilla.get_length()+1);

		},

		getSyntax: function() {
			return pyGetSyntax();
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
/**
 * Returns current syntax name
 * @return {String}
 */
function pyGetSyntax() {
	var scope = cur_doc_type;
    var syntax = 'html'
    if (scope == 'xml' || scope == 'xsl') {
		syntax = scope;
    }
    if(scope == 'css' || scope == 'less' || scope == 'sass'){
        syntax = 'css'
    }
    return require('actionUtils').detectSyntax(editorProxy, syntax);
}

function pyDetectProfile(argument) {
	return require('actionUtils').detectProfile(editorProxy);
}
