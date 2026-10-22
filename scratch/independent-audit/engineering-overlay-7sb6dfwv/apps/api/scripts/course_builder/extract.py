from html.parser import HTMLParser

class _Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in {"script","style","nav","footer"}: self.skip+=1
    def handle_endtag(self,tag):
        if tag in {"script","style","nav","footer"} and self.skip: self.skip-=1
    def handle_data(self,data):
        if not self.skip and data.strip(): self.parts.append(data.strip())
def extract_main_text(html:str)->str:
    parser=_Text(); parser.feed(html); return "\n".join(parser.parts)
