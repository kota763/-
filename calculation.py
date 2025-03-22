import pandas as pd
import ast

def calculate_weightedsum(weights, max_money=None, place=None, scene=None, taste=None, count=None):
    score_columns = ["food_rating", "service_rating", "atmosphere_rating"]

    df = pd.read_csv("./static/data/output_taste.csv")

    # 評価スコアを数値型に変換
    for col in score_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("点", "", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 価格の処理（NaNを0にする）
    if "price_max" in df.columns:
        df["price_max"] = df["price_max"].astype(str).str.replace("¥", "", regex=False).str.replace("円", "", regex=False).str.replace(",", "", regex=False)
        df["price_max"] = pd.to_numeric(df["price_max"], errors="coerce")
        df["price_max"] = df["price_max"].fillna(0)  # NaNを0に変換

    # photo_links の欠損値を空文字で埋める
    if "photo_links" in df.columns:
        df["photo_links"] = df["photo_links"].fillna("")

    # CSVに必要な列があるか確認
    missing_columns = [col for col in score_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"以下の列がCSVファイルに存在しません: {missing_columns}")

    # 重みを数値型に変換
    float_weights = {col: float(weights[col]) for col in score_columns}

    # 加重スコアを計算
    weighted_scores = df[score_columns].mul([float_weights[col] for col in score_columns], axis=1)
    df["weighted_sum"] = weighted_scores.sum(axis=1, skipna=True)

    # 予算フィルタリング（複数選択に対応）
    if max_money:
        if isinstance(max_money, str):  
            max_money = max_money.split(",")  # カンマ区切りの文字列をリストに変換

        if isinstance(max_money, list) and "all" not in max_money:
            try:
                max_money = [int(m) for m in max_money]  # 文字列を整数に変換
                df = df[df["price_max"].apply(lambda x: any(x <= budget and x > budget - 999 for budget in max_money))]
            except ValueError as e:
                print(f"数値変換エラー: {e}")


    # 場所フィルタリング
    if place and place != "all":
        df = df[df["place"] == place]

    # 利用シーンフィルタリング
    if scene and scene != "all":
        df["scene"] = df["scene"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)  # 文字列をリストに変換
        df = df[df["scene"].apply(lambda x: scene in x if isinstance(x, list) else False)]

    # 味フィルタリング
    if taste and taste != "all":
        df["taste"] = df["taste"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)  # 文字列をリストに変換
        df = df[df["taste"].apply(lambda x: taste in x if isinstance(x, list) else False)]

    # 結果が空なら False を返す
    if df.empty:
        return False

    # スコア順にソート
    sorted_df = df.sort_values(by="weighted_sum", ascending=False)

    store_name = []
    picture_url = []
    link_url = []
    price_range = []
    place_list = []

    total_count = sorted_df["weighted_sum"].count()
    if total_count - count < 10:
        end_index = total_count
    else:
        end_index = count + 10

    for i in range(count, end_index):
        pickup_row = sorted_df.iloc[i]

        store_name.append(pickup_row["store_name"])

        # `photo_links` のデータを `|` で分割し、リスト化
        photo_list = str(pickup_row["photo_links"]).split("|")

        # リスト内の各URLの前後の余白を削除
        photo_list = [photo.strip() for photo in photo_list]

        # `.jpg` または `.jpeg` の画像URLを取得
        jpeg_photos = [photo for photo in photo_list if ".jpg" in photo or ".jpeg" in photo]

        if jpeg_photos:
            picture_url.append(jpeg_photos[0])  # 最初のJPEG画像を取得
        else:
            picture_url.append("")  # JPEG画像がなければ空文字

        # IDをURLとして格納
        url = f"{pickup_row['store_id']}"
        link_url.append(url)

        # 価格範囲を格納
        price_range.append(pickup_row["price_range"])
        place_list.append(pickup_row["place"])

    result = {
        "store_name": store_name,
        "picture_url": picture_url,
        "link_url": link_url,
        "price_range": price_range,
        "place_list": place_list,
        "pickup_count": count,
        "len": total_count,
    }

    return result
