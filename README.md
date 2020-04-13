# min-rss-gen
A minimal RSS 2.0 generator. Follows guidelines from https://validator.w3.org/feed/docs/rss2.html

# XML Implementations
Accepts any implementation that fulfills Python's ElementTree API. Due to this, `lxml` is supported. 

# Installation
```
pip install min-rss
```

# Usage

The following script powers the RSS feed at https://nwalsh1995.github.io/rss.xml

```python
from min_rss_gen.generator import start_rss, gen_item

import xml.etree.ElementTree
from glob import glob
from pathlib import PurePath

SITE = "https://nwalsh1995.github.io"
RSS_FILENAME = "rss.xml"
rss_items = []


# Generate all items
for f in glob("**/*.html", recursive=True):
    path = PurePath(f)
    title = path.with_suffix("").name.replace("-", " ").title()
    rss_items.append(gen_item(title=title, link=f"{SITE}/{str(path)}"))


# Generate the <rss> XML element and subelements.
rss_xml_element = start_rss(title="nwalsh1995.github.io", link="nwalsh1995.github.io", description="A collection of thoughts.", items=rss_items)

# You can add custom subelements onto the returned <rss> element if you choose.

with open(RSS_FILENAME, "wb") as f:
    f.write(xml.etree.ElementTree.tostring(rss_xml_element))
```
