import re
import MeCab
import jaconv

import utils
from remove import (
    remove_subtitle,
    remove_series,
    remove_person_name,
    remove_version_number,
    remove_catchcopy,
    remove_noise_words
)

import pprint
pp = pprint.PrettyPrinter(compact=True)

NEOLOGD_PATH = '/usr/local/lib/mecab/dic/mecab-ipadic-neologd'


class ShortenedWordLazy:
    text = ''
    words = {}
    features = {}

    def __init__(self, text, *args, **kwargs):
        self.text = text
        self.features = self._get_features(text)
        pass

    def _clean_text(self, text):
        '''textをから余分な文字列を削除する
        '''
        text = remove_subtitle(text)
        text = remove_series(text)
        return text

    def _get_features(self, text, use_neologd=False):
        ''' 素性を取得する

        MeCabでデフォルト出力されるフォーマットは以下の通り。
        [表層形, 品詞, 品詞細分類1, 品詞細分類2, 品詞細分類3, 活用型, 活用形, 原形, 読み, 発音]
        via: http://taku910.github.io/mecab/#format
        '''
        if use_neologd:
            tagger = MeCab.Tagger(' --dicdir {0}'.format(NEOLOGD_PATH))
        else:
            tagger = MeCab.Tagger()
        results = tagger.parse(text).split('\n')
        features = []
        for result in results:
            result = result.split('\t')
            if len(result) > 1:  # EOSと空白は何もしない
                original_word = result[0]
                word_features = result[1].split(',')
                tmp = []
                tmp.append(original_word)
                tmp.extend(word_features)
                features.append(tmp)
        return features

    def _filter_gt_3chars(self, words: list):
        '''
        語のリストから3字以上の語リストを返す

        字数の少ない語はゆらぎ候補語から除外するため。
        2字以下の語は固有な意味を表現しづらいため、
        一般的に短縮語は3字以上の語になることが多いように思われる。
        最終的に生成されたゆらぎ候補語から、3字未満の語は削除する。
        '''
        min_char_length = 3
        if words is None:
            return None
        cleaned_words = []
        for word in words:
            if len(word) >= min_char_length:
                cleaned_words.append(word)
        return cleaned_words

    def generate(self):
        pass

    def get_words(self, debug=False):
        '''ゆらぎ候補語を取得する処理

        この処理は self.words の中身を返す。
        debug=False の場合はリストが返って来る。
        debug=True の場合は、生成パターン名をキーとした dict が返って来る。
        デバッグ中に意図したゆらぎ候補語が作成されない場合などは、
        debug=Trueにすると良い。

        self.generate() を実行すると、self.words にゆらぎ候補語が格納されるが、
        実行前は空のdictになっている。
        空のdictが返って来る場合は、 self.generate() を実行すると良いかもしれない。
        '''
        if debug is True:
            return self.words
        result = []
        for pattern_name, word_list in self.words.items():
            if word_list is not None:
                result.extend(word_list)
        return result


class SingleShortenedWord(ShortenedWordLazy):
    '''単一の語から成り立つ短縮語
    '''

    def _make_extracted_words(self):
        '''抽出した語をそのままゆらぎ候補語として取り出す
        '''
        pass

    def _make_divided_titles(self, text):
        '''分割した語をそのままゆらぎ候補語として取り出す

        〈例〉
        番組名「CRISIS 公安機動捜査隊特捜班」から、ゆらぎ語「CRISIS」を導き出したい。
        空白や記号などを区切りとして分割し、語のまとまりをゆらぎ語の候補として取り出す。
        In : 'CRISIS 公安機動捜査隊特捜班'
        Out: ['CRISIS']
        '''
        # 文字数の長い語は短縮語として使われにくいので無視
        max_char_length = 8
        # 空白、句読点で分割する
        tokens = re.split('[\ |\u3000|,|.|、|。]', text)
        result = []
        for token in tokens:
            if len(token) < max_char_length:
                result.append(token)
        if '' in result:  # 空白の削除
            result.remove('')
        return result

    def _extract_katakana(self, features: list):
        '''ユニークなカタカナ語を取り出す

        カタカナ語が一つだけある場合、短縮語として用いられるケースが見られる。
        2つ以上ある場合は特徴が薄くなるせいか、
        短縮語として用いられないことが多いように思われる。
        '''
        words = []
        for feature in features:
            is_katakana = True
            for letter in feature[0]:
                if not utils.is_katakana(letter):
                    is_katakana = False
            if is_katakana:
                words.append(feature[0])
        # カタカナ語がない場合、2つ以上あった場合は何も返さない
        return words
        if len(words) == 1:
            return words
        else:
            return []

    def _make_unique_katakana(self, text):
        '''抽出したユニークなカタカナによるゆらぎ候補語を作成する

        NEOLOGDを有効にした場合と、無効にした場合の
        2パターンの形態素セットでカタカナ語を作成する。
        '''
        result = []
        features = self._get_features(text, use_neologd=False)
        features_neologd = self._get_features(text, use_neologd=True)
        for f in [features, features_neologd]:
            katakana_list = self._extract_katakana(f)
            if len(katakana_list) == 1:
                result.extend(katakana_list)
        return result

    def generate(self):
        words = {}

        # サブタイトルとシリーズ番号を除去
        cleaned_text = self._clean_text(self.text)

        # wordsに追加する
        words['divided'] = self._make_divided_titles(self.text)
        words['unique_katakana'] = self._make_unique_katakana(cleaned_text)
        self.words = words
        return self.words


