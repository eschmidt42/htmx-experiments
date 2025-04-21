from dataclasses import dataclass

from fasthtml.common import (
    FT,
    H1,
    A,
    Button,
    Container,
    Div,
    Fieldset,
    FileResponse,
    Form,
    HtmxHeaders,
    Input,
    Label,
    Legend,
    Link,
    P,
    Redirect,
    Span,
    Table,
    Tbody,
    Td,
    Th,
    Thead,
    Title,
    Tr,
    fast_app,
    picolink,
    serve,
)

import htmx_experiments.contact as htmx_contact
from htmx_experiments.archiver import Archiver
from htmx_experiments.contact import Contact

htmx_contact.PAGE_SIZE = 10  # Controls number of items in pagination
Contact.load_db()


css = Link(rel="stylesheet", href="site.css", type="text/css")
app, rt = fast_app(hdrs=(picolink, css), static_path="./static")


@app.route("/")
def index():
    return Redirect("/contacts")


def get_rows(contacts) -> FT:
    _get_td_view = lambda c: Td(A("View", href=f"/contacts/{c.id}"))
    _get_td_edit = lambda c: Td(A("Edit", href=f"/contacts/{c.id}/edit"))
    _get_td_delete = lambda c: Td(
        A(
            "Delete",
            href="#",
            hx_delete=f"/contacts/{c.id}",
            hx_swap="outerHTML swap:1s",
            hx_confirm="Are you sure you want to delete this contact?",
            hx_target="closest tr",
        )
    )
    rows = Tbody(
        Tr(
            Td(c.first),
            Td(c.last),
            Td(c.phone),
            Td(c.email),
            _get_td_view(c),
            _get_td_edit(c),
            _get_td_delete(c),
        )
        for c in contacts
    )
    return rows


def get_search(q: str | None = None):
    _q = q if q else ""
    return Input(
        type="search",
        value=_q,
        name="q",
        hx_get="/contacts",
        hx_trigger="search, keyup delay:200ms changed",
        hx_target="tbody",
        hx_swap="outerHTML",
        hx_push_url="true",
    )


def get_index(contacts, search, page: int, archiver: Archiver):
    rows = get_rows(contacts)
    head = (Thead(Tr(Th("First"), Th("Last"), Th("Phone"), Th("Email"))),)

    a_previous = A("Previous", href=f"/contacts?page={page - 1}")
    a_next = A("Next", href=f"/contacts?page={page + 1}")
    pager = P(Div(Span((a_previous, a_next), style="float: right")))

    add_contacts = A("Add Contact", href="/contacts/new")

    counts = Span(hx_get="/contacts/count", hx_trigger="revealed")

    return Title("Contact App"), Container(
        H1("contacts.app"),
        get_archive_ui(Archiver.get()),
        get_search(search),
        Table(head, rows),
        pager,
        P(add_contacts, counts),
    )


@app.route("/contacts", methods=["GET"])
def contacts(
    headers: HtmxHeaders, q: str | None = None, page: int | None = 0
):  # request: Request
    search = q
    page = int(page) if page else 1
    print(f"{page=} {search=}")
    print(f"{headers=}")
    if search is not None:
        print("searching")
        contacts_set = Contact.search(search)
        if headers.trigger_name == "q":
            return get_rows(contacts=contacts_set)
    else:
        print("using all")
        contacts_set = Contact.all(page)
    print(f"{len(contacts_set)=}")
    return get_index(contacts_set, search, page, Archiver.get())


@app.route("/contacts/count")
def contacts_count():
    "`count` here to enable lazy loading, see https://hypermedia.systems/more-htmx-patterns/#_lazy_loading"
    count = Contact.count()
    return "(" + str(count) + " total Contacts)"


