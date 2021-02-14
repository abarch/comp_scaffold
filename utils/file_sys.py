import os


def crawler(base_path, execute):
    """
    Description: This recursive function traverses over all the directories and files of the given directory "base_path" and runs
    the method or function provided in "execute" everytime a file is encountered. This function is recursive in nature
    so keep in mind that all the lines of the function will run everytime. This can be a problem when initialisation
    needs to be done only once through the course of the function's run.

    Inputs: base_path - Valid path for a directory that has to be traversed completely atleast once.
                        type:<string> example:'C:/ProgramData'
            execute -   Valid method that would be called everytime a file is encountered. It needs to take the
                        'base_path' as the input.
                        type:<object>(<input>) example:print(base_path)

    Output: None

    Note: This is an example of observer pattern as found in design patterns in good coding practices.
    """

    if os.path.exists(base_path):
        if os.path.isdir(base_path):
            ls = os.listdir(base_path)
            for file in ls:
                crawler(base_path+'/'+file,execute)
        else:
            try:
                execute(base_path)
            except AttributeError:
                print("No such function or method was found.")
            return
    else:
        raise FileNotFoundError('No such file or directory exists.')


if __name__ == "__main__":
    daWay = "D:/Projects/midi/data"

    def outp(path):
        print(path)

    crawler(daWay,outp)