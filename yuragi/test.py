from shortened_word import SingleShortenedWord, CombinedShortenedWord
from yuragi import Yuragi

import pprint
pp = pprint.PrettyPrinter(indent=4)


def test_lazy(text, target_word, obj):
    debug = True
    words = obj.get_words()
    debug_words = obj.get_words(debug=debug)
    print('「{}」から「{}」をゆらぎ語として生成します:'.format(text, target_word))
    if target_word in words:
        print('OK')
    else:
        print("!!!FAILED!!!")
    print('ゆらぎ候補語:{}'.format(debug_words))
    print('\n')


def test_single(text, target_word):
    '''短縮語（単一語）のテスト
    '''
    single_word = SingleShortenedWord(text)
    single_word.generate()
    test_lazy(text, target_word, single_word)


def test_combined(text, target_word):
    '''短縮語（結合語）のテスト
    '''
    combined_word = CombinedShortenedWord(text)
    combined_word.generate()
    test_lazy(text, target_word, combined_word)


def test_yuragi(text, target_word):
    '''ゆらぎ語のテスト
    '''
    yuragi_word = Yuragi(text)
    yuragi_word.generate()
    test_lazy(text, target_word, yuragi_word)


def main():
    # # -------------------------------
    # # 単一語のテスト
    # # -------------------------------
    # # 単一語(分割)
    # test_single('CRISIS 公安機動捜査隊特捜班', 'CRISIS')
    # test_single('SRサイタマノラッパー~マイクの細道~', 'サイタマノラッパー')
    # test_single('中居正広のミになる図書館', 'ミになる図書館')
    # test_single('ファイナルファンタジーXIV　光のお父さん', '光のお父さん')
    # test_single('関ジャム　完全燃SHOW', '関ジャム')
    # # 単一語（分割して変換）
    # test_single('CRISIS 公安機動捜査隊特捜班', 'クライシス')
    # # 単一語（キャッチコピーを削除してそのまま）
    # test_single('1億人の大質問!?笑ってコラえて！', '笑ってコラえて')
    # # 単一語（主語をそのまま）
    # test_single('櫻子さんの足下には死体が埋まっている', '櫻子さん')
    # # 単一語（主語をそのまま）
    # test_single('警視庁捜査一課9係　season12', '9係')
    # # 単一語（カタカナ語をそのまま）
    # test_single('幸せ！ボンビーガール', 'ボンビーガール')
    # # 単一語（ノイズを除去して、カタカナ語をそのまま）
    # test_single('ユーリ!!! on ICE', 'ユーリ')
    # # 単一語（シリーズ名の除去）
    # test_single('進撃の巨人 Season 2」', '進撃の巨人')

    # # -------------------------------
    # # 結合語のテスト
    # # -------------------------------
    # # 結合語
    # # test_combined('マッサージ探偵　ジョー」', '探偵ジョー')  # 失敗する、カタカナ3字は非対応だから
    # test_combined('ボク、運命の人です。', 'ボク運')
    # test_combined('真夜中のプリンス', '真夜プリ')
    # test_combined('緊急取調室 第2シリーズ」', 'キントリ')
    # test_combined('中居正広の金曜日のスマイルたちへ」', '金スマ')
    # test_combined('この素晴らしい世界に祝福を！2」', 'このすば')
    # test_combined('あなたのことはそれほど」', 'あなそれ')
    # test_combined('ボク、運命の人です。」', 'ボク運')
    # test_combined('人は見た目が100パーセント」', 'ひとパー')
    # test_combined('恋がヘタでも生きてます」', '恋ヘタ')
    # test_combined('あなたのことはそれほど」', 'あなそれ')
    # test_combined('3人のパパ」', '3パパ')
    # test_combined('警視庁捜査一課9係　season12」', '9係')
    # # 結合語（分解して変換して結合）
    # test_combined('鋼の錬金術師', 'ハガレン')

    # -------------------------------
    # ゆらぎ候補語のテスト
    # -------------------------------
    # 単一語(分割)
    test_yuragi('ダンジョンに出会いを求めるのは間違っているだろうか', 'ダンまち')
    test_yuragi('Re：ゼロから始める異世界生活', 'リゼロ')
    test_yuragi('転生したらスライムだった件', '転スラ')


main()
