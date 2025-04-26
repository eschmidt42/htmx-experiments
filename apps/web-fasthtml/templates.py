from fasthtml.common import (
    FT,
    H1,
    A,
    Button,
    Container,
    Div,
    Fieldset,
    Form,
    Input,
    Label,
    Legend,
    P,
    Span,
    Table,
    Tbody,
    Td,
    Th,
    Thead,
    Title,
    Tr,
)

from htmx_experiments.archiver import Archiver
from htmx_experiments.contact import Contact


def get_rows(contacts: list[Contact]) -> FT:
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


def get_search(q: str | None = None) -> FT:
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


def get_index(contacts, search, page: int):
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


def get_show(c: Contact):
    return Title("Contact App"), Container(
        H1(f"{c.first} {c.last}"),
        Div(Div(f"Phone: {c.phone}"), Div(f"Email: {c.email}")),
        P(A("Edit", href=f"/contacts/{c.id}/edit"), A("Back", href="/contacts")),
    )


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


def get_archive_ui(archiver: Archiver):
    _id = "archive-ui"
    url = "/contacts/archive"
    match archiver.status():
        case "Waiting":
            return Div(
                Button(
                    "Download Contact Archive",
                    hx_post=url,
                ),
                id=_id,
                hx_target="this",
                hx_swap="outerHTML",
            )

        case "Running":
            return Div(
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
                    hx_get=f"{url}/status",  # if "/update" is not used as in web4 / web5 etc this yields a 404 *shrug*
                    hx_trigger="load delay:500ms",
                ),
                id=_id,
                hx_target="this",
                hx_swap="outerHTML",
            )
        case "Complete":
            return Div(
                A(
                    "Click here to download.",
                    hx_boost="false",
                    href=f"{url}/file",
                ),
                Button(
                    "Clear Download", hx_delete=f"{url}/delete"
                ),  # # if "/update" is not used as in web4 / web5 etc this yields a 404 *shrug*
                id=_id,
                hx_target="this",
                hx_swap="outerHTML",
            )
        case _:
            raise NotImplementedError()
