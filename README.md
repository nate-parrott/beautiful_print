# `beautiful_print`

## Better pretty-printing of HTML in Python

Sometimes you want to take ugly HTML and fix it up, adding proper indentation and consistent style and all that. The best way I found to do this in Python was through `BeautifulSoup`'s `prettify` function, but it didn't do everything I needed. `beautiful_print` does.

 - choose the whitespace you want to use for indentation
 - break long lines
 - treat certain tags like `<em>` as inline, and don't insert new lines every time they're encountered

And it's built atop the HTML-parsing magic of [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/).

## Usage

    $ pip install beautiful_print

_Then_,

    from beautiful_print import beautiful_print
	 
	 ugly_html = """
	 <html> <body> <div>it sure is hot inside this div! <em>right?</em>
	 </div> <p>Yep!</p> <img src=fire.gif></img> </body> </html>
	 """
	 print beautiful_print(ugly_html)
	 
	 <html>
	 	<body>
	 		<div>
	 			it sure is hot inside this div! <em>right?</em>
	 		</div>
	 		<p>
	 			Yep!
	 		</p>
	 		<img src="fire.gif"/>
	 	</body>
	 </html>
