### SUMMARY:

### TODO:
- verify how the openai connection works, where its at, and what changes to make to its section.
	- do we just prompt the user on launch to notify that we're connecting, and if there's no env variable or config file we'll ask them to enter their key and then create a config.ini in the directory
- fix the textbox of the directory section so that the text is not editable.  also, get rid of the "chosen directory" portion.
- in the contents table we should introduce an easy way to clear all cells or selected cells. 
	- maybe with the delete/backspace key. but also a button below edit that says 'clear all'.
- figure out all models available through the api so that we can list them in the dropbox for selection.
	- verify the process, if any, for switching between models
- introduce a usage statistics area with things like:
	- summary requests made
	- token usage? input and output?
	- models used
- upon exiting, if the user hasn't saved, prompt them to. 
- also, upon exiting the user should recieve a pop up window telling them where their file was saved as well as the total usage statistics at the end.
	- if the file isn't saved and they click end, we'll tell them to saved
		- if they do, we'll show them the full end window showing location and usage
		- if they dont, we'll just show them the full usage without the file saving location.