def get_new(c: Contact):
    values = Fieldset(
        Legend("Contact Values"),
        Div(
            P(
                Label("Email", _for="email"),
                Input(
                    name="email",
                    id="email",
                    type="email",
                    hx_get=f"/contacts/{c.id}/email",
                    hx_target="next .error",
                    placeholder="Email",
                    value=f"{c.email}",
                ),
                Span(c.errors.get("email"), _class="error"),
            ),
            P(
                Label("First Name", _for="first_name"),
                Input(
                    name="first_name",
                    id="first_name",
                    type="text",
                    placeholder="First Name",
                    value=f"{c.first}",
                ),
                Span(c.errors.get("first"), _class="error"),
            ),
            P(
                Label("Last Name", _for="last_name"),
                Input(
                    name="last_name",
                    id="last_name",
                    type="text",
                    placeholder="Last Name",
                    value=f"{c.last}",
                ),
                Span(c.errors.get("last"), _class="error"),
            ),
            P(
                Label("Phone", _for="phone"),
                Input(
                    name="phone",
                    id="phone",
                    type="text",
                    placeholder="Phone",
                    value=f"{c.phone}",
                ),
                Span(c.errors.get("phone"), _class="error"),
            ),
            _class="table rows",
        ),
        Button("Save", type="submit"),
    )

    return Title("Contact App"), Container(
        H1("contacts.app"),
        Form(values, action="/contacts/new", method="post"),
        P(A("Back", href="/contacts")),
    )


@app.route("/contacts/new", methods=["GET"])
def contacts_new_get():
    c = Contact()
    return get_new(c)


@dataclass
class FormData:
    first_name: str
    last_name: str
    phone: str
    email: str


@app.route("/contacts/new", methods=["POST"])
def contacts_new(d: FormData):
    c = Contact(None, d.first_name, d.last_name, d.phone, d.email)

    if c.save():
        return Redirect("/contacts")
    else:
        return get_new(c)


def get_show(c: Contact):
    return Title("Contact App"), Container(
        H1(f"{c.first} {c.last}"),
        Div(Div(f"Phone: {c.phone}"), Div(f"Email: {c.email}")),
        P(A("Edit", href=f"/contacts/{c.id}/edit"), A("Back", href="/contacts")),
    )


@app.route("/contacts/{contact_id}", methods=["GET"])
def contacts_view(contact_id: int = 0):
    contact = Contact.find(contact_id)
    if contact is None:
        raise NotImplementedError(f"Tried to find non-existing {contact_id=}")
    return get_show(contact)


def get_edit(c: Contact):
    values = Fieldset(
        Legend("Contact Values"),
        Div(
            P(
                Label("Email", _for="email"),
                Input(
                    name="email",
                    id="email",
                    type="email",
                    hx_get=f"/contacts/{c.id}/email",
                    hx_target="next .error",
                    placeholder="Email",
                    value=f"{c.email}",
                ),
                Span(c.errors.get("email"), _class="error"),
            ),
            P(
                Label("First Name", _for="first_name"),
                Input(
                    name="first_name",
                    id="first_name",
                    type="text",
                    placeholder="First Name",
                    value=f"{c.first}",
                ),
                Span(c.errors.get("first"), _class="error"),
            ),
            P(
                Label("Last Name", _for="last_name"),
                Input(
                    name="last_name",
                    id="last_name",
                    type="text",
                    placeholder="Last Name",
                    value=f"{c.last}",
                ),
                Span(c.errors.get("last"), _class="error"),
            ),
            P(
                Label("Phone", _for="phone"),
                Input(
                    name="phone",
                    id="phone",
                    type="text",
                    placeholder="Phone",
                    value=f"{c.phone}",
                ),
                Span(c.errors.get("phone"), _class="error"),
            ),
            _class="table rows",
        ),
        Button("Save", type="submit"),
        Button(
            "Delete Contact",
            id="delete-btn",
            hx_delete=f"/contacts/{c.id}",
            hx_target="body",
            hx_push_url="true",
            hx_confirm="Are you sure you want to delete this contact?",
        ),
    )

    return Title("Contact App"), Container(
        H1("contacts.app"),
        Form(values, action=f"/contacts/{c.id}/edit", method="post"),
        P(A("Back", href="/contacts")),
    )


