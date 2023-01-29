from flask import Flask, Response
from webargs import fields
from webargs.flaskparser import use_args


from application.services.create_table import create_table
from application.services.db_connection import DBConnection

app = Flask(__name__)


@app.route("/")
def start():  # put application's code here
    return "<h1>phone book</h1>"


@app.route("/phone/create")
@use_args({"contact_name": fields.Str(required=True), "phone_value": fields.Str(required=True)}, location="query")
def users__create(args):
    with DBConnection() as connection:
        with connection:
            connection.execute(
                " INSERT INTO phones (contact_name, phone_value) VALUES (:contact_name, :phone_value);",
                {"contact_name": args["contact_name"], "phone_value": args["phone_value"]},
            )

    return "ok"


@app.route("/phone/get_all_phones")
def read_all_phones():
    with DBConnection() as connection:
        phones_ = connection.execute("SELECT * FROM phones;").fetchall()
    data = [f'{phone_["phone_id"]}: {phone_["contact_name"]} - {phone_["phone_value"]}' for phone_ in phones_]
    return "<br>".join(data)


@app.route("/phone/get_phone/<int:phone_id>")
def phone_read(phone_id: int):
    with DBConnection() as connection:
        phone_ = connection.execute(
            "SELECT * FROM phones WHERE (phone_id=:phone_id)",
            {
                "phone_id": phone_id,
            },
        ).fetchone()
    return f'{phone_["phone_id"]}: {phone_["contact_name"]} - {phone_["phone_value"]}'


@app.route("/phone/update/<int:phone_id>")
@use_args({"contact_name": fields.Str(), "phone_value": fields.Str()}, location="query")
def phone_update(args, phone_id: int):
    with DBConnection() as connection:
        with connection:
            phone_ = connection.execute(
                "SELECT * FROM phones WHERE (phone_id=:phone_id)",
                {
                    "phone_id": phone_id,
                },
            ).fetchone()
            print(phone_)
            if phone_ is None:
                return "no such id"
            contact_name = args.get("contact_name")
            phone_value = args.get("phone_value")
            if contact_name is None and phone_value is None:
                return Response(
                    "No arguments to change",
                    status=400,
                )

            args_for_request = []
            if contact_name is not None:
                args_for_request.append("contact_name=:contact_name")
            if phone_value is not None:
                args_for_request.append("phone_value=:phone_value")

            args_final = ", ".join(args_for_request)

            connection.execute(
                "UPDATE phones " f"SET {args_final} " "WHERE phone_id=:phone_id;",
                {
                    "phone_id": phone_id,
                    "contact_name": contact_name,
                    "phone_value": phone_value,
                },
            )

    return "Ok"


@app.route("/phone/delete/<int:phone_id>")
def phone_delete(phone_id: int):
    with DBConnection() as connection:
        with connection:
            connection.execute(
                "DELETE FROM phones WHERE (phone_id=:phone_id);",
                {
                    "phone_id": phone_id,
                },
            )

    return "Ok"


create_table()

if __name__ == "__main__":
    app.run()
