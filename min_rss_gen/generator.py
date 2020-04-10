import xml.etree.ElementTree
import copy
import functools
from typing import Optional, NewType, Iterable, Union

COMPLEX_ELEMENTS = ["cloud", "textInput", "image"]
DEFAULT_ETREE = xml.etree.ElementTree

ImageElement = NewType("ImageElement", DEFAULT_ETREE.Element)
CloudElement = NewType("CloudElement", DEFAULT_ETREE.Element)
TextInputElement = NewType("TextInputElement", DEFAULT_ETREE.Element)
ItemElement = NewType("ItemElement", DEFAULT_ETREE.Element)
EnclosureElement = NewType("EnclosureElement", DEFAULT_ETREE.Element)
GUIDElement = NewType("GUIDElement", DEFAULT_ETREE.Element)
SourceElement = NewType("SourceElement", DEFAULT_ETREE.Element)
CategoryElement = NewType("CategoryElement", DEFAULT_ETREE.Element)

MAX_IMAGE_WIDTH = 144
MAX_IMAGE_HEIGHT = 400


def add_subelement_with_text(root: DEFAULT_ETREE.Element, child_tag: str, text: str, etree=DEFAULT_ETREE) -> DEFAULT_ETREE.SubElement:
    sub = etree.SubElement(root, child_tag)
    sub.text = text

    return sub


def gen_image(url: str, title: str, link: str, width: Optional[int] = None, height: Optional[int] = None, etree=DEFAULT_ETREE) -> ImageElement:
    image = etree.Element("image")

    add_subelement_with_text_etree = functools.partial(add_subelement_with_text, etree=etree)

    add_subelement_with_text_etree(image, "url", url)
    add_subelement_with_text_etree(image, "title", title)
    add_subelement_with_text_etree(image, "link", link)

    if width is not None:
        if width > 144:
            raise ValueError(f"Max width {MAX_IMAGE_WIDTH}")

        add_subelement_with_text_etree(image, "width", str(width))

    if height is not None:
        add_subelement_with_text_etree(image, "height", str(height))

    return ImageElement(image)


def gen_cloud(domain: str, port: int, path: str, registerProcedure: str, protocol: str, etree=DEFAULT_ETREE) -> CloudElement:
    return CloudElement(etree.Element("cloud", domain=domain, port=str(port), path=path, registerProcedure=registerProcedure, protocol=protocol))


def gen_text_input(title: str, description: str, name: str, link: str, etree=DEFAULT_ETREE) -> TextInputElement:
    text_input = etree.Element("textInput")

    add_subelement_with_text_etree = functools.partial(add_subelement_with_text, etree=etree)

    add_subelement_with_text_etree(text_input, "title", title)
    add_subelement_with_text_etree(text_input, "description", description)
    add_subelement_with_text_etree(text_input, "name", name)
    add_subelement_with_text_etree(text_input, "link", link)

    return TextInputElement(text_input)


def gen_item(
    title: Optional[str] = None,
    link: Optional[str] = None,
    description: Optional[str] = None,
    author: Optional[str] = None,
    category: Union[Optional[str], Iterable[CategoryElement]] = None,
    comments: Optional[str] = None,
    enclosure: Optional[EnclosureElement] = None,
    guid: Optional[GUIDElement] = None,
    pubDate: Optional[str] = None,
    source: Optional[SourceElement] = None,
    etree=DEFAULT_ETREE,
) -> ItemElement:
    if title is None and description is None:
        raise ValueError("Either title or description must be set.")

    args = copy.copy(locals())

    # Remove elements that we are handling specifically.
    args.pop("etree")

    item = etree.Element("item")

    # Category can be a string or CategoryElements, handle the latter case.
    # TODO: Collapse into 'add complex elements'
    if category is not None and type(category) != str:
        for category_element in category:
            item.append(category_element)
        args.pop("category")

    # Add complex elements.
    for complex_element_name in ("enclosure", "guid", "source"):
        complex_element = args[complex_element_name]

        if complex_element is not None:
            item.append(complex_element)

        args.pop(complex_element_name)

    add_subelement_with_text_etree = functools.partial(add_subelement_with_text, etree=etree)
    for tag_name, tag_value in ((k, v) for k, v in args.items() if v is not None):
        add_subelement_with_text_etree(item, tag_name, tag_value)

    return ItemElement(item)


def gen_guid(guid: str, isPermaLink: bool = True, etree=DEFAULT_ETREE) -> GUIDElement:
    return GUIDElement(etree.Element(guid, isPermaLink=isPermaLink))


def gen_enclosure(url: str, length: int, type: str, etree=DEFAULT_ETREE) -> EnclosureElement:
    return EnclosureElement(etree.Element("enclosure", url=url, length=str(length), type=type))


def gen_source(text: str, url: str, etree=DEFAULT_ETREE) -> SourceElement:
    source = etree.Element("source", url=url)
    source.text = text

    return SourceElement(source)


# TODO: Gen source
# TODO: Gen category


def start_rss(
    title: str,
    link: str,
    description: str,
    etree=DEFAULT_ETREE,
    language: Optional[str] = None,
    copyright: Optional[str] = None,
    managingEditor: Optional[str] = None,
    webMaster: Optional[str] = None,
    pubDate: Optional[str] = None,
    lastBuildDate: Optional[str] = None,
    category: Optional[str] = None,
    generator: Optional[str] = None,
    docs: Optional[str] = None,
    cloud: Optional[CloudElement] = None,
    ttl: Optional[int] = None,
    image: Optional[ImageElement] = None,
    textInput: Optional[TextInputElement] = None,
    skipHours: Optional[str] = None,
    skipDays: Optional[str] = None,
    items: Optional[Iterable[ItemElement]] = None,
) -> DEFAULT_ETREE.Element:
    if ttl is not None:
        ttl = str(ttl)  # type: ignore

    args = copy.copy(locals())

    # Remove elements that we are handling specifically.
    args.pop("etree")
    args.pop("items")

    rss = etree.Element("rss", version="2.0")
    channel = etree.SubElement(rss, "channel")

    # Add the 'complex' subelements.
    for complex_element_type in COMPLEX_ELEMENTS:
        element = args[complex_element_type]
        if element is not None:
            channel.append(element)
        args.pop(complex_element_type)

    # Add required subelements.
    add_subelement_with_text_etree = functools.partial(add_subelement_with_text, etree=etree)
    add_subelement_with_text_etree(channel, "title", title)
    add_subelement_with_text_etree(channel, "link", link)
    add_subelement_with_text_etree(channel, "description", description)

    # Add any other optional fields that were passed as subelements.
    for optional_arg_title, optional_arg_value in ((k, v) for k, v in args.items() if v is not None):
        add_subelement_with_text_etree(channel, optional_arg_title, optional_arg_value)

    if items is not None:
        for item in items:
            channel.append(item)

    return rss


import lxml.etree  # noqa: E402

xml.etree.ElementTree.dump(
    start_rss(
        "my own title",
        "my link",
        "my description",
        ttl=60,
        image=gen_image(url="https://url.test/image.gif", title="image title", link="https://url.test/"),
        items=[gen_item(title="my item")],
    )
)
xml.etree.ElementTree.dump(start_rss("my own title", "my link", "my description", etree=lxml.etree))
