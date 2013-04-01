import requests, re
from BeautifulSoup import BeautifulSoup

class OptionInfo(object):
    
    @staticmethod 
    def is_dash_option(option):
        return isinstance(option, basestring) and option.startswith('-') and not option.startswith('--')
    
    @staticmethod
    def is_dash_dash_option(option):
        return isinstance(option, basestring) and option.startswith('--')
    
    @staticmethod
    def is_possible_option(option):
        return OptionInfo.is_dash_dash_option(option) or OptionInfo.is_dash_option(option)
    
    @staticmethod
    def split_into_possible_options(options):
        # Regex for splitting out into possible options. Should tighten this up, and look at more manpages
        possible_options = re.split('\\n|\<|\>|,|/|\=|\[| ', options)  
        return_options = []
              
        for cur_option in possible_options:
            if OptionInfo.is_dash_dash_option(cur_option):
                return_options.append(cur_option)
            elif OptionInfo.is_dash_option(cur_option):
                # If its a dash option, we need to separate out grouped options
                return_options.extend(["-" + new_option for new_option in list(cur_option[1:])])
        
        return return_options
        

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
        
        # Find all <dt> elements whose text passes as a possible option
        matching_elements = doc.findAll(lambda tag : tag.name == 'dt' and OptionInfo.is_possible_option(tag.text))
        # Assume that actual options have an adjacent element with the description, if not, assume that it's not an option
        elements_with_siblings  = [ (element, element.nextSibling) for element in matching_elements if element.nextSibling]

        for (element, sibling_element) in elements_with_siblings:
            # Generate full text version of the option by joining all sub-elements
            option_text = "".join([str(part) for part in element.contents])
            # Generate full text version of the description
            option_description = "".join([str(part) for part in sibling_element.contents])
            # Store information for all possible permutations of the option
            for cur_option in OptionInfo.split_into_possible_options(option_text):
                self.option_to_description_map[cur_option] = (option_text, option_description)
    
    def normalized_result_for(self, option):
        return self.option_to_description_map.get(option,(option, "Argument Not Found"))