@app.route("/contacts/{contact_id}/edit", methods=["GET"])
def contacts_edit_get(contact_id: int = 0):
    contact = Contact.find(contact_id)
    if contact is None:
        raise NotImplementedError(f"Tried to find non-existing {contact_id=}")
    return get_edit(contact)


@app.route("/contacts/{contact_id}/edit", methods=["POST"])
def contacts_edit_post(d: FormData, contact_id: int = 0):
    c = Contact.find(contact_id)
    if c is None:
        raise NotImplementedError(f"Tried to find non-existing {contact_id=}")
    c.update(d.first_name, d.last_name, d.phone, d.email)
    if c.save():
        return Redirect(f"/contacts/{contact_id}")
    else:
        return get_edit(c)


@app.route("/contacts/{contact_id}/email", methods=["GET"])
def contacts_email_get(email: str, contact_id: int = 0):
    "Validating e-mails server side, see https://hypermedia.systems/htmx-patterns/#_validating_emails_server_side"
    c = Contact.find(contact_id)
    if c is None:
        raise NotImplementedError(f"Tried to find non-existing {contact_id=}")

    c.email = email
    c.validate()
    return c.errors.get("email") or ""


@app.route("/contacts/{contact_id}", methods=["DELETE"])
def contacts_delete(headers: HtmxHeaders, contact_id: int = 0):
    c = Contact.find(contact_id)
    if c is None:
        raise NotImplementedError(f"Tried to find non-existing {contact_id=}")

    c.delete()

    if headers.trigger == "delete-btn":
        return Redirect("/contacts")
    else:
        return ""


def get_archive_ui(archiver: Archiver):
    match archiver.status():
        case "Waiting":
            val = Button("Download Contact Archive", hx_post="/contacts/archive")
        case "Running":
            val = (
                "Running ...",
                Div(
                    "Creating Archive ...",
                    Div(
                        Div(
                            id="archive-progress",
                            _class="progress-bar",
                            aria_valuenow=f"{archiver.progress() * 100}",
                            style=f"width:{archiver.progress() * 100}%",
                        ),
                        _class="progress",
                    ),
                    hx_get="/contacts/archive",
                    hx_trigger="load delay:500ms",
                    hx_target="#archive-ui",
                    hx_swap="outerHTML",
                ),
            )  # TODO: this does not update the progress bar properly, also a 404 was seen for GET /contacts/archive
        case "Complete":
            val = (
                A(
                    "Click here to download.",
                    hx_boost="false",
                    href="/contacts/archive/file",
                ),
                Button("Clear Download", hx_delete="/contacts/archive"),
            )  # TODO: this does not update the progress bar properly, also a 404 was seen for DELETE /contacts/archive
        case _:
            raise NotImplementedError()
    return Div(
        val,
        id="archive-ui",
        hx_target="this",
        hx_swap="outerHTML",
    )


@app.route("/contacts/archive", methods=["POST"])
def start_archive():
    "Added to enable archive UI, see https://hypermedia.systems/a-dynamic-archive-ui/#_adding_the_archiving_endpoint"
    archiver = Archiver.get()
    archiver.run()
    return get_archive_ui(archiver)


@app.route("/contacts/archive", methods=["GET"])
def archive_status():
    "Added to enable archive UI polling status update, see https://hypermedia.systems/a-dynamic-archive-ui/#_adding_the_progress_bar_ui"
    archiver = Archiver.get()
    return get_archive_ui(archiver)


@app.route("/contacts/archive/file", methods=["GET"])
def archive_content():
    "Added to enable file download in the archiver UI, see https://hypermedia.systems/a-dynamic-archive-ui/#_downloading_the_result"
    manager = Archiver.get()
    return FileResponse(
        manager.archive_file(), filename="contacts.json", media_type="text/plain"
    )


@app.route("/contacts/archive", methods=["DELETE"])
def reset_archive():
    "Added to enable cancellation of download in the archiver UI, see https://hypermedia.systems/a-dynamic-archive-ui/#_dismissing_the_download_ui"
    archiver = Archiver.get()
    archiver.reset()
    return get_archive_ui(archiver)


if __name__ == "__main__":
    serve(host="127.0.0.1", port=5006)
