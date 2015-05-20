SPLIT_CHAR = '%%'

class TextSplit():
    def __init__(self, font):
        """
        Split up the description into a list of lines of the correct width.

        description - the description to split up.
        """
        #TODO - maybe move out of class to a module function?
       
        self.box_width = 196 #TODO - make a formatting constant
        self.font = font

    def process(self, description):

        # first split up description into words
        word = ""
        words = []
        for char in description:
           if char != " ":
              word += char
           elif char == " ":
              words.append(word)
              word = ""
        else:
           words.append(word)

        # then figure out how long each word is (in pixels)
        word_lens = []
        for word in words:
           word_lens.append(self.font.calcWidth(word))
        space_len = self.font.calcWidth(" ")

        # iterate through the words adding them until they get too long, then send them to sentance and repeat til all words are done
        s_length = 0   # length of currently being formed line
        num_words = len(words)
        lines = []
        sentance = ""
        for curr in range(0,  num_words):
            curr_length = word_lens[curr]
            if words[curr] == SPLIT_CHAR:
                lines.append(sentance)
                s_length = curr_length + space_len
                sentance = ""
            else:
                if s_length + curr_length + space_len <= self.box_width:
                    sentance = sentance + words[curr] + " "
                    s_length += curr_length + space_len
                else:
                    lines.append(sentance)
                    s_length = curr_length + space_len
                    sentance = words[curr] + " "
        lines.append(sentance)
        return lines
