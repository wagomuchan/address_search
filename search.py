import re
import sys
import requests


def main():
    # 1. 標準入力から1行取得（前後の余計な空白を削除）
    user_input = sys.stdin.readline().strip()

    # 2. 正規表現で「3桁、ハイフン（任意）、4桁」の郵便番号らしきものを抽出
    # (\d{3}) と (\d{4}) で数字のみをグループとしてキャプチャします
    match = re.search(r"(\d{3})-?(\d{4})", user_input)

    if not match:
        print(
            "Error: 郵便番号の形式（3桁-4桁、または7桁数字）が正しくありません。",
            file=sys.stderr,
        )
        sys.exit(1)

    # ハイフンを除外した「7桁の数字」を結合して作成
    zipcode = match.group(1) + match.group(2)

    # 3. 郵便番号検索API（zipcloud）の仕様に合わせてリクエスト
    url = "https://zipcloud.ibsnet.co.jp/api/search"
    params = {"zipcode": zipcode}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTPステータスコードが200以外なら例外を投げる

        # JSON形式のレスポンスをPythonの辞書型に変換
        data = response.json()

        # 4. APIの結果を検証して標準出力
        if data["results"]:
            # 住所が一意に定まるため、結果リストの先頭（[0]）を取得
            result = data["results"][0]

            state = result["address1"]  # 都道府県
            city = result["address2"]  # 市区町村
            town = result["address3"]  # 町域名

            # 指定のフォーマット {state}{city}{town} で標準出力
            print(f"{state}{city}{town}")
        else:
            print(
                f"Error: 郵便番号「{zipcode}」に該当する住所がありませんでした。",
                file=sys.stderr,
            )
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Communication Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()