from shortened_word import SingleShortenedWord, CombinedShortenedWord


class Yuragi(SingleShortenedWord, CombinedShortenedWord):
    def generate(self):
        words = {}

        # サブタイトルとシリーズ番号を除去
        cleaned_text = self._clean_text(self.text)

        # wordsに追加する
        words['divided'] = self._make_divided_titles(self.text)
        words['unique_katakana'] = self._make_unique_katakana(cleaned_text)

        # 素性に分解する
        features = self._get_features(cleaned_text)
        words['combined'] = self._make_acronym_combination_words(features)

        self.words = words
        return self.words
