var utils = emmet.utils.common;
var actions = emmet.require('action/main.js');
var resources = emmet.resources;
var actionUtils = emmet.utils.action;
var editorUtils = emmet.utils.editor;
var htmlMatcher = emmet.htmlMatcher;

function pySetupEditorProxy() {
    editorProxy._syntax = cur_doc_type;
    utils.setCaretPlaceholder("%cursor%");
    resources.setVariable('newline', cur_doc.editor.eol_char);

    var matchPairHighlight = function(editor) {
    	var content = String(editor.getContent());
	var caretPos = editor.getCaretPos();
	if (content.charAt(caretPos) == '<')
            // looks like caret is outside of tag pair
            caretPos++;
	    var tag = htmlMatcher.tag(content, caretPos);
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
var editorProxy = {
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
	if (typeof end === 'undefined')
	    end = typeof start === 'undefined' ? this.getContent().length : start;
	if (typeof start === 'undefined') start = 0;
            var sel_range = this.getSelectionRange();
	if (sel_range.start === sel_range.end){
	    this.createSelection(start, end);
	}
	var scintilla = getScintilla();
	scintilla.replace_sel("");
    value = editorUtils.normalize(value);
	cur_doc.editor.insert_snippet(start, value);
    },
    getContent: function() {
	var scintilla = getScintilla();
	return scintilla.get_contents(scintilla.get_length()+1);
    },
    getSyntax: function() {
	return actionUtils.detectSyntax(this, cur_doc_type);;
    },
    getProfileName: function() {
	return pyDetectProfile();
    },
    prompt: function(title) {
	if (typeof title === 'undefined'){
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

function pyDetectProfile() {
    return actionUtils.detectProfile(editorProxy);
}
