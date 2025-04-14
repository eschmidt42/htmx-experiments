# HTMX-experiments
> Contact.app with and without `htmx`.

This repo is based on the book [hypermedia-systems](https://hypermedia.systems/). In the book an app is described called Contact.app. Though the book discusses classic html features and htmx features separately, the [example given there](https://hypermedia.systems/a-web-1-0-application/) ([github](https://github.com/bigskysoftware/contact-app)) contains both.

The purpose of this repo is to provide both the vanilla html web app as well as the a version which utilizes htmx, so a simple file diff can show how htmx is inserted and one can study its value.

## How to use

### Contact.app

`apps/web1` contains a minimal html app, without javascript libraries and without htmx bits.

##### `apps/web1`

The basic app from chapter ["A Web 1.0 Application"](https://hypermedia.systems/a-web-1-0-application/), without any htmx or js.

To start

    cd apps/web1
    flask run --debug

(`--debug` to automatically reload if python files were changed)

navigate in your browser to http://127.0.0.1:5000

#### `apps/web2`

* boosting links & forms for efficiency
* using DELETE
* validating input on client and server side
* paging

#### `apps/web3`

* active search
* lazy loading
* inline / bulk delete

#### `apps/web4`

* managing long running process, e.g. data download

#### `apps/web5`

* including a json data api

## References
* HTML standard: https://html.spec.whatwg.org/multipage/
