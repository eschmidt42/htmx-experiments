"Based on Contact.app described in https://hypermedia.systems/a-web-1-0-application/ available here https://github.com/bigskysoftware/contact-app"

from flask import Flask, flash, jsonify, redirect, render_template, request, send_file

import htmx_experiments.contact as htmx_contact
from htmx_experiments.archiver import Archiver
from htmx_experiments.contact import Contact

htmx_contact.PAGE_SIZE = 10  # Controls number of items in pagination

Contact.load_db()
app = Flask(__name__)
app.secret_key = b"hypermedia rocks"


@app.route("/")
def index():
    return redirect("/contacts")


@app.route("/contacts", methods=["GET"])
def contacts():
    search = request.args.get("q")
    # `page` related changes to enable paging, see https://hypermedia.systems/htmx-patterns/#_another_application_improvement_paging
    page = int(request.args.get("page", 1))
    if search is not None:
        contacts_set = Contact.search(search)
        # send smaller html if search trigger, see https://hypermedia.systems/more-htmx-patterns/#_http_request_headers_in_htmx and https://hypermedia.systems/more-htmx-patterns/#_using_our_new_template
        if request.headers.get("HX-Trigger") == "search":
            return render_template("rows.html", contacts=contacts_set)
    else:
        contacts_set = Contact.all(page)
    return render_template(
        "index.html", contacts=contacts_set, page=page, archiver=Archiver.get()
    )  # for archiver part see https://hypermedia.systems/a-dynamic-archive-ui/#_conditionally_rendering_a_progress_ui


@app.route("/contacts/", methods=["DELETE"])
def contacts_delete_all():
    "Bulk delete, see https://hypermedia.systems/more-htmx-patterns/#_the_server_side_for_delete_selected_contacts"
    contact_ids = [int(id) for id in request.args.getlist("selected_contact_ids")]
    page = int(request.args.get("page", 1))
    for contact_id in contact_ids:
        c = Contact.find(contact_id)
        if c is None:
            raise NotImplementedError(f"Tried to find non-existing {contact_id=}")
        c.delete()
    flash("Deleted Contacts!")
    contacts_set = Contact.all()
    return render_template(
        "index.html", contacts=contacts_set, page=page, archiver=Archiver.get()
    )  # for archiver part see https://hypermedia.systems/a-dynamic-archive-ui/#_conditionally_rendering_a_progress_ui


@app.route("/contacts/count")
def contacts_count():
    "`count` here to enable lazy loading, see https://hypermedia.systems/more-htmx-patterns/#_lazy_loading"
    count = Contact.count()
    return "(" + str(count) + " total Contacts)"


@app.route("/contacts/new", methods=["GET"])
def contacts_new_get():
    return render_template(
        "new.html", contact=Contact()
    )  # TODO: why are new contacts initialized with _id=None here and below?


@app.route("/contacts/new", methods=["POST"])
def contacts_new():
    c = Contact(
        None,
        request.form["first_name"],
        request.form["last_name"],
        request.form["phone"],
        request.form["email"],
    )

    if c.save():
        flash("Created New Contact!")
        return redirect("/contacts")
    else:
        return render_template("new.html", contact=c)


@app.route("/contacts/<contact_id>", methods=["GET"])
def contacts_view(contact_id=0):
    contact = Contact.find(contact_id)
    return render_template("show.html", contact=contact)


@app.route("/contacts/<contact_id>/edit", methods=["GET"])
def contacts_edit_get(contact_id=0):
    contact = Contact.find(contact_id)
    return render_template("edit.html", contact=contact)


@app.route("/contacts/<contact_id>/edit", methods=["POST"])
def contacts_edit_post(contact_id=0):
    c = Contact.find(contact_id)
    if c is None:
        raise NotImplementedError(f"Tried to find non-existing {contact_id=}")
    c.update(
        request.form["first_name"],
        request.form["last_name"],
        request.form["phone"],
        request.form["email"],
    )
    if c.save():
        flash("Updated Contact!")
        return redirect("/contacts/" + str(contact_id))
    else:
        return render_template("edit.html", contact=c)


@app.route("/contacts/<contact_id>/email", methods=["GET"])
def contacts_email_get(contact_id=0):
    "Validating e-mails server side, see https://hypermedia.systems/htmx-patterns/#_validating_emails_server_side"
    c = Contact.find(contact_id)
    if c is None:
        raise NotImplementedError(f"Tried to find non-existing {contact_id=}")
    c.email = request.args.get("email")
    c.validate()
    return c.errors.get("email") or ""