class CombinedShortenedWord(ShortenedWordLazy):
    '''複数の語を組み合わせて成立する短縮語
    '''
    # _tokens = {}

    def _tokenize_text(self):
        '''textを形態素に分解する
        '''
        pass

    def _remove_noise_from_tokens(self):
        '''形態素から、助詞や助動詞や記号など
        短縮語として用いられる可能性の低い語を除去する
        '''
        pass

    def _reflex(self, word_a: list, word_b: list):
        '''単語Aの語リストと、単語Bの語リストから、
        単語Aを先頭にした結合語を返す
        '''
        words = []
        for wa in word_a:
            for wb in word_b:
                words.append(wa + wb)
        return words

    def _make_acronym_combination_words(self, features_list: list):
        '''2単語の頭文字の組み合わせで構成される、ゆらぎ候補語を作り、リストで返す

        最終的にはこういう短縮語を求めることを目的としている。
        例：ボク運（ボク、運命の人です）
            真夜プリ（真夜中のプリンス）
            ハガレン（鋼の錬金術師）

        ある語を、表層形2字、表層形1字、カタカナ2字、ひらがな2字の4パターンがあると想定し、
        2単語 * 4パターン の短縮語を作成する。
        '''
        # 素性から助詞や助動詞など不要なワードを除去する
        features = remove_noise_words(features_list)

        # 素性から短縮語の素になる二次元配列を作る
        # 短縮語として用いられそうな語を、
        # 表層形2字、表層形1字、カタカナ2字、ひらがな2字の4種類ずつの
        # 配列を作る
        # 
        # 例：「ボク、運命の人です」の場合
        # [['ボク', 'ボ', 'ボク', 'ぼく']
        #  ['運命', '運', 'ウン', 'うん']
        #  ['人', '人', 'ヒト', 'ひと']]
        words_a = []
        for i, feature in enumerate(features):
            words_a.append([])
            words_a[i].append(feature[0][:2])  # 表層形2字
            words_a[i].append(feature[0][:1])  # 表層形1字
            words_a[i].append(feature[-1][:2])  # カタカナ2字
            words_a[i].append(jaconv.kata2hira(feature[-1][:2]))  # ひらがな2字

        # 短縮語の素を組み合わせて、結合語を作る
        # 総当たりで組み合わせた語のリストを作る
        # 単語Aが単語Bよりも先にくるもののみ作成する
        words_b = words_a
        combined_words = []
        for i, word_a in enumerate(words_a):
            for j, word_b in enumerate(words_b):
                if i < j:
                    combined_words.extend(self._reflex(word_a, word_b))                    

        # 重複をなくしてリストで返す
        return list(set(combined_words))

    def generate(self):
        words = {}

        # サブタイトルとシリーズ番号を除去
        cleaned_text = self._clean_text(self.text)

        # 素性に分解する
        features = self._get_features(cleaned_text)

        # wordsに追加する
        words['combined'] = self._make_acronym_combination_words(features)
        self.words = words
        return self.words

