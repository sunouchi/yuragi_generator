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


    def _get_combined_titles(self, features_list):


    def generate(self, title, verbose=False):
        pass


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
