import bs4
from bs4.dammit import EntitySubstitution
import re

class Line(object):
	def __init__(self, text, allow_inline, indent_level, no_content_alteration = False):
		self.text = text
		self.allow_inline = allow_inline
		self.indent_level = indent_level
		self.no_content_alteration = no_content_alteration
	
	def __repr__(self):
		return "%i: %s'%s'"%(self.indent_level, ('[inline] ' if self.allow_inline else ''), self.text)

class Printer(object):
	indentation = u"\t"
	maximum_text_length = 70
	inline_tags = set(['span', 'em', 'strong', 'b', 'i', 'img', 'button', 'input', 'font', 'wbr'])
	self_closeable_tags = set(['button', 'img', 'audio', 'video', 'iframe'])
	tags_with_contents_that_cannot_be_altered = set(['pre', 'script', 'css'])
	unhandled_entity_types = set([bs4.element.CData, bs4.element.ProcessingInstruction, bs4.element.Doctype, bs4.element.Declaration, bs4.element.Comment])
	
	def pretty_print(self, html):
		assert isinstance(self.indentation, unicode)
		doc = bs4.BeautifulSoup(html)
		lines = reduce(lambda a,b: a+b, map(self.lines, doc.contents))
		return self.string_from_lines(lines)
	
	def lines(self, node, indent_level=0):
		if self.node_is_unhandleable(node):
			empty_doc = bs4.BeautifulSoup("")
			empty_doc.append(node)
			return [Line(unicode(empty_doc), True, indent_level)]
		elif isinstance(node, bs4.element.NavigableString):
			return [Line(line_str, True, indent_level) for line_str in unicode(node).split("\n")]
		elif isinstance(node, bs4.element.Tag):
			if node.name.lower() in self.tags_with_contents_that_cannot_be_altered:
				return [Line(unicode(node), False, indent_level, True)]
			else:
				lines = []
				inline = self.node_is_inline(node)
				self_closing = self.can_tag_self_close(node)
				lines.append(Line(self.make_opening_tag(node, self_closing), inline, indent_level))
				if not self_closing:
					for child in node.contents:
						lines += self.lines(child, indent_level+1)
					lines.append(Line(u"</%s>"%(node.name), inline, indent_level))
				return lines
	
	def string_from_lines(self, lines):
		
		def join_inlines(line_list_1, line_list_2):
			left = line_list_1[-1] if len(line_list_1) else None
			right = line_list_2[0] if len(line_list_2) else None
			if left and right and left.allow_inline and right.allow_inline and abs(left.indent_level - right.indent_level) <= 1:
				merged_line = Line(left.text + right.text, True, min(left.indent_level, right.indent_level))
				return line_list_1[:-1] + [merged_line] + line_list_2[1:]
			else:
				return line_list_1 + line_list_2
		
		lines = reduce(join_inlines, [[line] for line in lines])
		
		def break_line(line):
			if line.no_content_alteration:
				return [line]
			line.text = line.text.strip()
			result_lines = []
			if len(line.text) > self.maximum_text_length:
				break_point = self.find_break_point_in_line_text(line.text)
				if break_point != None:
					result_lines += break_line(Line(line.text[break_point:].strip(), line.allow_inline, line.indent_level))
					line.text = line.text[:break_point].strip()
			result_lines.insert(0, line)
			return result_lines
		
		lines = reduce(lambda a,b: a+b, [break_line(line) for line in lines])
		
		return u"\n".join([self.string_from_line(line) for line in lines if len(line.text.strip()) > 0])
	
	def string_from_line(self, line):
		return self.indentation * line.indent_level + line.text
	
	def find_break_point_in_line_text(self, text):
		break_points = list(re.finditer(r"(^[^\<]+|\>[^\<]*)(\s)", text))
		indices = [point.start(2) for point in break_points]
		indices_before_max_length = [i for i in indices if i <= self.maximum_text_length]
		if len(indices_before_max_length) > 0:
			return indices_before_max_length[-1]
		elif len(indices) > 0:
			return indices[0]
		else:
			return None
	
	def node_is_inline(self, node):
		return node.name.lower() in self.inline_tags if isinstance(node, bs4.element.Tag) else True
	
	def node_is_unhandleable(self, node):
		for kind in self.unhandled_entity_types:
			if isinstance(node, kind):
				return True
		return False
	
	def can_tag_self_close(self, tag_node):
		return tag_node.name.lower() in self.self_closeable_tags and tag_node.is_empty_element
	
	def make_opening_tag(self, tag_node, self_closing=False):
		components = [tag_node.name]
		for attr, value in tag_node.attrs.iteritems():
			if isinstance(value, list):
				value = u" ".join(value)
			components.append(u'%s="%s"'%(attr, EntitySubstitution.substitute_html(value)))
		start = u"<"
		end = u"/>" if self_closing else u">"
		return start +  u" ".join(components) + end

def beautiful_print(html):
	return Printer().pretty_print(html)

if __name__=='__main__':
	ex1 = """<!DOCTYPE HTML>
	<html>
	<head>
	<script>
	function() {
		if (2 > 1) {
			console.log("well that's a relief");
		}
	}
	</script>
	</head>
	<body>
	<h1>Hello, world</h1>
	<p>This is a <em>long, long, long</em> sentence with inline content, including an image (<img src='photo.png'/>).</p>
	<pre>do not
disturb the indentation!
  okay?</pre>
	<!--COMMENT-->
	</body>
	</html>
	"""
	ex1 = """	 	 <html> <body> <div>it sure is hot inside this div! <em>right?</em>
	 </div> <p>Yep!</p> <img src=fire.gif></img> </body> </html>"""
	print beautiful_print(ex1)
	