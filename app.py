from flask import Flask, render_template, request, redirect, url_for, session
from calculation import calculate_weightedsum
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"  # セッションデータ暗号化用のキー
app.config["SESSION_TYPE"] = "filesystem"  # セッションデータをファイルに保存
Session(app)
"""
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "session:"
app.config["SESSION_REDIS"] = Redis(
    host="your_redis_host", port=6379, password="your_password"
)
Session(app)
"""
"""#これを試したい
app.config["SECRET_KEY"] = "your_secret_key"  # セッションデータ暗号化用のキー
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")  # Redisクライアントを作成
redis_client = Redis.from_url(redis_url)  # Flask-Sessionの設定
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis_client
Session(app)
"""

@app.route("/")
def index():
    session["click_count"] = 0
    return render_template("index.html")


# --------------------------------------#
@app.route("/calc", methods=["GET", "POST"])
def calculation():
    if request.method == "GET":
        session["click_count"] = 0
        return render_template("calculation.html")
    elif request.method == "POST":
        session["click_count"] = 0
        food_rank = request.form["food_rank"]
        service_rank = request.form["service_rank"]
        atmosphere_rank = request.form["atmosphere_rank"]

        money = request.form["money"]
        place = request.form["place"]
        scene = request.form["scene"]
        taste = request.form["taste"]

        weights = {
            "food_rating": food_rank,
            "service_rating": service_rank,
            "atmosphere_rating": atmosphere_rank,
        }
        # 計算結果をセッションに保存
        session["weights"] = weights
        session["money"] = money
        session["place"] = place
        session["scene"] = scene
        session["taste"] = taste

        # /result にリダイレクト
        return redirect(url_for("result"))


# --------------------------------------#
@app.route("/result")  # , methods=["GET", "POST"])
def result():
    session["click_count"] = 0

    weights = session.get("weights", {})
    money = session.get("money", "No result available")
    place = session.get("place", "No result available")
    scene = session.get("scene", "No result available")
    taste = session.get("taste", "No result available")

    output = calculate_weightedsum(
        weights, max_money=money, place=place, scene=scene, taste=taste, count=session["click_count"]
    )
    return render_template("result.html", output=output, count=session["click_count"])


# @app.route("/result_more", methods=["POST"])  # クリックして結果を更新
# def result_more():
#     # クリック数を増加
#     session["click_count"] += 10
#     count = session["click_count"]

#     weights = session.get("weights", {})
#     money = session.get("money", "No result available")
#     place = session.get("place", "No result available")

#     # 重み付き計算
#     output = calculate_weightedsum(weights, max_money=money, place=place, count=count)

#     # 結果を表示
#     return render_template("result.html", output=output, count=count)


# @app.route("/result_less", methods=["POST"])  # クリックして結果を更新
# def result_less():
#     # クリック数を増加
#     session["click_count"] -= 10
#     count = session["click_count"]

#     weights = session.get("weights", {})
#     money = session.get("money", "No result available")
#     place = session.get("place", "No result available")

#     # 重み付き計算
#     output = calculate_weightedsum(weights, max_money=money, place=place, count=count)

#     # 結果を表示
#     return render_template("result.html", output=output, count=count)


if __name__ == "__main__":
    app.run(debug=False)