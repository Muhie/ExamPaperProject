# save all PDFs in the PDFs folder to the database
from pdfreader import PDFReading
from sqlhandler import SQLHandler
from pathlib import Path
from sqlitehandler import SQLiteHandler

# SERVER = "DESKTOP-QG36584\SQLEXPRESS"
SERVER = "DANIELS-DELL\SQLEXPRESS"
DATABASE = "ExamQuestions"


def main():
    sqlsocket = SQLiteHandler()
    files = list((Path.cwd() / "pdfs").rglob('*.pdf'))
    for file in files:
        print("processing " + str(file))
        reader = PDFReading(file)
        questions = reader.questionspartsindex
        # add the header information for the paper first
        paperid = f"{reader.level}-{reader.component}-{reader.year}"
        headerquery = f"""INSERT INTO PAPER VALUES(
        '{paperid}',
        '{reader.component}',
        '{reader.year}',
        '{reader.level}'
        )"""
        sqlsocket.addToDatabase(headerquery)
        for question in questions:
            # create the SQL query
            questionobj = questions[question]
            questionid = paperid + str(questionobj.number)
            totalmarks = questionobj.marks + sum(
                i.marks for i in questionobj.parts)
            # first add the question itself
            questioninsert = f"""
            INSERT INTO QUESTION VALUES(
            '{questionid}',
            '{paperid}',
            {questionobj.number},
            '{questionobj.contents}',
            {totalmarks}
            )
            """
            sqlsocket.addToDatabase(questioninsert)
            for topic in questionobj.topics:
                topicquery = f"""
                INSERT INTO QUESTIONTOPIC VALUES(
                '{questionid + topic}',
                '{questionid}',
                '{topic}'
                )
                """
                sqlsocket.addToDatabase(topicquery)
            for part in questionobj.parts:
                if part.marks == 0:
                    continue

                partid = questionid + part.section
                partinsert = f"""
                INSERT INTO PARTS VALUES(
                '{partid}',
                '{questionid}',
                '{part.section}',
                '{part.contents.strip()}',
                {part.marks}
                )
                """
                sqlsocket.addToDatabase(partinsert)


if __name__ == "__main__":
    main()
    print("done")
