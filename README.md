# Go Fluent Automation

This project is a proof of concept on how you can automatise the process of simulating some human actions on a real
world website. It teaches the basics of scraping and parsing. You can also learn semi object-oriented programming since
the project is mostly made of classes.

## Configuration

In order to run the project, you'll need to set up the environment variables in an `.env` file (create the file if not
done yet). With the following keys
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

Example :

```
python3 -m src.main --auto-run 10 --grammar
```

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

Two main runners are set up, you can either automatically execute the auto run mode where the count of done activities
is retrieved and the scraper automatically does the needed activities to match the expected count. The other way is to
execute the simple run mode which solve an activity automatically by specifying a link in the CLI.

## Technical Documentation

### Project structure

The project architecture is the following :

- `.env` : This file stores the credentials and api keys used in the application (not stored in GitHub).
- `.env.example` : This is the example schema of the `.env` file.
- `src/` : The source folder, storing all the main code of the application.
    - `src/classes/` : The project classes (because the project is an OOP based project).
        - `src/classes/activity` : The activity class, storing the information about an activity (grammar /
          vocabulary). An activity (from an url) is composed of a lesson and a quiz.
        - `src/classes/solving` : The solving class, handling all the driver operations to solve an activity, retrieving
          the questions, finding and caching the answers and retrying the quiz until the expected score is achieved.
        - `src/classes/learning` : The learning class, retrieving the information of an activity (in order to give to
          the AI).
        - `src/classes/logger` : The logger class.
        - `src/classes/scraper` : The scraper class, handling the firefox webdriver (selenium) and all global automation
          actions (logging in, navigate through the website...).
        - `src/classes/questions/` : The questions classes. In order to solve the different kinds of questions on the
          website, every combination of questions types has a class that scrape, parse and solve this question.
    - `src/utils` : The utils files. Every filename matches its content and provide methods to help process and handle
      different types of data.
    - `src/runners` : The main app runners, handling the global logic of the code (abstraction for the parser).

## Improvements & Bugs

- improv: using Kor to get securely typed data from OpenAI
- bug: when an activity skips because "All questions have been used and it's trying to retake the quiz.", the done activities count reset? to debug, check `scraper.py:387`