@app.route("/contacts/<contact_id>", methods=["DELETE"])
def contacts_delete(contact_id=0):
    c = Contact.find(contact_id)
    if c is None:
        raise NotImplementedError(f"Tried to find non-existing {contact_id=}")
    c.delete()
    # onl re-render page if delete comes from the edit page with buttin id delete-btn, see https://hypermedia.systems/more-htmx-patterns/#_updating_the_server_side
    if request.headers.get("HX-Trigger") == "delete-btn":
        flash("Deleted Contact!")
        return redirect(
            "/contacts", 303
        )  # 303 necessary, explanation here https://hypermedia.systems/htmx-patterns/#_a_response_code_gotcha
    else:
        return ""


@app.route("/contacts/archive", methods=["POST"])
def start_archive():
    "Added to enable archive UI, see https://hypermedia.systems/a-dynamic-archive-ui/#_adding_the_archiving_endpoint"
    archiver = Archiver.get()
    archiver.run()
    return render_template("archive_ui.html", archiver=archiver)


@app.route("/contacts/archive", methods=["GET"])
def archive_status():
    "Added to enable archive UI polling status update, see https://hypermedia.systems/a-dynamic-archive-ui/#_adding_the_progress_bar_ui"
    archiver = Archiver.get()
    return render_template("archive_ui.html", archiver=archiver)


@app.route("/contacts/archive/file", methods=["GET"])
def archive_content():
    "Added to enable file download in the archiver UI, see https://hypermedia.systems/a-dynamic-archive-ui/#_downloading_the_result"
    manager = Archiver.get()
    return send_file(manager.archive_file(), "archive.json", as_attachment=True)


@app.route("/contacts/archive", methods=["DELETE"])
def reset_archive():
    "Added to enable cancellation of download in the archiver UI, see https://hypermedia.systems/a-dynamic-archive-ui/#_dismissing_the_download_ui"
    archiver = Archiver.get()
    archiver.reset()
    return render_template("archive_ui.html", archiver=archiver)


# JSON Data API


@app.route("/api/v1/contacts", methods=["GET"])
def json_contacts():
    "Enables JSON data download api, see https://hypermedia.systems/json-data-apis/#our-first-json-endpoint--listing-all-contacts"
    contacts_set = Contact.all()
    contacts_dicts = [c.__dict__ for c in contacts_set]
    return {"contacts": contacts_dicts}


@app.route("/api/v1/contacts", methods=["POST"])
def json_contacts_new():
    "Enables JSON data upload, see https://hypermedia.systems/json-data-apis/#adding-contacts"
    c = Contact(
        None,
        request.form.get("first_name"),
        request.form.get("last_name"),
        request.form.get("phone"),
        request.form.get("email"),
    )
    if c.save():
        return c.__dict__
    else:
        return {"errors": c.errors}, 400


@app.route("/api/v1/contacts/<contact_id>", methods=["GET"])
def json_contacts_view(contact_id=0):
    "Enables JSON view of single contact, see https://hypermedia.systems/json-data-apis/#_viewing_contact_details"
    contact = Contact.find(contact_id)
    return contact.__dict__


@app.route("/api/v1/contacts/<contact_id>", methods=["PUT"])
def json_contacts_edit(contact_id):
    "Enables JSON editing of single contact, see https://hypermedia.systems/json-data-apis/#_updating_deleting_contacts"
    c = Contact.find(contact_id)
    if c is None:
        raise NotImplementedError(f"Tried to find non-existing {contact_id=}")
    c.update(
        request.form["first_name"],
        request.form["last_name"],
        request.form["phone"],
        request.form["email"],
    )
    if c.save():
        return c.__dict__
    else:
        return {"errors": c.errors}, 400


@app.route("/api/v1/contacts/<contact_id>", methods=["DELETE"])
def json_contacts_delete(contact_id=0):
    "Enables JSON deletion of single contact, see https://hypermedia.systems/json-data-apis/#_updating_deleting_contacts"
    c = Contact.find(contact_id)
    if c is None:
        raise NotImplementedError(f"Tried to find non-existing {contact_id=}")
    c.delete()
    return jsonify({"success": True})
