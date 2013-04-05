import re, os

class OptionInfo(object):
    """This helps to determine what options are passed to a command"""
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
    
    ROOT_MANPAGE_PATH = "tools/manpage_text/"
    CACHED_SUPPORTED_PAGES = None
    
    @staticmethod
    def get_supported_pages():
        if not ManPageRetriever.CACHED_SUPPORTED_PAGES:
            ManPageRetriever.CACHED_SUPPORTED_PAGES = \
                [filename[:-4] for filename in os.listdir(ManPageRetriever.ROOT_MANPAGE_PATH)]
        
        return ManPageRetriever.CACHED_SUPPORTED_PAGES       
    
    def __init__(self, man_page):
        self.man_page = man_page.strip()
        
        ''' A set of regular expressions to parse out the various formats of command line options
         in manpages. This is far from complete, and doesn't cover a lot of edge cases, still need 
         to tweak quite a bit '''
        self.start_of_option_match = re.compile('(^\s*-{1,2}[a-zA-Z]+)|(^\s*[a-zA-Z]\s+)')
        self.single_dash_option_match = re.compile('^\s*[^-](-[a-zA-Z])')
        self.double_dash_option_match = re.compile('^.*[/|\,]?\s{0,2}(--[a-zA-Z\-]+)')
        self.single_letter_option_match = re.compile('^\s*([a-zA-Z])\s+');
        
        self.option_descriptions = []
        self.options = []
        
    def supports_man_page(self):
        return os.path.exists(self._file_path())
    
    def _file_path(self):
        return ManPageRetriever.ROOT_MANPAGE_PATH + self.man_page + ".txt"
    
    def run_retrieval(self):        
        try:
            input_lines = [line for line in open(self._file_path())]
        except IOError:
            return

        self._split_into_options(input_lines)
        
    def _split_into_options(self, lines):
        num_lines = len(lines)
        cur_line_num = 0
      
        self.option_descriptions = []
        
        while cur_line_num < num_lines:
            cur_line = lines[cur_line_num]
            cur_line_num += 1
            
            # If this appears to be the start of an option, process it
            if self.start_of_option_match.match(cur_line):
                start_of_cur_option = cur_line
                new_option = [start_of_cur_option]
                self.option_descriptions.append(new_option)
                
                ''' Use indentation to determine when the option 'stops' (e.g. if a line is 
                less indented than the previous line, assume the option stops'''
                leading_spaces = len(start_of_cur_option) - len(start_of_cur_option.lstrip())
                
                while cur_line_num < num_lines:
                    cur_line = lines[cur_line_num]
                    cur_line_num += 1
                    leading_spaces_cur_line = len(cur_line) - len(cur_line.lstrip())
                    if(leading_spaces_cur_line > leading_spaces):
                        new_option.append(cur_line)
                    else:
                        cur_line_num -= 1
                        break
        
        # Parse out the options for each found option description
        for cur_option_description in self.option_descriptions:
            first_line = cur_option_description[0]
 
            new_option = []
            
            dash_match = re.match(self.single_dash_option_match, first_line)
            if dash_match:
                new_option.append(dash_match.group(1))
            dash_dash_match = re.match(self.double_dash_option_match, first_line)
            if dash_dash_match:
                new_option.append(dash_dash_match.group(1))
            single_letter_match = re.search(self.single_letter_option_match, first_line)
            if single_letter_match:
                new_option.append(single_letter_match.group(1))

            self.options.append(new_option)
                
    def normalized_result_for(self, option):
        for i in range(0, len(self.options)):
            option_group = self.options[i]
            for cur_option in option_group:
                if option.strip() == cur_option.strip():
                    return (option.strip(), "\n".join(self.option_descriptions[i]))
        
        
        return (option, "Argument Not Found")