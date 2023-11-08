from lxml import html

tree = html.parse("test.html")

for component in tree.xpath("//div[@class='template-components__group']"):
    print(component.text_content().replace(" ", "").replace("\n", ""))