from distutils.core import setup
setup(
  name = 'beautiful_print',
  packages = ['beautiful_print'], # this must be the same as the name above
  version = '0.11',
  description = 'Prettier pretty-printing of HTML.',
  author = 'Nate Parrott',
  author_email = 'nate@nateparrott.com',
  url = 'https://github.com/nate-parrott/beautiful_print', # use the URL to the github repo
  download_url = 'https://github.com/nate-parrott/beautiful_print/tarball/0.1', # I'll explain this in a second
  keywords = ['HTML', 'BeautifulSoup', 'pretty print', 'readable'], # arbitrary keywords
  classifiers = [],
	install_requires = ['beautifulsoup4']
)
