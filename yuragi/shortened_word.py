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

    def _get_features(self, text, use_neologd=False):
        ''' 素性を取得する

        MeCabでデフォルト出力されるフォーマットは以下の通り。
        表層形\t品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,原形,読み,発音
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
            result.extend(word_list)
        return result


class SingleShortenedWord(ShortenedWordLazy):
    '''単一の語から成り立つ短縮語
    '''

    # def _make_removed_words(self):
    #     '''除去した語をそのままゆらぎ候補語として取り出す
    #     '''
    #     pass

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
        cleaned_text = remove_subtitle(self.text)
        cleaned_text = remove_series(cleaned_text)

        # wordsに追加する
        words['divided'] = self._make_divided_titles(self.text)
        words['unique_katakana'] = self._make_unique_katakana(cleaned_text)
        self.words = words
        return self.words


class CombinedShortenedWord(ShortenedWordLazy):
    '''複数の語を組み合わせて成立する短縮語
    '''
    # _tokens = {}

    def _clean_text(self):
        '''textをから余分な文字列を削除する
        '''
        pass

    def _tokenize_text(self):
        '''textを形態素に分解する
        '''
        pass

    def _remove_noise_from_tokens(self):
        '''形態素から、助詞や助動詞や記号など
        短縮語として用いられる可能性の低い語を除去する
        '''
        pass

    def _make_acronym_combination_wordss(self, features_list: dict):
        '''2単語の頭文字を組み合わせてゆらぎ候補語を作る
        このような短縮語を作るためのメソッド。

        例：ボク運（ボク、運命の人です）
            真夜プリ（真夜中のプリンス）
            ハガレン（鋼の錬金術師）

        ある語を、原形1字、原形2字、ひらがな2字、カタカナ2字の4パターンがあると想定し、
        2単語 * 4パターン の短縮語を作成する。
        '''

        '''
        単語の組み合わせによって、ゆらぎ語の候補を生成する

        MeCabから出力された素性リストをもとに、
        1字あるいは2字の頭字語を結びつけて短縮語のリストを作る。

        〈例〉
        番組名「ボク、運命の人です。」から、ゆらぎ語「ボク運」を導き出したい。
        「ボク運」を含んだ、短縮語と考えられる組み合わせのリストを作成する。
        In : 'ボク、運命の人です。'
        Out: ['ボク運命', 'ボク運', 'ボクウン', 'ボウン', 'ボクうん', 'ボうん', 'ボク人', 'ボク人', 'ボクヒト', 'ボヒト', 'ボクひと', 'ボひと', '運命人', '運人', 'ウン人', 'ウン人', 'うん人', 'うん人', '運命人', '運命ヒト', '運ヒト', '運命ひと', '運ひと', '運人']
        '''
        result = []
        for i, w in enumerate(features_list):
            for j in range(i+1, len(features_list)):
                tmp = []
                word = features_list[i][0][:2]
                nword = features_list[j][0][:2]
                # 語に漢字が含まれている場合、読み仮名をカタカナとひらがなで取得する。
                # MeCab素性に読み仮名が含まれている場合、len(features_list[x])が8以上になっている
                if (len(features_list[i])-1 >= 8) and \
                        features_list[i][-1] is not '*':
                    word_kata = features_list[i][-1][:2]
                    word_hira = jaconv.kata2hira(word_kata)
                else:
                    word_kata = ''
                if (len(features_list[j])-1 >= 8) and \
                        features_list[j][-1] is not '*':
                    nword_kata = features_list[j][-1][:2]
                    nword_hira = jaconv.kata2hira(nword_kata)
                else:
                    nword_kata = ''
                # ==================== ゆらぎ語の生成 ====================
                # 変換せずにそのままペアを作る
                tmp.append(word+nword)                  # 例:兄貴困っ
                # 漢字の場合は1字のみのペアも作る
                if utils.is_kanji(word[0]):
                    tmp.append(word[0]+nword)           # 例:兄困っ
                    if word_kata:
                        tmp.append(word_kata+nword)     # 例:アニ困っ
                        tmp.append(word_kata+nword[0])  # 例:アニ困
                        tmp.append(word_hira+nword)     # 例:あに困っ
                        tmp.append(word_hira+nword[0])  # 例:あに困
                if utils.is_kanji(nword[0]):
                    tmp.append(word+nword[0])           # 例:兄貴困
                    if nword_kata:
                        tmp.append(word+nword_kata)     # 例:兄貴コマ
                        tmp.append(word[0]+nword_kata)  # 例:兄コマ
                        tmp.append(word+nword_hira)     # 例:兄貴こま
                        tmp.append(word[0]+nword_hira)  # 例:兄こま
                # if utils.is_kanji(word[0]) and utils.is_kanji(nword[0]):
                #     tmp.append(word[0]+nword[0])       #例:兄困
                if word_kata and len(word_kata)-1 >= 8:
                    tmp.append(word_kata+nword_kata)   # 例:アニコマ
                    tmp.append(word_hira+nword_hira)   # 例:あにこま

                # 読み仮名があった場合、アルファベットに変換する
                # 例: 9係 -> 9gakari
                word_kata_orig = features_list[i][-1] if not word_kata == '' else ''
                nword_kata_orig = features_list[j][-1] if not nword_kata == '' else ''
                tmp.append(word + utils.kana2romaji(nword_kata_orig))
                tmp.append(word_kata + utils.kana2romaji(nword_kata_orig))
                tmp.append(utils.kana2romaji(word_kata_orig) + nword)
                tmp.append(utils.kana2romaji(word_kata_orig) + nword_kata)
                tmp.append(utils.kana2romaji(word_kata_orig) + utils.kana2romaji(nword_kata_orig))

                result.extend(tmp)
        return result

    def generate(self):
        pass
