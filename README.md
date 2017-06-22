# bgc
Board game collection. Query Board Game Geek for a user's games and then create a spreadsheet with relevant information for choosing what to play.

## setup
requires python 3
`pip install tryagain` also required

## use
Before you start, make sure macros are enabled in libre office calc by going to
	`Tools > Options > Libre Office > Security > Macro Security`

### command line
`cd` to directory with executable
`python bgc.py [username] [playername]`
`clip < output\collection_[username].csv` this copies the contents of the file to the clipboard
or just `run [username]`

### libre office
open `print_this_file.ods` in libre office
open the tab `Game Data`
`Ctrl + V` paste the contents of the csv
rename the first tab to the name of the player, e.g. "Trevor"
open the first tab
go to `Format > Print Ranges > Edit`
change the user-defined print range to include only the list of games
	e.g. if you have 107 games in your list then it should be `$A$1:$AD$107`
	e.g. if you have 222 games in your list then it should be `$A$1:$AD$222`
print the document



