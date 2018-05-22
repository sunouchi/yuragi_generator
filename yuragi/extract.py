import utils


def extract_subject(features: list):
    '''主語を取り出す

    主語の次に現れる助詞を見つけ、その一つ前にある語を主語として抽出する。
    '''
    words = []
    for index, features in enumerate(features):
        # MeCab出力フォーマットから必要な素性を取り出す
        word = features[0]  # 表層形
        pos = features[1]  # 品詞
        pos_detail = features[2]  # 品詞詳分類1
        # 主語のあとに来る「は」「が」を見つけようとしている
        # 「は」「が」は品詞が「助詞」であり、品詞詳分類1が「格助詞」「係助詞」であると考えられる
        #
        # e.g. 恋がヘタでも生きてます
        # [['恋', '名詞', '一般', '*', '*', '*', '*', '恋', 'コイ', 'コイ'],
        #  ['が', '助詞', '格助詞', '一般', '*', '*', '*', 'が', 'ガ', 'ガ'],
        #  ['ヘタ', '名詞', '一般', '*', '*', '*', '*', 'ヘタ', 'ヘタ', 'ヘタ'],
        #  ['で', '助詞', '格助詞', '一般', '*', '*', '*', 'で', 'デ', 'デ'],
        #  ['も', '助詞', '係助詞', '*', '*', '*', '*', 'も', 'モ', 'モ'],
        #  ['生き', '動詞', '自立', '*', '*', '一段', '連用形', '生きる', 'イキ', 'イキ'],
        #  ['て', '助詞', '接続助詞', '*', '*', '*', '*', 'て', 'テ', 'テ'],
        #  ['ます', '助動詞', '*', '*', '*', '特殊・マス', '基本形', 'ます', 'マス', 'マス']]
        # この場合、出力結果は ['恋']となる。
        if (word == 'は' or word == 'が') and \
                pos == '助詞' and \
                (pos_detail == '格助詞' or pos_detail == '係助詞'):
            prev_word = features[index-1][0]
            words.append(prev_word)
    return words


def extract_pronouns(features: list):
    '''代名詞を取り出す
    '''
    words = []
    for feature in features:
        if feature[1] == '名詞' and feature[2] == '代名詞':
            words.append(feature[0])
    return words


def extract_proper_nouns(features: list):
    '''固有名詞を取り出す
    '''
    words = []
    for feature in features:
        if feature[1] == '名詞' and feature[2] == '固有名詞':
            words.append(feature[0])
    return words


def extract_suffix(features: list):
    '''接尾語を取り出す
    '''
    words = []
    for feature in features:
        if feature[1] == '名詞' and feature[2] == '接尾':
            words.append(feature[0])
    return words


def extract_number(features: list):
    '''数字を取り出す
    '''
    words = []
    for feature in features:
        if feature[1] == '名詞' and feature[2] == '数':
            words.append(feature[0])
    return words
