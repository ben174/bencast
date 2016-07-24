from feedgen.feed import FeedGenerator


class BencastFeedGenerator(FeedGenerator):

    def configure(self, title, prefix):
        self.prefix = prefix
        self.load_extension('podcast')
        self.podcast.itunes_category('Comedy')
        self.id(title.lower().replace(' ', '-'))
        self.title(title)
        self.author({'name': 'Ben', 'email': ''})
        self.link(href='http://www.bugben.com', rel='alternate')
        self.subtitle('Ben\'s personal podcast feed.')
        self.language('en')
        self.podcast.itunes_image('/static/' + prefix + '.jpg')
