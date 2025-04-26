from dataclasses import dataclass

from fasthtml.common import (
    FileResponse,
    HtmxHeaders,
    Link,
    Redirect,
    fast_app,
    picolink,
    serve,
)
from templates import get_archive_ui, get_edit, get_index, get_new, get_rows, get_show

import htmx_experiments.contact as htmx_contact
from htmx_experiments.archiver import Archiver
from htmx_experiments.contact import Contact

htmx_contact.PAGE_SIZE = 10  # Controls number of items in pagination
Contact.load_db()


@dataclass
class FormData:
    first_name: str
    last_name: str
    phone: str
    email: str


css = Link(rel="stylesheet", href="site.css", type="text/css")
app, rt = fast_app(hdrs=(picolink, css), static_path="./static")


@app.route("/")
def index():
    return Redirect("/contacts")


@app.route("/contacts", methods=["GET"])
def contacts(headers: HtmxHeaders, q: str | None = None, page: int | None = 0):
    search = q
    page = int(page) if page else 1

    if search is not None:
        print("searching")
        contacts_set = Contact.search(search)
        if headers.trigger_name == "q":
            return get_rows(contacts=contacts_set)
    else:
        print("using all")
        contacts_set = Contact.all(page)
    print(f"{len(contacts_set)=}")
    return get_index(contacts_set, search, page)


@app.route("/contacts/count")
def contacts_count():
    "`count` here to enable lazy loading, see https://hypermedia.systems/more-htmx-patterns/#_lazy_loading"
    count = Contact.count()
    return "(" + str(count) + " total Contacts)"


@app.route("/contacts/new", methods=["GET"])
def contacts_new_get():
    c = Contact()
    return get_new(c)


@app.route("/contacts/new", methods=["POST"])
def contacts_new(d: FormData):
    c = Contact(None, d.first_name, d.last_name, d.phone, d.email)

    if c.save():
        return Redirect("/contacts")
    else:
        return get_new(c)


@app.route("/contacts/{contact_id}", methods=["GET"])
def contacts_view(contact_id: int = 0):
    contact = Contact.find(contact_id)
    if contact is None:
        raise NotImplementedError(f"Tried to find non-existing {contact_id=}")
    return get_show(contact)


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


# Note: The routes for `archive_status` and `reset_archive` were extended relative to the web4 & web5 versions. If this is not done this causes 404 codes requesting /contacts/archive with GET / DELETE *shrug*


@app.route("/contacts/archive", methods=["POST"])
def start_archive():
    "Added to enable archive UI, see https://hypermedia.systems/a-dynamic-archive-ui/#_adding_the_archiving_endpoint"
    archiver = Archiver.get()
    archiver.run()
    return get_archive_ui(archiver)


@app.route("/contacts/archive/status", methods=["GET"])
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


@app.route("/contacts/archive/delete", methods=["DELETE"])
def reset_archive():
    "Added to enable cancellation of download in the archiver UI, see https://hypermedia.systems/a-dynamic-archive-ui/#_dismissing_the_download_ui"
    archiver = Archiver.get()
    archiver.reset()
    return get_archive_ui(archiver)


if __name__ == "__main__":
    serve(host="127.0.0.1", port=5006)
