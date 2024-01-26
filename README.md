# Go Fluent Automation

This project is a proof of concept on how you can automatise the process of simulating some human actions on a real
world website. It teaches the basics of scraping and parsing. You can also learn semi object oriented programming since
the project is mostly made of classes.

## Configuration

In order to run the project, you'll need to set up the environment variables in an `.env` file. With the following keys
values :

- `OPENAI_ORGANIZATION` : The OpenAI organization key which can be found
  at https://platform.openai.com/account/organization.
- `OPENAI_API_KEY` : The OpenAI API key which can be found at https://platform.openai.com/api-keys.

For the credentials you have two ways of storing them (note that you can store credentials of multiple peoples) :

- `GOFLUENT_USERNAME__<PROFILE_NAME>` : The GoFluent username to log in to the app (replace `<PROFILE_NAME>` by the name
  of the profile you want).
- `GOFLUENT_PASSWORD__<PROFILE_NAME>` : The GoFluent password to log in to the app (replace `<PROFILE_NAME>` by the name
  of the profile you want).

You can also put default credentials with the following keys :

- `GOFLUENT_USERNAME` : The GoFluent username to log in to the app.
- `GOFLUENT_PASSWORD` : The GoFluent password to log in to the app.

## Run the project

Project CLI helper :

```
usage: python3 -m src.main [-h] (--auto-run AUTO_RUN_COUNT | --simple-run URL) [--vocabulary | --grammar] [--debug | --no-debug]
                           [--headless | --no-headless] [--profile PROFILE]

automatically execute some go fluent activities.

options:
  -h, --help            show this help message and exit
  --auto-run AUTO_RUN_COUNT
                        the amount of activities to do for the month (e.g. only does 2 if you already did 8).
  --simple-run URL      the URL of the activity to solve.
  --vocabulary          Do the vocabulary activities.
  --grammar             Do the grammar activities
  --debug, --no-debug   Enable the debug mode. Shows more logs messages in the terminal.
  --headless, --no-headless
                        Run the firefox instance in headless mode (meaning the window won't show).
  --profile PROFILE     The name of the credentials profile stored in the .env file.
```