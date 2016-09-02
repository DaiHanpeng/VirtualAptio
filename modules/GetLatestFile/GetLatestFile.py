import os


class GetLatestFile():
    """
    get latest modified file within specific folder.
    """
    #def __init__(self):
    #    pass

    @staticmethod
    def get_latest_file(path_to_folder,part_of_file_name='',file_extension=''):
        '''
        :param path_to_folder:
        :param part_of_file_name:
        :param file_extension
        :return: name of latest modified file in <path_to_folder> and
                 file name contains <part_of_file_name> and end with <file_extension>
        '''
        folder_file_list = os.listdir(path_to_folder)
        filted_file_list = []
        if part_of_file_name <> '' or file_extension <> '':
            for file_name in folder_file_list:
                if -1 <> file_name.find(part_of_file_name) and file_name.endswith(file_extension):
                    filted_file_list.append(os.path.join(path_to_folder,file_name))
        else:
            for item in folder_file_list:
                filted_file_list.append(os.path.join(path_to_folder,item))

        max_file_modified_time = 0
        latest_modified_file = ''
        for f in filted_file_list:
            if os.path.getmtime(f) > max_file_modified_time:
                latest_modified_file = f
                max_file_modified_time = os.path.getmtime(f)

        return latest_modified_file


def test():
    #print GetLatestFile.get_latest_file('.')
    path_to_log_folder = r'D:\01_Automation\23_Experiential_Conclusions_2016\05_DaAn\A002\DATA'
    print GetLatestFile.get_latest_file(path_to_log_folder,'','.MTD')
    #print GetLatestFile.get_latest_file(path_to_log_folder)

if __name__ == '__main__':
    test()