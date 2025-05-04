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


def get_layout(*args, h1_str: str = "contacts.app"):
    title = Title("Contact App")
    h1 = H1(h1_str)
    return title, Container(h1, *args)


def get_index(contacts, page: int, search: str | None = None):
    archive_ui = get_archive_ui(Archiver.get())
    search_ui = get_search(search)

    head = (Thead(Tr(Th("First"), Th("Last"), Th("Phone"), Th("Email"))),)
    rows = get_rows(contacts)
    table = Table(head, rows)

    a_previous = A("Previous", href=f"/contacts?page={page - 1}")
    a_next = A("Next", href=f"/contacts?page={page + 1}")
    pager = P(Div(Span((a_previous, a_next), style="float: right")))

    add_contacts = A("Add Contact", href="/contacts/new")

    counts = Span(hx_get="/contacts/count", hx_trigger="revealed")

    return get_layout(
        archive_ui,
        search_ui,
        table,
        pager,
        P(add_contacts, counts),
    )


def get_contact_property_tag(
    c: Contact, label: str, key: str, value: str, error_key: str
):
    return P(
        Label(label, _for=key),
        Input(
            name=key,
            id=key,
            type="text",
            placeholder=label,
            value=value,
        ),
        Span(c.errors.get(error_key), _class="error"),
    )


def get_contact_email_tag(c: Contact):
    return P(
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
    )


def get_new(c: Contact):
    contact_fields = Fieldset(
        Legend("Contact Values"),
        Div(
            get_contact_email_tag(c),
            get_contact_property_tag(
                c, "First Name", "first_name", f"{c.first}", "first"
            ),
            get_contact_property_tag(c, "Last Name", "last_name", f"{c.last}", "last"),
            get_contact_property_tag(c, "Phone", "phone", f"{c.phone}", "phone"),
            _class="table rows",
        ),
        Button("Save", type="submit"),
    )

    input_form = Form(contact_fields, action="/contacts/new", method="post")
    navigation = P(A("Back", href="/contacts"))

    return get_layout(input_form, navigation)


def get_show(c: Contact):
    contact_values = Div(Div(f"Phone: {c.phone}"), Div(f"Email: {c.email}"))
    a_edit = A("Edit", href=f"/contacts/{c.id}/edit")
    a_back = A("Back", href="/contacts")

    return get_layout(contact_values, P(a_edit, a_back), h1_str=f"{c.first} {c.last}")


def get_edit(c: Contact):
    contact_fields = Fieldset(
        Legend("Contact Values"),
        Div(
            get_contact_email_tag(c),
            get_contact_property_tag(
                c, "First Name", "first_name", f"{c.first}", "first"
            ),
            get_contact_property_tag(c, "Last Name", "last_name", f"{c.last}", "last"),
            get_contact_property_tag(c, "Phone", "phone", f"{c.phone}", "phone"),
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

    edit_form = Form(contact_fields, action=f"/contacts/{c.id}/edit", method="post")
    navigation = P(A("Back", href="/contacts"))

    return get_layout(edit_form, navigation)


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
                ),  # if "/update" is not used as in web4 / web5 etc this yields a 404 *shrug*
                id=_id,
                hx_target="this",
                hx_swap="outerHTML",
            )
        case _:
            raise NotImplementedError()
