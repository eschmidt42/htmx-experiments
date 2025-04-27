# HTMX-experiments
> Progressively building up the Contact.app from the "hypermedia systems" book from plain html to `htmx` everywhere.

This repo is based on the book [hypermedia-systems](https://hypermedia.systems/). In the book an app is described called Contact.app. The book discusses classic html features and htmx features succcessively and provides  [code examples starting here](https://hypermedia.systems/a-web-1-0-application/) and beyond. Those code examples mostly build on top of each other, but sometimes also assume other code, available on the authors ([github repo for this book](https://github.com/bigskysoftware/contact-app)). That github repo serves a functioning Contact.app, but comes with a few bells and whistles in the code, whose connection to the parts in the book are not immediately obvious. Which I found made it a little bit difficult to connect the ideas in the book to the code. I would have preferred to see in the repo the app being progressively built up following the book.

The purpose of this repo is to do just that, for the book between the sections "A Web 1.0 Application" and "JSON Data APIs". In this repo the vanilla html web app can be found in [`apps/web1`](#appsweb1) and the versions with progressively added htmx features in [`apps/web2`](#appsweb2), [`apps/web3`](#appsweb3), [`apps/web4`](#appsweb4) and [`apps/web5`](#appsweb5).

Also, since I discovered htmx through Jeremy Howard's [intro video](https://youtu.be/QqZUzkPcU7A?si=nwwMKnWAkXgTWdhK) and chat with [Carson Gross](https://youtu.be/WuipZMUch18?si=sFL0EWtNgBV1Utl5), I couldn't help myself to try and reproduce the Contact.app with [`python-fasthtml`](https://pypi.org/project/python-fasthtml/). You can find that in [`apps/web-fasthtml`](#appsweb-fasthtml).

Note that I've kept the code pieces from the book / authors' repo which I felt are most educating and fit into what I'm interested in. This may be different for you. So I strongly encourage to read the book to find what I've skipped ^^, but there are way more gems to discover, e.g. the "Bringing Hypermedia To Mobile" section or the authors' takes on the history on web development, at least I found that very clarifying.

## Setup

[Install uv](https://docs.astral.sh/uv/getting-started/installation/). Clone this repo

    git clone https://github.com/eschmidt42/htmx-experiments.git

Install dependencies and create virtual env

    cd htmx-experiments
    uv sync

## How to use


### `apps/web1`

The basic app from chapter ["A Web 1.0 Application"](https://hypermedia.systems/a-web-1-0-application/), without any htmx or js.

To start

    cd apps/web1
    flask run --debug --port 5001

(`--debug` to automatically reload if python files were changed)

To use navigate in your browser to http://127.0.0.1:5001

### `apps/web2`

Adds

* boosting links & forms for efficiency
* using DELETE
* validating input on client and server side
* paging

To start

    cd apps/web2
    flask run --debug --port 5002

To use navigate in your browser to http://127.0.0.1:5002

### `apps/web3`

Adds

* active search
* lazy loading
* inline / bulk delete

To start

    cd apps/web3
    flask run --debug --port 5003

To use navigate in your browser to http://127.0.0.1:5003

### `apps/web4`

Adds

* management of a long running process, e.g. data download

To start

    cd apps/web4
    flask run --debug --port 5004

To use navigate in your browser to http://127.0.0.1:5004

### `apps/web5`


Adds

* a json data api

To start

    cd apps/web5
    flask run --debug --port 5005

To use navigate in your browser to http://127.0.0.1:5005

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

### `apps/web-fasthtml`

Same as `apps/web4` but using `python-fasthtml`, replacing the need for a css file, html files and jinja2 templating.

To start

    cd apps/web-fasthtml
    python app.py

To use navigate in your browser to http://127.0.0.1:5006

## References
* HTML standard: https://html.spec.whatwg.org/multipage/
