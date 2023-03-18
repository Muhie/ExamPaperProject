import sqlite3
import genanki
from sqlitehandler import SQLiteHandler
import re
from typing import List
def GetQuestionAndParts(SQLSocket: SQLiteHandler, questionid: str):
    """
    Gets the question and parts and formats them into
    proper formatting:
    (2017 component 1 a level)
    1. bla bla bla
    (a) (i) do this [4]
    """
    partsquery = f"""
    SELECT
    PartNumber,
    PartContents,
    PartMarks
    FROM Parts
    WHERE QuestionID = '{questionid}'
    ORDER BY PartNumber
    """
    partsdata = SQLSocket.queryDatabase(partsquery)
    questionquery = f"""
    SELECT
    QuestionNumber,
    QuestionContents,
    TotalMarks
    FROM Question
    WHERE QuestionID = '{questionid}'
    """
    questiondata = SQLSocket.queryDatabase(questionquery)[0]
    paperquery = f"""
    SELECT
    (PaperYear || '-' || PaperComponent ||
    '-' || PaperLevel || ' level')
    FROM Paper
    WHERE PaperID = (SELECT PaperID
    FROM Question WHERE QuestionID = '{questionid}')
    """
    paperdata = SQLSocket.queryDatabase(paperquery)
    questionstring = f"""
    {paperdata[0][0]}
    {questiondata[0]}. {questiondata[1]}
    """
    # if there are no parts then just add the total mark at the ned
    if not partsdata:
        questionstring += f" [{questiondata[2]}]"
        return questionstring

    questionstring += "\n"
    # else run through the parts
    for part in partsdata:
        partnum = GetReversedStringRepresentation(part[0])
        questionstring += f"{partnum} {part[1]} [{part[2]}]\n"


    return questionstring


def GetReversedStringRepresentation(partnumber: str) -> str:
    """
    Convert parts like 2bii to (b) (ii)
    """
    try:
        # get just the letters
        string = re.search(r"[^0-9]+", partnumber).group(0)
        # get the main letter e.g. b
        mainpart = re.search(r"[^iv]+", string)
        output = ""
        if mainpart:
            output = f"({mainpart.group(0)})"
        # sub part liek ii
        subpart = re.search(r"[iv]+", string)
        if subpart:
            output += f" ({subpart.group(0)})"
        return output
    except Exception as e:
        # used as there are still erorrs in the database
        # can be removed when these are fixed.
        print(e)
        print("Erroneous question part found: " + partnumber)


def GetAllQuestionsAndParts(sqlsocket: SQLiteHandler) -> List[str]:
    """
    Gets all the questions and parts, and outputs them as a list of strings
    """
    questionsquery = f"""
    SELECT QuestionID FROM Question
    """
    questions = [i[0] for i in sqlsocket.queryDatabase(questionsquery)]
    outputlist = []
    for question in questions:
        outputlist.append(
            GetQuestionAndParts(sqlsocket, question)
        )
    return outputlist


class Anki_card_model: #defining a model for a single card
    def __init__(self):
        self.my_model = genanki.Model(
        1607392319,
        'Simple Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ])
class Anki_converter(Anki_card_model):
    def __init__(self, path_to_database, name):
        super().__init__()
        self.db_path = path_to_database
        self.name = name
        self.my_deck = genanki.Deck(2059400110, self.name)

    def add_cards(self, questions, papers):
        front_list =  questions# put all of the questions here
        #back_list = [] #put all of the question numbers and from which paper
        print(self.db_path)
        print(len(front_list))
        for i in range(0,len(front_list)-1):
            string = "{}".format(front_list[i])
            my_note = genanki.Note(
            model=self.my_model,
            fields=[string, 'test'])
            self.my_deck.add_note(my_note)
    def create_deck(self):
        genanki.Package(self.my_deck).write_to_file(self.name)
        


if __name__ == '__main__':
    model = Anki_card_model()
    start = Anki_converter('database.sqlite', 'deck.apkg')
    start.add_cards(GetAllQuestionsAndParts(SQLiteHandler()))
    start.create_deck()

