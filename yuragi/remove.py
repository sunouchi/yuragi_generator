import re


def remove_subtitle(text: str):
    '''サブタイトルを削除した、文字列を返す

    「〜」で囲われた部分をサブタイトルと見なす
    ほかにもサブタイトルと判定できそうなルールが見つかったら、鋭意追加していく
    '''
    return re.sub('〜(.+)〜', '', text)


def remove_series(text: str):
    '''シリーズ番号を削除した、文字列を返す

    一続きのシリーズであることを示す語を取り除く。
    例：
    - 「シリーズ」
    - 「series」
    - 「シーズン」
    - 「season」
    ほかにもシリーズ番号と判定できそうなルールが見つかったら、鋭意追加していく
    '''
    words = re.split('[\ |\u3000]', text)
    for word in words:
        if re.search('シリーズ|series|シーズン|season', word.lower()):
            words.remove(word)
    return ''.join(words)


def remove_person_name(text: str):
    '''人名を削除した、文字列を返す

    未実装。とりあえずこれ無しでも行けそうなので、後で余裕があれば実装する。
    '''
    return text


def remove_version_number(text: str):
    '''バージョン番号を削除した、文字列を返す

    未実装。とりあえずこれ無しでも行けそうなので、後で余裕があれば実装する。
    '''
    return text


def remove_catchcopy(text: str):
    '''キャッチコピーのような文字列を削除した、文字列を返す

    未実装。とりあえずこれ無しでも行けそうなので、後で余裕があれば実装する。
    '''
    return text


def remove_noise_words(features: list) -> list:
    '''ノイズと思われる語を削除した、リストを返す

    ノイズとは、短縮語として用いられないと思われる語のこと。
    例えば、
    - 助詞（は、が）
    - 助動詞（られる、たい）
    - 記号（！、。）
    - 非自立名詞（こと、もの）
    - 非自立動詞（ごらん、ちょうだい、しまう、ちゃう）
    など。
    '''
    cleaned_features = []
    for index, features in enumerate(features):
        if not re.search('助詞|助動詞|記号', features[1]) and \
                not features[2] == '非自立':  # 名詞と動詞の非自立
            cleaned_features.append(features)
    return cleaned_features
