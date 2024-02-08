import hpsrc.data_processing.parse as parse
import hpsrc.data_processing.checkpointOne as checkpointOne
import hpsrc.data_processing.json2vec as json2vec
import hpsrc.data_processing.RadicalCollector as RadicalCollector
import sys

def run(argv):
    choice = input('Divide docx by radical...(Y/N):')
    if choice == 'Y' or choice == 'y':
        if RadicalCollector.run() == 1:
            print('Divide docx by radical completed.')
            print('Please check the data folder for the docx files.')
        else:
            print('Divide docx by radical failed.')
    choice = input('Start parsing...(Y/N):')
    if choice == 'Y' or choice == 'y':
        parse.recursion_count = 0
        if parse.run(argv) == 1:
            print('Parsing completed.')
            print('Please check the checkpoint folder for the loop_synonym.txt')
            print('Please check the parsed_json folder for the parsed json files.')
        else:
            print('Parsing failed.')
    else:
        print('Parsing aborted.')
    choice = input('Start checkpoint one...(Y/N):')
    if choice == 'Y' or choice == 'y':
        if checkpointOne.run() == 1:
            print('Checkpoint one completed.')
            print('Please check the checkpoint folder for the characterOnlyEntry.txt')
    else:
        print('Checkpoint one aborted.')
    choice = input('Start json2vec...(Y/N):')
    if choice == 'Y' or choice == 'y':
        if json2vec.run() == 1:
            print('Json2vec completed.')
            print('Please check the vec folder for the csv files.')
    else:
        print('Json2vec aborted.')

    print('All done.')

if __name__ == '__main__':
    run(sys.argv)
