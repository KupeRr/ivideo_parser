# ivideo_parser
The task of the program is to receive a certain number of new links to cameras and all the data that is on the site about them(https://tv.ivideon.com/). It was necessary to create a parser that would run from time to time and write data to the database mysql. 

## My Additions

To work it is necessary to fill the configuration file, namely:

- Specify the data to connect to the database
- Specify the headers
- Specify the desired number of new links per run
