#!/bin/env python

import unittest
import html_parser


class TestHtml(unittest.TestCase):

    def setUp(self):
        self.parser = html_parser.MyHTMLParser()
        self.maxDiff = 1024

    def test_parser_html_link_with_similar_text(self):
        html = '''<p>Катали с приятелем в двухдневный поход на выходных.
        Наснимал немножко видео и попробовал немножко помонтировать. Прошу смотреть и оценивать.<br>
        День первый: <a href="https://www.youtube.com/watch?v=Rma0SafnztU" rel="nofollow noopener noreferrer" target="_blank">youtube.com</a></p>
        <a href="https://juick.com/tag/%D0%B2%D0%B5%D0%BB%D0%BE" rel="nofollow noopener noreferrer" target="_blank">#вело</a>
        <a href="https://juick.com/tag/bike" rel="nofollow noopener noreferrer" target="_blank">#bike</a>'''
        
        self.parser.feed(html)
        self.parser.close()
        text = self.parser.get_result()
        sample_text = '''\nКатали с приятелем в двухдневный поход на выходных.        Наснимал немножко видео и попробовал немножко помонтировать. Прошу смотреть и оценивать.
        День первый: https://www.youtube.com/watch?v=Rma0SafnztU        #вело        #bike'''
        self.assertEqual(text, sample_text)

    def test_parser_html_link_as_tags(self):

        html = '''<p>Сегодня снова колесил <a href="https://mastodon.host/tags/%D0%BF%D0%BE%D0%BB%D1%81%D1%82%D0%B0" 
        class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>полста</span></a>. Дежурный маршрут: после дождей другое слишком рисковано.</p><p>Наконец начал методично работать над силой: только первый тягун преодолел на 22:28, а остальные — только на повышающих передачах (минимум 1,05).</p><p>Несмотря на обилие <a href="https://mastodon.host/tags/%D1%84%D0%BE%D1%82%D0%BE" class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>фото</span></a> остановок, средний темп более 22 км/ч.</p><p>Фото в комментариях.</p><p><span class="h-card"><a href="https://mastodon.ml/@rf" class="u-url mention" rel="nofollow noopener noreferrer" target="_blank">@<span>rf</span></a></span> <span class="h-card"><a href="https://mastodon.social/@russian_mastodon" class="u-url mention" rel="nofollow noopener noreferrer" target="_blank">@<span>russian_mastodon</span></a></span></p>'''
        
        sample_text = "\nСегодня снова колесил  #полста. Дежурный маршрут: после дождей другое слишком рисковано.\n" + \
            'Наконец начал методично работать над силой: только первый тягун преодолел на 22:28, а остальные — только на повышающих передачах (минимум 1,05).\n' + \
            'Несмотря на обилие  #фото остановок, средний темп более 22 км/ч.\nФото в комментариях.\n@rf  @russian_mastodon'
        
        self.parser.feed(html)
        self.parser.close()
        text = self.parser.get_result()
        self.assertEqual(text, sample_text)
    
    def test_parser_html_link_with_invisible_part(self):
        html = '<p>Я несколько лет не посещал этот сайт, с удивлением обнаружил, что он всё ещё жив и даже пополнился новыми фичами:</p><p>«Российский дзен. Бессмысленный и беспощадный».<br><a href="https://zenrus.ru/" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://</span><span class="">zenrus.ru/</span><span class="invisible"></span></a></p>'
        sample_text = '''\nЯ несколько лет не посещал этот сайт, с удивлением обнаружил, что он всё ещё жив и даже пополнился новыми фичами:\n«Российский дзен. Бессмысленный и беспощадный».\nhttps://zenrus.ru/'''
        self.parser.feed(html)
        self.parser.close()
        text = self.parser.get_result()
        self.assertEqual(text, sample_text)
        
    def test_parser_html_link_with_account(self):
        html = '@<span class=""><a href="https://mastodon.host/users/velociraptor" class="u-url mention" rel="nofollow noopener noreferrer" target="_blank"><span class="mention">velociraptor</span></a></span> ИМХО зря покрасили, лубок получился. Или это всегда так было?'
        sample_text = '@velociraptor ИМХО зря покрасили, лубок получился. Или это всегда так было?'
        self.parser.feed(html)
        self.parser.close()
        text = self.parser.get_result()
        self.assertEqual(text, sample_text)
            
    def test_parser_html_link_with_tag_and_account(self):
        html = '''Отдыхаете? Карантините помаленьку?<br><br>А мы пашем!!!<br><br>#<a href="https://friends.deko.cloud/search?tag=%D0%A2%D0%B0%D0%BA%D0%B8%D0%B5%D0%94%D0%B5%D0%BB%D0%B0" class="" rel="nofollow noopener noreferrer" target="_blank">ТакиеДела</a><p><span class="h-card"><a href="https://friends.deko.cloud/profile/shuro" class="u-url mention" rel="nofollow noopener noreferrer" target="_blank">@<span>shuro</span></a></span> Жму руку.</p>'''
        sample_text = 'Отдыхаете? Карантините помаленьку?\n\n' + \
            'А мы пашем!!!\n\n' + \
            '#ТакиеДела\n@shuro Жму руку.'
        self.parser.feed(html)
        self.parser.close()
        text = self.parser.get_result()
        self.assertEqual(text, sample_text)

    def test_parser_html_link_with_same_link_and_text(self):
        html = '''<p>Будет что послушать, иначе Aleckat &amp; Hynamo затеру до дыр. \n<a href="https://sound.skrep.in/library/albums/4" rel="nofollow noopener noreferrer" target="_blank"></a><a href="https://sound.skrep.in/library/albums/4" rel="nofollow noopener noreferrer" target="_blank">https://sound.skrep.in/library/albums/4</a>/</p>'''
        sample_text = '''\nБудет что послушать, иначе Aleckat & Hynamo затеру до дыр. https://sound.skrep.in/library/albums/4/'''
        self.parser.feed(html)
        self.parser.close()
        text = self.parser.get_result()
        self.assertEqual(text, sample_text)

    def test_parser_html_link_with_text_as_part_link(self):
        html = '<p>Малоизвестный рецепт о борьбе с депрессией</p><p><a href="https://youtu.be/_enjTduzNrE?is=JYEGiTISvLVR-zSr" rel="nofollow noopener" translate="no" target="_blank"><span class="invisible">https://</span><span class="ellipsis">youtu.be/_enjTduzNrE?is=JYEGiT</span><span class="invisible">ISvLVR-zSr</span></a></p>'
        sample_text = '''\nМалоизвестный рецепт о борьбе с депрессией\nhttps://youtu.be/_enjTduzNrE?is=JYEGiTISvLVR-zSr'''
        self.parser.feed(html)
        self.parser.close()
        text = self.parser.get_result()
        self.assertEqual(text, sample_text)

    def test_parser_html_link_with_meaning_text(self):
        html = '<p>тут ссылка на </p><p><a href="https://youtu.be/_enjTduzNrE?is=JYEGiTISvLVR-zSr" rel="nofollow noopener" translate="no" target="_blank"><span class="invisible">https://</span><span class="ellipsis">youtu.be/_enjTduzNrE?is=JYEGiT</span><span class="invisible">вот такое видео</span></a></p>'
        sample_text = '''\nтут ссылка на  \n[вот такое видео](https://youtu.be/_enjTduzNrE?is=JYEGiTISvLVR-zSr)'''
        self.parser.feed(html)
        self.parser.close()
        text = self.parser.get_result()
        self.assertEqual(text, sample_text)
