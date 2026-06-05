## TODO
- greedy dynamic cluster
	- consistency between local selection and global selection
		- done in an efficient way

- solution checker - new script
	- **first organize the output of the scripts in /algorithms**
	- then test the output, check below for each day
		- **number of routes - less than number of vehicles**
		- **distance per route - less than vehicle distance limit**
		- **demand per route - less than vehicle capacity**

		- no routes for days when vehicles are NOT available

		- frequencies satisfied 
			- unlike the others this kinda has to be checked dynamically
			- since when an edge is assigned to a day - its frequency is reset - i.e. deadline is reset
			- basically check if an edge has its frequency fulfilled for each time in the planning duration
			---
			- **how many times was it fulfilled**
			- **how many times did it go over deadline - over frequency**
	---
	- extra - show some visualizations with plots