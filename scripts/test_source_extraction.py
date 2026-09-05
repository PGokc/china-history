import unittest
from fetch_sources import extract_biography
class ExtractionTests(unittest.TestCase):
 def test_primary_div_includes_inline_terms_excludes_glossary(self):
  biography='洪熙元年五月十二日去世。'*12
  html='<p>不属于本传的弹窗注释</p><div id="content_with_keyword">朱高炽<b>洪熙</b><br>'+biography+'<div>本传内层附记</div></div><p>更多注释</p>'
  text=extract_biography(html)
  self.assertIn(biography,text);self.assertIn('本传内层附记',text)
  self.assertNotIn('弹窗',text);self.assertNotIn('更多注释',text)
 def test_glossary_only_page_is_rejected(self):
  with self.assertRaises(ValueError):extract_biography('<p>'+'相关注释'*200+'</p>')
if __name__=='__main__':unittest.main()
