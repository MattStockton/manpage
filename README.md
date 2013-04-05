# ManPage: Quickly find out what a command does

**ManPage** is a small experiment to create an easier way to explore manpages

The basic idea is to provide a search box for a shell command. When you search, ManPage returns exactly what the arguments to the shell command will do.

This is a quick hack / experiment, but I hope to refine and improve it in the future. 

## Under The Hood

ManPage uses [Python](http://www.python.org/) and [Flask](http://flask.pocoo.org/). The public demo is hosted on [Heroku](http://www.heroku.com/).

There is a utility script in the /tools directory, which provides the mechanism for converting man pages to txt

## See ManPage in action

Visit [manpage.me](http://manpage.me/) to try the demo