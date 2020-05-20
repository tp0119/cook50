# Design document for Cook50
# by Tulsi Patel

The structure of the code for this website is split into four main categories.
First, there is the python file application.py that contains all of the flask and routes to the different webpages on the site.
Next, there is the SQL database, cookbook.db. The next are all of the html templates that each route in application.py redirects to.
Finally, there are the CSS and Bootstrap stylesheets.

The python file application.py begins with the necessary import statements, followed by the various routes
that are called with "GET" and "POST" when a user clicks on a button or link on the website.
Each route will be described in more detail when each individual template is discussed.

Application.py also imports the database, cookbook.db. This SQL database has four tables.
Users stores information like username and password for each individual who uses the site.
Recipes is the "main" table that stores each user's unique id, along with every recipe they input into their cookbook.
The Shopping List table was made to store each user's unique id and the items on their shopping list.
A separate Shopping List table was made (as opposed to storing a user's items in the Recipes table) for greater efficiency.
The Recipes table would have otherwise grown too large and cluttered.
With two separate tables, the information is more organized because it's separated.
Finally, there is a planner table.
It was important that this table was also its own, separate table because the user would have to add and delete recipes to a certain day on a weekly basis.
Therefore, simply adding a "day" column to an existing table would not have been efficient, since the user would otherwise have to delete and re-add the entire recipe.
This table easily links the user's id to a day of the week and an existing recipe in the Recipes table.
Additionally, giving each entry in every table a unique key was incredibly important.
The unique keys add more functionality to the website by allowing the user to delete recipes, update quantities of items on their shopping list, and more.

Next, I will discuss the design and implementation of each template and its corresponding route.
First, users had to be able to log into the website to access their personal recipes.
Therefore, it was necessary that I implement log in/log out and register templates and routes.

The homepage of the website is the "index.html" template. In this file, in addition to a few others in my website,
I had to add another jinja block called {% block import %} to add a few new import statements to the layout.html file because
I ended up using some JQuery and a few html icons like the stars for the recipe rating and a trash can to delete a recipe.
The main element in index.html is a table of the user's recipes and their respective details.
The route that corresponds to index.html was "/", and it was designed to select all of the user's recipes from the database
and pass it to index.html as a list of dictionaries.
A for loop was implemented in jinja in the html file to display each recipe.
One design element that is common throughout all of the pages that allow users to delete stuff are the Javascript (JS) functions I created.
First, in the html body, there is a hidden text field.
The trash can icon on the page is actually a button that when pressed, sends the id of the recipe to the JS function.
Inside the script tags, the JS passes the recipe id to the empty, hidden text field and submits the form.
The input is then passed to a route in application.py (titled remove, delete, or the like) which takes the recipe id
and uses it to remove the selected recipe from whichever table it's assigned to delete items from.
The decision was made to use JS since it was the most efficient way to link the html aspect (the delete button, for example)
to the database we wanted to remove from.

The Add Recipe page is a mainly form.
Something on this page that is common to all of the pages is the h2 tag displaying the page's title.
I thought this was a necessary feature to add for the user's convenience when navigating through the site.
It was decided that the recipe name and type of meal should be required components to add to the cookbook to make them the most salient
aspects for this cookbook. By quickly browing through the cookbook and seeing a recipe's name and which type of meal it is,
it can help users easily plan their meals.
Therefore, the "Add" button is grayed out until users enter a recipe's name and its type. The other parameters are optional.
JS was again used to gray out the button. The apology.html file is included in the templates folder just in case some code falls through,
and it becomes necessary to display a back-up error page.
The "/add" route not only get all of the elements entered into the form, but it also checks if any main ingredients were entered or not.
If no main ingredients were entered, it assigns "No ingredients listed" to the i1 (ingredient 1) column in the Recipes table in the cookbook.db.
Then, the route redirects to the index page once a recipe is successfully added.

The Shopping List template has two main parts: a form and a table.
The form requires the user enter at least the item's name to add it to their list. The "Add" button is again grayed out if that field is left empty.
The table displays the item's name, quantity, a checkbox, and a delete button.
The "/shoppinglist" route checks if a quantity was entered by the user.
If no quantity is entered, the route sets the default quantity in the Shopping List table as 1.
This design decision was made because it is most likely the person who neglected to specify a quanitity only needs 1 of the item.
Inputting a 0 would not make sense since if the user needed 0 of an item, they wouldn't add it to the list to begin with.
The checkboxes are there for the user's convenience. When they acquire an item, it's easy and quick to check it off the list.
The delete button is there to remove items that have been acquired or are no longer needed.
This template implements a delete function in JS almost identical to the one implemented in index.html.
However, this remove function removes recipes from the Shopping List table, not the Recipes table.
It is also important to note that whenever I implement a for loop in jinja inside a template, I have chosen to pass not only a list of dictionaries,
but also the length of each list to the corresponding html template to use inside the for loop.
Designing the for loop as {% for k in length %} helps me keep the code organized and remind myself that rows is a list of dictionaries,
not simply a list or just a dictionary.

The planner template also has two main parts: a form to add a recipe to a day, and the table displaying each day's planned meals.
The form only allows users to add recipes that are already in their cookbook.
This decision was made because it made the most sense—one of the main purposes of a virtual cookbook is to help users easily
view and plan meals to make, so the meals they can plan from are the ones in their cookbook.
They can specify day of the week, meal type, and recipe name.
Next, seven tables are displayed, one for each day of the week.
This was a better design that displaying all meals in one large table because the smaller, color-coded tables
make it easy and quick to find a day and its corresponding recipes. It's easier on the eye as well.
Because of the decision to use 7 small tables, in the "/planning" route, I had to get 7 separate lists containing recipes of each respective day of the week,
which were then all passed to the template. The route also adds new recipes to the Planner table in the database.
It was also decided that users would only be able to plan breakfasts, lunches, and dinners since those are the 3 main meals in a day.

Finally, the timer template allows a user to enter the number of minutes they want to set their timer to.
The design decision to only allow minutes between 0 and 60 was because most recipes only require baking or cooking time to be within that range.
When the "POST" method is called on timer, the "/timer" route takes the input of minutes and sends it to timerdisplay.html which actually shows the timer.
The code for implementing the timer in timerdisplay.html was taken from StackOverflow, the main modifications being it now displays the minutes the user entered
and the display itself is bigger and easier for the user to see.

A search bar was added to the navigation bar (as opposed to a specific page like index.html) so that the user could search from a recipe by name from anywhere on the website.
If there are recipes in the cookbook that have the name the user typed in, a table similar to that in index.html will show up.
However, this template is called searchresults.html.
If no recipe matches the name entered, an apology will be displayed. Underneath, there will also be a link the Add Recipe page,
giving users the option to enter the recipe into their cookbook if they so choose.

As for the layout, a horizontal navigation bar was kept constant throughout the site, giving users easy access to switch between pages,
go back to the home screen, search for recipes, and log out.
In addition to styles.css,there I added a file called bootstrap.min.css from the website Bootswatch.
From Bootswatch.com, I downloaded the style code for their Bootstrap theme called Minty and uploaded it as the additional stylesheet.
In layout.html, I import this new CSS and Bootstrap file in order to give my website a softter, more modern aesthetic.
Also, to add more flair to the page, I downloaded and imported a Favicon icon that is called "Shallow pan of food."
I diplay it in the tab/title part of my website. Additionally, I used it in place of the "0" in "Cook50."