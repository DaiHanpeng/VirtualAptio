import os

class AptioTestMap():
    '''

    '''
    def __init__(self):
        self.test_map = {}

    def build_test_map_from_ini_file(self,ini_file_path):
        if os.path.exists(ini_file_path):
            try:
                ini_file_handler = open(ini_file_path)
                ini_file_contents = ini_file_handler.readlines()

                for line in ini_file_contents[1:-1]:
                    test_info_list = line.split()
                    #print ' '.join(test_info_list[1:])
                    if len(test_info_list) > 1:
                        self.test_map[test_info_list[0]] = ' '.join(test_info_list[1:])
            except Exception as e:
                print e
            finally:
                ini_file_handler.close()

    def is_test_enabled_in_instrument(self,test,instrument):
        if isinstance(self.test_map[test],str):
            if self.test_map[test].find(instrument) <> -1:
                return True
        return False

    def __str__(self):
        return 'test map info:'+'\n'.join(str(item)+":\t"+self.test_map[item] for item in self.test_map)

if __name__ == '__main__':
    ini_path = r'D:\01_Automation\20_Experiential_Conclusions_2015\53_Zhongshan_Aptio\01_Aptio\Config\Dream\Test-Maps.ini'
    test_map = AptioTestMap()
    test_map.build_test_map_from_ini_file(ini_path)
    print test_map
    print test_map.is_test_enabled_in_instrument('ASTm','09')
    print test_map.is_test_enabled_in_instrument('ASTm','10')