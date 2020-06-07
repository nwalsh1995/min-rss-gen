import xml.etree.ElementTree
import functools
from typing import Optional, NewType, Iterable, Union, Generator

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


def add_subelement_with_text(
    parent: DEFAULT_ETREE.Element,
    child_tag: str,
    text: str,
    etree=DEFAULT_ETREE,
) -> DEFAULT_ETREE.SubElement:
    """
    Add a SubElement defined with `child_tag` and `text` to a `parent` node.

    :param parent: Node which will parent the newly created SubElement.
    :param child_tag: Tag to use for the SubElement.
    :param text: Text attribute to be set on the SubElement.
    :param etree: SubElement is created with `etree.SubElement`,
        intended for dependency injection.
    :return: Newly created SubElement attached to the parent node 
        with text attribute set.
    """
    sub = etree.SubElement(parent, child_tag)
    sub.text = text

    return sub


def gen_image(
    url: str,
    title: str,
    link: str,
    width: int = 88,
    height: int = 31,
    etree=DEFAULT_ETREE,
) -> ImageElement:
    """
    Validates and creates an `ImageElement`, a tag which should display
     an image for a channel.

    https://validator.w3.org/feed/docs/rss2.html#ltimagegtSubelementOfLtchannelgt

    :param url: URL of a GIF, JPEG or PNG image that represents the channel.
    :param title: describes the image, it's used in the ALT attribute of the
        HTML <img> tag when the channel is rendered in HTML
    :param link: URL of the site, when the channel is rendered,
        the image is a link to the site.
        (Note, in practice the image <title> and <link>
        should have the same value as the channel's <title> and <link>).
    :param width: Width of image in pixels.
        Maximum value for width is 144, default value is 88.
    :param height: Height of image in pixels.
        Maximum value for height is 400, default value is 31.
    :param etree: Element is created with `etree.Element`,
        intended for dependency injection.
    :return: The `etree.Element` for the newly created image.
    """
    image = etree.Element("image")

    add_to_image = functools.partial(
        add_subelement_with_text, etree=etree, root=image
    )

    kwargs = {
        "url": url,
        "title": title,
        "link": link,
    }

    if width is not None:
        width = min(width, MAX_IMAGE_WIDTH)
        kwargs["width"] = width

    if height is not None:
        height = min(height, MAX_IMAGE_HEIGHT)
        kwargs["height"] = height

    for child_tag, text in kwargs.items():
        add_to_image(child_tag, text)

    return ImageElement(image)


def gen_cloud(
    domain: str,
    port: int,
    path: str,
    registerProcedure: str,  # camelCase for equivalence with RSS docs
    protocol: str,
    etree=DEFAULT_ETREE,
) -> CloudElement:
    """
    Creates a `CloudElement`, a tag which allows processes
     to register with a cloud to be notified of updates to the channel,
     implementing a lightweight publish-subscribe protocol for RSS feeds.

    https://validator.w3.org/feed/docs/rss2.html#ltcloudgtSubelementOfLtchannelgt
    """
    return CloudElement(
        etree.Element(
            "cloud",
            domain=domain,
            port=str(port),
            path=path,
            registerProcedure=registerProcedure,
            protocol=protocol,
        )
    )


def gen_text_input(
    title: str, description: str, name: str, link: str, etree=DEFAULT_ETREE
) -> TextInputElement:
    """
    Validates and creates a `TextInputElement` which specifies
     a text input box that can be displayed with the channel.

    https://validator.w3.org/feed/docs/rss2.html#lttextinputgtSubelementOfLtchannelgt

    :param title: The label of the Submit button in the text input area.
    :param description: Explains the text input area. 
    :param name: The name of the text object in the text input area.
    :param link: The URL of the CGI script that processes text input requests.
    :param etree: Element is created with `etree.Element`,
        intended for dependency injection.
    """
    text_input = etree.Element("textInput")

    add_subelement_with_text_etree = functools.partial(
        add_subelement_with_text, etree=etree, root=text_input
    )

    add_subelement_with_text_etree("title", title)
    add_subelement_with_text_etree("description", description)
    add_subelement_with_text_etree("name", name)
    add_subelement_with_text_etree("link", link)

    return TextInputElement(text_input)


def gen_category(
    category: str, domain: Optional[str] = None, etree=DEFAULT_ETREE
) -> CategoryElement:
    """
    Validates and creates a `CategoryElement` which specifies
     one or more categories that the channel belongs to.

    https://validator.w3.org/feed/docs/rss2.html#ltcategorygtSubelementOfLtitemgt

    :param category: Value for the category node.
    :param domain: string that identifies a categorization taxonomy.
    :param etree: Element is created with `etree.Element`,
        intended for dependency injection.
    """
    element = etree.Element("category")

    if domain is not None:
        element.attrib["domain"] = domain

    element.text = category

    return CategoryElement(element)


def not_none(
    *elements: Iterable[Optional[DEFAULT_ETREE.Element]],
) -> Generator[DEFAULT_ETREE.Element, None, None]:
    """Yield back any ``element`` that is not None."""
    return (e for e in elements if e is not None)


