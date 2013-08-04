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

var _completions = {};

function require(name) {
	return emmet.require(name);
}

function pyExpandAbbreviationAsYouType(abbr) {
	var info = require('editorUtils').outputInfo(editorProxy);
	try {
		var result = emmet.expandAbbreviation(abbr, info.syntax, info.profile, 
					require('actionUtils').captureContext(editorProxy));
		return pyPreprocessText(result);
	} catch (e) {
		return '';
	}
	
}

function pyWrapAsYouType(abbr, content) {
	var info = require('editorUtils').outputInfo(editorProxy);
	content = require('utils').escapeText(content);
	var ctx = require('actionUtils').captureContext(editorProxy);
	try {
		var result = require('wrapWithAbbreviation').wrap(abbr, content, info.syntax, info.profile, ctx);
		return pyPreprocessText(result);
	} catch(e) {
		return '';
	}
}

function pyCaptureWrappingRange() {
	var info = require('editorUtils').outputInfo(editorProxy);
	var range = editorProxy.getSelectionRange();
	var startOffset = range.start;
	var endOffset = range.end;
	
	if (startOffset == endOffset) {
		// no selection, find tag pair
		var match = require('htmlMatcher').find(info.content, startOffset);
		if (!match) {
			// nothing to wrap
			return null;
		}
		
		/** @type Range */
		var utils = require('utils');
		var narrowedSel = utils.narrowToNonSpace(info.content, match.range);
		startOffset = narrowedSel.start;
		endOffset = narrowedSel.end;
	}

	return [startOffset, endOffset];
}

function pyGetTagNameRanges(pos) {
	var ranges = [];
	var info = require('editorUtils').outputInfo(editorProxy);
		
	// search for tag
	try {
		var tag = require('htmlMatcher').tag(info.content, pos);
		if (tag) {
			var open = tag.open.range;
			var tagName = /^<([\w\-\:]+)/i.exec(open.substring(info.content))[1];
			ranges.push([open.start + 1, open.start + 1 + tagName.length]);

			if (tag.close) {
				ranges.push([tag.close.range.start + 2, tag.close.range.start + 2 + tagName.length]);
			}
		}
	} catch (e) {}

	return ranges;
}

function pyGetTagRanges() {
	var ranges = [];
	var info = require('editorUtils').outputInfo(editorProxy);
		
	// search for tag
	try {
		var tag = require('htmlMatcher').tag(info.content, editorProxy.getCaretPos());
		if (tag) {
			ranges.push(tag.open.range.toArray());
			if (tag.close) {
				ranges.push(tag.close.range.toArray());
			}
		}
	} catch (e) {}

	return ranges;
}

function pyExtractAbbreviation() {
	return require('expandAbbreviation').findAbbreviation(editorProxy);
}

function pyHasSnippet(name) {
	return !!emmet.require('resources').findSnippet(editorProxy.getSyntax(), name);
}

/**
 * Get all available CSS completions. This method is optimized for CSS
 * only since it should contain snippets only so it's not required
 * to do extra parsing
 */
function pyGetCSSCompletions(dialect) {
	dialect = dialect || pyGetSyntax();

	if (!_completions[dialect]) {
		var all = require('resources').getAllSnippets(dialect);
		var css = require('cssResolver');
		_completions[dialect] = _.map(all, function(v, k) {
			var snippetValue = typeof v.parsedValue == 'object' 
				? v.parsedValue.data
				: v.value;
			var snippet = css.transformSnippet(snippetValue, false, dialect);
			return {
				k: v.nk,
				label: snippet.replace(/\:\s*\$\{0\}\s*;?$/, ''),
				v: css.expandToSnippet(v.nk, dialect)
			};
		});
	}

	return _completions[dialect];
}

/**
 * Returns current syntax name
 * @return {String}
 */
function pyGetSyntax() {
	var scope = cur_doc_type;
    var syntax = 'html'
    if (scope == 'xml' || scope == 'xsl') {
		syntax = 'xsl';
    }
    if(scope == 'css' || scope == 'less' || scope == 'sass'){
        syntax = 'css'
    }
    return require('actionUtils').detectSyntax(editorProxy, syntax);
}

function pyDetectProfile(argument) {
	return require('actionUtils').detectProfile(editorProxy);
}