from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    session,
)

import pandas as pd

app = Flask(__name__)

car = pd.read_csv("car_data.csv", sep=",", encoding="utf-8")
car_df = pd.DataFrame(car)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        selected_categories = request.form.getlist("category")
        selected_areas = request.form.getlist("area")
        selected_colors = request.form.getlist("color")
        # min_price = request.form.get("min_price", "")
        # max_price = request.form.get("max_price", "")
        # start_year = request.form.get("start_year", "")
        # end_year = request.form.get("end_year", "")
        filter_df = car_df

        if selected_categories and selected_areas and selected_colors:
            filter_df = filter_df[
                (filter_df["모델명"].str.contains("|".join(selected_categories)))
                & (filter_df["지역"].str.contains("|".join(selected_areas)))
                & (filter_df["색상"].str.contains("|".join(selected_colors)))
            ]

        return render_template("home.html", data=filter_df.to_dict(orient="records"))
    return render_template("home.html", data=None)
