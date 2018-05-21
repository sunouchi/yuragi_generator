import re
import MeCab
import pprint
import utils
import jaconv

pp = pprint.PrettyPrinter(compact=True)

NEOLOGD_PATH = '/usr/local/lib/mecab/dic/mecab-ipadic-neologd'


class YuragiBase:
    def __init__(self):
        self.title = ''
        self.features = []


    def _get_features(self, text, use_neologd=False):
        '''
        素性を取得する
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
            if len(result) > 1: #EOSと空白は何もしない
                original_word = result[0]
                word_features = result[1].split(',')
                tmp = []
                tmp.append(original_word)
                tmp.extend(word_features)
                features.append(tmp)
        return features


    def _remove_noises_from_features(self, features_list):
        index_list = []
        for index, features in enumerate(features_list):
            if re.search('助詞|助動詞|記号', features[1]) or \
                features[2] == '非自立': #名詞と動詞の非自立
                index_list.append(index)
        if len(index_list) > 0:
            for i in sorted(index_list, reverse=True):
                features_list.pop(i)
        return features_list


    def _get_combined_titles(self, features_list):
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
                word_orig  = features_list[i][0]
                nword_orig = features_list[j][0]
                word  = features_list[i][0][:2] 
                nword = features_list[j][0][:2]
                # 語に漢字が含まれている場合、読み仮名をカタカナとひらがなで取得する。
                # MeCab素性に読み仮名が含まれている場合、len(features_list[x])が8以上になっている
                if (len(features_list[i])-1 >= 8) and features_list[i][-1] is not '*':
                    word_kata = features_list[i][-1][:2] 
                    word_hira = jaconv.kata2hira(word_kata)
                else:
                    word_kata = ''
                if (len(features_list[j])-1 >= 8) and features_list[j][-1] is not '*':
                    nword_kata = features_list[j][-1][:2] 
                    nword_hira = jaconv.kata2hira(nword_kata)
                else:
                    nword_kata = ''
                # ==================== ゆらぎ語の生成 ====================
                # 変換せずにそのままペアを作る
                tmp.append(word+nword)                 #例:兄貴困っ
                # 漢字の場合は1字のみのペアも作る
                if utils.is_kanji(word[0]):
                    tmp.append(word[0]+nword)          #例:兄困っ
                    if word_kata:
                        tmp.append(word_kata+nword)    #例:アニ困っ
                        tmp.append(word_kata+nword[0]) #例:アニ困
                        tmp.append(word_hira+nword)    #例:あに困っ
                        tmp.append(word_hira+nword[0]) #例:あに困
                if utils.is_kanji(nword[0]):
                    tmp.append(word+nword[0])          #例:兄貴困
                    if nword_kata:
                        tmp.append(word+nword_kata)    #例:兄貴コマ
                        tmp.append(word[0]+nword_kata) #例:兄コマ
                        tmp.append(word+nword_hira)    #例:兄貴こま
                        tmp.append(word[0]+nword_hira) #例:兄こま
                # if utils.is_kanji(word[0]) and utils.is_kanji(nword[0]):
                #     tmp.append(word[0]+nword[0])       #例:兄困
                if word_kata and len(word_kata)-1 >= 8:
                    tmp.append(word_kata+nword_kata)   #例:アニコマ
                    tmp.append(word_hira+nword_hira)   #例:あにこま

                # 読み仮名があった場合、アルファベットに変換する
                # 例: 9係 -> 9gakari
                word_kata_orig  = features_list[i][-1] if not word_kata  == '' else ''
                nword_kata_orig = features_list[j][-1] if not nword_kata == '' else '' 
                tmp.append(word      + utils.kana2romaji(nword_kata_orig))
                tmp.append(word_kata + utils.kana2romaji(nword_kata_orig))
                tmp.append(utils.kana2romaji(word_kata_orig) + nword)
                tmp.append(utils.kana2romaji(word_kata_orig) + nword_kata)
                tmp.append(utils.kana2romaji(word_kata_orig) + utils.kana2romaji(nword_kata_orig))

                result.extend(tmp)
        return result


    def _get_divided_titles(self, text):
        '''
        単語の分割によって、ゆらぎ語の候補を生成する

        〈例〉
        番組名「CRISIS 公安機動捜査隊特捜班」から、ゆらぎ語「CRISIS」を導き出したい。
        空白や記号などを区切りとして分割し、語のまとまりをゆらぎ語の候補として取り出す。
        In : 'CRISIS 公安機動捜査隊特捜班'
        Out: ['CRISIS']
        '''
        # 空白、句読点で分割する
        tmp = re.split('[\ |\u3000|,|.|、|。]', text)
        result = []
        for t in tmp:
            if len(t) < 8: #文字数の長い語はゆらぎ語として使われにくいので無視
                result.append(t)
        if '' in result: #空白の削除
            result.remove('')
        if len(result) > 0:
            return result
        else:
            return None


    def _remove_less_than_3letters(self, words):
        '''
        3字未満の語をリストから削除する
        '''
        if words is None: return words
        removed_words = []
        for word in words:
            if len(word) > 2:
                removed_words.append(word)
        return removed_words


    def generate(self, title, verbose=False):
        pass


    def _extract_subjects(self):
        '''
        主語の抽出
        主語の次に現れる助詞を見つけ、その一つ前にある語を主語として抽出する。
        '''
        words = []
        for index, features in enumerate(self.features):
            # MeCab出力フォーマットから必要な素性を取り出す
            word       = features[0] #表層形
            pos        = features[1] #品詞
            pos_detail = features[2] #品詞詳分類1
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
                prev_word = self.features[index-1][0]
                words.append(prev_word)
        return words


    def _extract_pronouns(self):
        '''
        代名詞の抽出
        '''
        words = []
        for features in self.features:
            if features[1] == '名詞' and features[2] == '代名詞':
                words.append(features[0])
        return words


    def _extract_proper_nouns(self):
        '''
        固有名詞の抽出
        '''
        words = []
        for features in self.features:
            if features[1] == '名詞' and features[2] == '固有名詞':
                words.append(features[0])
        return words


    def _extract_suffixies(self):
        '''
        接尾語の抽出
        '''
        words = []
        for features in self.features:
            if features[1] == '名詞' and features[2] == '接尾':
                words.append(features[0])
        return words 


    def _extract_significant_nums(self, text):
        '''
        特徴的な数字の抽出
        '''
        words = []
        all_features = self._get_features(text, use_neologd=False)
        for features in all_features:
            if features[1] == '名詞' and features[2] == '数':
                words.append(features[0])
        return words


    def _extract_unique_katakana(self, text):
        '''
        ユニークなカタカナの抽出
        '''
        words = []
        all_features = self._get_features(text, use_neologd=False)
        for features in all_features:
            is_katakana = True
            for letter in features[0]:
                if not utils.is_katakana(letter):
                    is_katakana = False
            if is_katakana:
                words.append(features[0])
        # カタカナ語がない場合、2つ以上あった場合は何も返さない
        if len(words) == 1:
            return words
        else:
            return None


    def _remove_subtitle(self, title):
        '''
        サブタイトルの除去

        「〜」で囲われた部分をサブタイトルと見なす
        ほかにもサブタイトルと判定できそうなルールが見つかったら、鋭意追加していく
        '''
        return re.sub('〜(.+)〜', '', title)


    def _remove_series(self, title):
        '''
        シリーズ番号の除去

        「シリーズ」「series」「シーズン」「season」
        ほかにもシリーズ番号と判定できそうなルールが見つかったら、鋭意追加していく
        '''
        words = re.split('[\ |\u3000]', title)
        for word in words:
            if re.search('シリーズ|series|シーズン|season', word.lower()):
                words.remove(word)
        return ''.join(words)


    def _remove_person_name(self, title):
        '''
        人名の除去

        未実装です。とりあえずこれ無しでも行けそうなので、後で余裕があれば実装する。
        '''
        return title


    def _remove_version_num(self, title):
        '''
        バージョン番号の除去

        未実装です。とりあえずこれ無しでも行けそうなので、後で余裕があれば実装する。
        '''
        return title


    def _remove_catchcopy(self, title):
        '''
        キャッチ文の除去

        未実装です。とりあえずこれ無しでも行けそうなので、後で余裕があれば実装する。
        '''
        return title


    def _remove_noises(self, title):
        '''
        小さいノイズ語の除去

        未実装です。とりあえずこれ無しでも行けそうなので、後で余裕があれば実装する。
        '''
        return title

        

class Yuragi(YuragiBase):
    def generate(self, title, verbose=False):
        '''
        ゆらぎ番組名を生成する
        '''
        self.title = title
        self.features = self._get_features(title, use_neologd=False)
        # サブタイトルとシリーズ番号を除去
        cleaned_title = self._remove_subtitle(self.title)
        cleaned_title = self._remove_series(cleaned_title)
        # 助詞、助動詞、記号、空白などを除去した素性を取得
        cleaned_features = self._get_features(cleaned_title)
        cleaned_features = self._remove_noises_from_features(cleaned_features)
        # ゆらぎ語番組名を作成
        titles = {
            'combined': self._get_combined_titles(cleaned_features),
            'divided' : self._get_divided_titles(self.title),
            'katakana': self._extract_unique_katakana(cleaned_title),
        }
        # 3字未満の語をリストから削除
        for key, value in titles.items():
            # value = self._remove_less_than_3letters(value)
            titles[key] = self._remove_less_than_3letters(value)
        # オプションでリストで取得したい場合の加工処理
        if with_one_dimension is True:
            tmp = []
            for key, value in titles.items():
                if value is not None: tmp.extend(value) #Noneをextendしようとするととエラーが出るから
            titles = set(tmp)
        return titles
