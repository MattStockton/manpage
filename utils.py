import requests, re
from BeautifulSoup import BeautifulSoup

class FlagInfo(object):
    @staticmethod
    def is_possible_flag(flag):
        return isinstance(flag, basestring) and (flag.startswith('--') or flag.startswith('-'))
    
    @staticmethod
    def split_into_possible_flags(options):
        possible_flags = re.split(',|/|\=|\[| ',options)
        return [flag for flag in possible_flags if FlagInfo.is_possible_flag(flag)]

class ManPageRetriever(object):
    """A class to retrieve man page information"""
    ROOT_MANPAGE_URL = "http://linux.die.net/man/1/"
    
    def __init__(self, man_page):
        self.man_page = man_page
        self.option_to_description_map = {}
        self.is_error = False
        
    def run_retrieval(self):
        url = ManPageRetriever.ROOT_MANPAGE_URL + self.man_page
        req = requests.get(url)
        
        if req.status_code != 200:
            self.is_error = True
            return
        
        doc = BeautifulSoup(req.text)
        
        # Find all <dt> elements that start with posisble flags
        command_options_elements = doc.findAll(lambda tag : tag.name == 'dt' and FlagInfo.is_possible_flag(tag.text))
        # Assume that actual flags have an adjacent element with the description, if not, assume that it's not a flag
        # TODO MSS - Need to look into -m option for grep
        options_with_descriptions  = [ (element.text, element.nextSibling.contents) for element in command_options_elements if element.nextSibling]

        # Store all assumed permutations of the flag along with description
        for (option, description) in options_with_descriptions:
            for cur_option in FlagInfo.split_into_possible_flags(option):
                self.option_to_description_map[cur_option] = description
    
    def normalized_description_for(self, option):
        return "".join([str(html_element) for html_element in self.option_to_description_map.get(option,["Argument Not Found"])])