def validate_either(*args, msg=None) -> None:
    """
    Ensures there is at least one arg that is not None.

    :raises ValueError: if all args are None.
    """
    if all(arg is None for arg in args):
        raise ValueError(msg)


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
    """
    Validates and creates an `ItemElement` which represents a "story".

    https://validator.w3.org/feed/docs/rss2.html#hrelementsOfLtitemgt

    :param title: The title of the item.
    :param link: The URL of the item.
    :param description: The item synopsis.
    :param author: Email address of the author of the item.
    :param category: Includes the item in one or more categories.
    :param comments: URL of a page for comments relating to the item.
    :param enclosure: Describes a media object that is attached to the item.
    :param guid: A string that uniquely identifies the item.
    :param pubDate: Indicates when the item was published.
    :param source: The RSS channel that the item came from.
    :param etree: Element is created with `etree.Element`,
        intended for dependency injection.
    """
    validate_either(
        title, description, msg="Either title or description must be set."
    )

    args = {k: v for k, v in locals().items() if v is not None}

    # Remove elements that we are handling specifically.
    args.pop("etree", None)

    item = etree.Element("item")

    # Category can be a string or CategoryElements, handle the latter case.
    # TODO: Collapse into 'add complex elements'
    if category is not None and type(category) is not str:
        item.extend(category)
        args.pop("category")

    # Add complex elements.
    item.extend(
        list(
            not_none(
                args.pop("enclosure", None),
                args.pop("guid", None),
                args.pop("source", None),
            )
        )
    )

    add_subelement_with_text_etree = functools.partial(
        add_subelement_with_text, etree=etree, root=item
    )

    for tag_name, tag_value in args.items():
        add_subelement_with_text_etree(tag_name, tag_value)

    return ItemElement(item)


def gen_guid(
    guid: str, isPermaLink: bool = True, etree=DEFAULT_ETREE
) -> GUIDElement:
    """
    Creates a `GUIDElement` which an aggregator may choose to use
     to determine if an item is new.

    https://validator.w3.org/feed/docs/rss2.html#ltguidgtSubelementOfLtitemgt

    :param guid: String that uniquely identifies the item.
    :param isPermaLink: If its value is false, the guid may not be assumed
        to be a url, or a url to anything in particular. Default: True.
    :param etree: Element is created with `etree.Element`,
        intended for dependency injection.
    """
    return GUIDElement(etree.Element(guid, isPermaLink=isPermaLink))


def gen_enclosure(
    url: str, length: int, type: str, etree=DEFAULT_ETREE
) -> EnclosureElement:
    """
    Creates a `EnclosureElement` which describes a media object that
     is attached to the item.

    https://validator.w3.org/feed/docs/rss2.html#ltenclosuregtSubelementOfLtitemgt

    :param url: says where the enclosure is located, must be HTTP.
    :param length: how big it is in bytes.
    :param type: what its type is, a standard MIME type.
    :param etree: Element is created with `etree.Element`,
        intended for dependency injection.
    """
    return EnclosureElement(
        etree.Element("enclosure", url=url, length=str(length), type=type)
    )


def gen_source(text: str, url: str, etree=DEFAULT_ETREE) -> SourceElement:
    """
    Creates a `SourceElement` which specifies the RSS channel
     that the item came from.

    https://validator.w3.org/feed/docs/rss2.html#ltsourcegtSubelementOfLtitemgt

    :param text: name of the RSS channel that the item came from,
        derived from its title.
    :param url: link to the XMLization of the source.
    :param etree: Element is created with `etree.Element`,
        intended for dependency injection.
    """
    source = etree.Element("source", url=url)
    source.text = text

    return SourceElement(source)


def gen_rss(
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
    """
    Validate and create an `rss` parent element and creates the channel.

    https://validator.w3.org/feed/docs/rss2.html#requiredChannelElements

    :param title: The name of the channel.
        It's how people refer to your service.
    :param link: The URL to the HTML website corresponding to the channel.
    :param description: Phrase or sentence describing the channel.
    :param language: The language the channel is written in.
    :param copyright: Copyright notice for content in the channel.
    :param managingEditor: Email address for person responsible
        for editorial content.
    :param webMaster: Email address for person responsible for technical issues
        relating to channel.
    :param pubDate: The publication date for the content in the channel.
    :param lastBuildDate: The last time the content of the channel changed.
    :param category: Specify one or more categories that the channel belongs to.
    :param generator: A string indicating the program used
        to generate the channel.
    :param docs: A URL that points to the documentation
        for the format used in the RSS file.
    :param cloud: A `CloudElement` to apply.
    :param ttl: number of minutes that indicates how long a channel
        can be cached before refreshing from the source.
    :param image: An `ImageElement` to apply.
    :param textInput: An `TextInputElement` to apply.
    :param skipHours: A hint for aggregators telling them which hours
        they can skip.
    :param skipDays: A hint for aggregators telling them which days
        they can skip.
    :param items: An iterable of `ItemElement`s to be added onto the channel.
    :param etree: Element is created with `etree.Element`,
        intended for dependency injection.

    :return: Parent <rss> element.
    """

    if ttl is not None:
        ttl = str(ttl)  # type: ignore

    args = {k: v for k, v in locals().items() if v is not None}

    # Remove elements that we are handling specifically.
    args.pop("etree", None)
    args.pop("items", None)

    rss = etree.Element("rss", version="2.0")
    channel = etree.SubElement(rss, "channel")

    # Add the 'complex' subelements.
    channel.extend(
        list(
            not_none(
                args.pop("cloud", None),
                args.pop("textInput", None),
                args.pop("image", None),
            )
        )
    )

    # Add required subelements.
    add_subelement_with_text_etree = functools.partial(
        add_subelement_with_text, etree=etree, root=channel
    )

    # Add any other optional fields that were passed as subelements.
    for child_tag, text in args:
        add_subelement_with_text_etree(child_tag, text)

    if items is not None:
        channel.extend(items)

    return rss
