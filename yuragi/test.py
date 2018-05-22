from shortened_word import ShortenedWordLazy, SingleShortenedWord, CombinedShortenedWord


def test_single(text, yuragi_word):
    single_word = SingleShortenedWord(text)
    single_word.generate()
    words = single_word.get_words()
    print('「{}」から「{}」をゆらぎ語として生成します:'.format(text, yuragi_word))
    if yuragi_word in words:
        print('OK')
        print('ゆらぎ候補語:{}'.format(single_word.get_words(debug=True)))
    else:
        print("!!!FAILED!!!")
        print('ゆらぎ候補語:{}'.format(single_word.get_words(debug=True)))
        #raise Exception
    print('\n')
    

def main():
    # 単一語(分割)
    test_single('CRISIS 公安機動捜査隊特捜班', 'CRISIS')
    test_single('SRサイタマノラッパー~マイクの細道~', 'サイタマノラッパー')
    test_single('中居正広のミになる図書館', 'ミになる図書館')
    # 単一語（分割して変換）
    test_single('CRISIS 公安機動捜査隊特捜班', 'クライシス')
    # 単一語（キャッチコピーを削除してそのまま）
    test_single('1億人の大質問!?笑ってコラえて！', '笑ってコラえて')
    # 単一語（主語をそのまま）
    test_single('櫻子さんの足下には死体が埋まっている', '櫻子さん')
    # 単一語（主語をそのまま）
    test_single('警視庁捜査一課9係　season12', '9係')
    # 単一語（カタカナ語をそのまま）
    test_single('幸せ！ボンビーガール', 'ボンビーガール')
    # 単一語（ノイズを除去して、カタカナ語をそのまま）
    test_single('ユーリ!!! on ICE', 'ユーリ')


main()
