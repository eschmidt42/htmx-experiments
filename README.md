# HTMX-experiments
> Contact.app with and without `htmx`.

This repo is based on the book [hypermedia-systems](https://hypermedia.systems/). In the book an app is described called Contact.app. Though the book discusses classic html features and htmx features separately, the [example given there](https://hypermedia.systems/a-web-1-0-application/) ([github](https://github.com/bigskysoftware/contact-app)) contains both.

The purpose of this repo is to provide both the vanilla html web app as well as the a version which utilizes htmx, so a simple file diff can show how htmx is inserted and one can study its value.

As a bonus this repo also contains a `python-fasthtml` version of the Contact.app from the Hypermedia Systems book.

## How to use

### Contact.app

`apps/web1` contains a minimal html app, without javascript libraries and without htmx bits.

##### `apps/web1`

The basic app from chapter ["A Web 1.0 Application"](https://hypermedia.systems/a-web-1-0-application/), without any htmx or js.

To start

    cd apps/web1
    flask run --debug --port 5001

(`--debug` to automatically reload if python files were changed)

navigate in your browser to http://127.0.0.1:5000

#### `apps/web2`

Adds

* boosting links & forms for efficiency
* using DELETE
* validating input on client and server side
* paging

To start

    cd apps/web2
    flask run --debug --port 5002

#### `apps/web3`

Adds

* active search
* lazy loading
* inline / bulk delete

To start

    cd apps/web3
    flask run --debug --port 5003

#### `apps/web4`

Adds

* management of a long running process, e.g. data download

To start

    cd apps/web4
    flask run --debug --port 5004

#### `apps/web5`


Adds

* a json data api

To start

    cd apps/web5
    flask run --debug --port 5005

Following some example curls for the json data api.

Listing all contacts

    curl -X GET http://localhost:5005/api/v1/contacts

Adding a contact

    curl -X POST -d "first_name=Joooohn&last_name=Doe&phone=555-1234&email=jooooohn@example.com" http://localhost:5005/api/v1/contacts

Viewing a specific contact

    curl -X GET http://localhost:5005/api/v1/contacts/2

Update a specific contact

    curl -X PUT -d "first_name=Carson&last_name=Gross&phone=123-456-7890&email=carson@example.comzzzz" http://localhost:5005/api/v1/contacts/2

Deleting a specific contact

    curl -X DELETE http://localhost:5005/api/v1/contacts/2

#### `apps/web-fasthtml`

Same as `apps/web4` but using `fasthtml`, replacing the need for css file, html files and jinja2 templating.

To start

    cd apps/web-fasthtml
    python app

## References
* HTML standard: https://html.spec.whatwg.org/multipage/
